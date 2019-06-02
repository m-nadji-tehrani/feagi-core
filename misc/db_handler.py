import sys
sys.path.append('/Users/mntehrani/PycharmProjects/Metis/venv/lib/python3.7/site-packages/')
from pymongo import MongoClient, DESCENDING, ASCENDING
from influxdb import InfluxDBClient
from configuration import runtime_data
import random


class MongoManagement:
    def __init__(self):
        # print("*** Conncting to database ***")
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['metis']
        self.collection_genome = self.db['genomes']
        self.collection_mnist = self.db['mnist']
        self.collection_test_stats = self.db['test_stats']
        self.collection_membrane_potentials = self.db['membrane_potentials']
        self.collection_neuron_activities = self.db['neuron_activities']
        # print(">> Connected successfully to database.")

    def insert_test_stats(self, stats_data):
        self.collection_test_stats.insert_one(stats_data)

    def inset_membrane_potentials(self, membrane_potential_data):
        self.collection_membrane_potentials.insert_one(membrane_potential_data)

    def insert_neuron_activity(self, fcl_data):
        self.collection_neuron_activities.insert_one(fcl_data)

    def insert_genome(self, genome_data):
        self.collection_genome.insert_one(genome_data)

    def insert_mnist_entry(self, mnist_data):
        self.collection_mnist.insert_one(mnist_data)


    # def read_genome(self, genome_id):
    #
    #     return genome

    def latest_genome(self):
        db_output = self.collection_mnist.find({}).sort("generation_date", DESCENDING).limit(1)
        return db_output[0]

    def mnist_(self, seq):
        pipeline = [
            {"$match": {"mnist_seq": seq}}
        ]
        mnist_seq_data = self.collection_mnist.aggregate(pipeline=pipeline)
        return mnist_seq_data

    def mnist_seq(self, mnist_type, seq):
        if mnist_type not in ['training', 'test']:
            print("ERROR: Invalid MNIST type!")
        else:
            mnist_seq_data = self.collection_mnist.find({"mnist_type": mnist_type, "mnist_seq": seq})
            return mnist_seq_data[0]

    def highest_fitness_genome(self):
        db_output = self.collection_genome.find({}).sort("fitness", DESCENDING).limit(1)
        return db_output[0]

    def genome_count(self):
        return self.collection_genome.count()

    def random_genome(self, n):
        pipeline = [
            {"$sample": {"size": n}}
        ]
        genome_list = self.collection_genome.aggregate(pipeline=pipeline)
        return genome_list

    def random_fit_genome(self, fitness_level):
        pipeline = [
            {"$match": {"fitness": {"$gt": fitness_level}}}
        ]
        genomes = self.collection_genome.aggregate(pipeline=pipeline)

        # Return a random genome from the list of fit genomes
        list_count = 0
        genome_list = []
        for item in genomes:
            list_count += 1
            genome_list.append(item)
        genome = genome_list[random.randrange(0, list_count, 1)]
        return genome

    def top_n_genome(self, n):
        # Assumption: Fitness array function is returning the list sorted with highest fit on top
        genome_list = self.fitness_array()
        genome_count = len(genome_list)
        python_list = []

        for i in range(min(n, genome_count)):
            python_list.append(genome_list[i])
        return python_list

    def random_m_from_top_n(self, selection_count, top_count):
        top_list = self.top_n_genome(top_count)
        python_list = []
        for _ in range(selection_count):
            python_list.append(top_list[random.randrange(0, len(top_list), 1)])
        return python_list

    def genome_id_2_properties(self, genome_id):
        genome = self.collection_genome.find_one({"genome_id": genome_id})
        return genome

    def fcl_data(self, genome_id):
        fcl_data = self.collection_neuron_activities.find({"genome_id": genome_id})
        return fcl_data

    def fitness_array(self):
        pipeline = [
            {"$match": {"fitness": {"$exists": True, "$ne": 0},
                        "genome_id": {"$exists": True, "$nin": [""]}}},
            {"$project": {"genome_id": 1, "fitness": 1}},
            {"$sort": {"fitness": -1}}
        ]
        fitness_list = self.genome_aggregate_function(pipeline)
        # results = self.collection_genome.aggregate(pipeline=pipeline)
        # fitness_list = []
        # for item in results:
        #     fitness_list.append(item)
        #     print(item)
        return fitness_list

    def genome_aggregate_function(self, pipeline):
        results = self.collection_genome.aggregate(pipeline=pipeline)
        python_list = self.mongo_2_list(results)
        return python_list

    def mongo_2_list(self, mongo_obj):
        python_list = []
        for item in mongo_obj:
            python_list.append(item)
        return python_list

    def id_list_2_genome_list(self, id_list):
        genome_list = []
        for _ in id_list:
            genome_list.append(self.genome_id_2_properties(_["genome_id"]))
        return genome_list


class InfluxManagement:
    def __init__(self):
        self.client = InfluxDBClient(host='localhost', port=8086)
        self.stats_database = runtime_data.parameters["InitData"]["influxdb_stat_db"]
        self.evolutionary_database = runtime_data.parameters["InitData"]["influxdb_evolutionary_db"]

        if not runtime_data.parameters["Switches"]["influx_keep_stats"]:
            self.client.drop_database(self.stats_database)

        def db_existence_check(db_name):
            """Checks the existence of a database and creates it if it doesnt exist."""
            self.db_list = self.client.get_list_database()
            if db_name not in [db['name'] for db in self.db_list]:
                print("Creating database named ", db_name)
                self.client.create_database(db_name)
            else:
                print("Database was in there somewhere ;-)")

        db_existence_check(self.stats_database)
        db_existence_check(self.evolutionary_database)

    def get_db_list(self):
        print(self.client.get_list_database())

    def insert_neuron_activity(self, connectome_path, cortical_area, neuron_id, membrane_potential):
        raw_data = [
            {
                "measurement": "membranePotential",
                "tags": {
                    "connectome": connectome_path,
                    "cortical_area": cortical_area,
                    "neuron": neuron_id
                },
                "fields": {
                    "membrane_potential": membrane_potential
                }
            }
        ]
        self.client.switch_database(self.stats_database)
        self.client.write_points(raw_data)

    def insert_burst_activity(self, connectome_path, burst_id, cortical_area, neuron_count):
        raw_data = [
            {
                "measurement": "burstStats",
                "tags": {
                    "connectome": connectome_path,
                    "cortical_area": cortical_area,
                },
                "fields": {
                    "burst_id": burst_id,
                    "neuron_count": neuron_count
                }
            }
        ]
        self.client.switch_database(self.stats_database)
        self.client.write_points(raw_data)

    def insert_burst_checkpoints(self, connectome_path, burst_id):
        raw_data = [
            {
                "measurement": "burstCheckpoints",
                "tags": {
                    "connectome": connectome_path
                },
                "fields": {
                    "burst_id": 1
                }
            }
        ]
        self.client.switch_database(self.stats_database)
        self.client.write_points(raw_data)

    def insert_connectome_stats(self, connectome_path, cortical_area, neuron_count, synapse_count):
        raw_data = [
            {
                "measurement": "connectomeStats",
                "tags": {
                    "connectome": connectome_path,
                    "cortical_area": cortical_area,
                },
                "fields": {
                    "neuron_count": neuron_count,
                    "synapse_count": synapse_count
                }
            }
        ]
        self.client.switch_database(self.stats_database)
        self.client.write_points(raw_data)

    def insert_inter_cortical_stats(self, connectome_path, cortical_area_src, cortical_area_dst, synapse_count):
        raw_data = [
            {
                "measurement": "interCorticalStats",
                "tags": {
                    "connectome": connectome_path,
                    "Source_cortical_area": cortical_area_src,
                    "Destination_cortical_area": cortical_area_dst
                },
                "fields": {
                    "synapse_count": synapse_count
                }
            }
        ]
        self.client.switch_database(self.stats_database)
        self.client.write_points(raw_data)

    def insert_evolutionary_fitness_stats(self, connectome_path, fitness_score):
        raw_data = [
            {
                "measurement": "fitness",
                "tags": {
                    "connectome": connectome_path
                },
                "fields": {
                    "brain_fitness": fitness_score
                }
            }
        ]
        self.client.switch_database(self.evolutionary_database)
        self.client.write_points(raw_data)

    def insert_evolutionary_connectome_stats(self, connectome_path, cortical_area, neuron_count, synapse_count):
        raw_data = [
            {
                "measurement": "evolutionaryConnectomeStats",
                "tags": {
                    "connectome": connectome_path,
                    "cortical_area": cortical_area,
                },
                "fields": {
                    "neuron_count": neuron_count,
                    "synapse_count": synapse_count
                }
            }
        ]
        self.client.switch_database(self.evolutionary_database)
        self.client.write_points(raw_data)
        print(">>>>>--------->>>>--------->>> Evolutionary stats logged in influx")

    def drop_neuron_activity(self):
        self.client.drop_database(self.stats_database)


if __name__ == "__main__":

    # from PUs import IPU_vision
    # from misc import disk_ops
    # disk_ops.load_parameters_in_memory()
    # from configuration import runtime_data
    # disk_ops.genome_handler("/Users/mntehrani/PycharmProjects/Metis/connectome/")

    # mnist = IPU_vision.MNIST()

    mongo = MongoManagement()

    results = mongo.mnist_seq(mnist_type='training', seq=5)

    print(results)





    # print(mnist.read_image(1))








    # #
    # for _ in mongo.fitness_array():
    #     print(_)
    # #
    # print(mongo.highest_fitness_genome())
    # print(type(latest_genome))
    # print(latest_genome["properties"])
    # for _ in latest_genome:
    #     print(_)
    #
    # random_genome = mongo.random_genome(1)

    # for _ in mongo.fcl_data('2018-07-28_11:16:12_938349_ZDW0VQ_G'):
    #     print(">>>", _)

    # print(mongo.random_genome())

    # print(">", mongo.top_n_genome(2))

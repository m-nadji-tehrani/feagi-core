from pymongo import MongoClient, DESCENDING, ASCENDING
import random
import pymongo


class MongoManagement:
    def __init__(self):
        # print("*** Conncting to database ***")
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['metis']
        self.collection_genome = self.db['genomes']
        self.collection_test_stats = self.db['test_stats']
        # print(">> Connected successfully to database.")

    def insert_test_stats(self, stats_data):
        self.collection_test_stats.insert_one(stats_data)

    def insert_genome(self, genome_data):
        self.collection_genome.insert_one(genome_data)

    # def read_genome(self, genome_id):
    #
    #     return genome

    def latest_genome(self):
        db_output = self.collection_genome.find({}).sort("generation_date", DESCENDING).limit(1)
        return db_output[0]

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


if __name__ == "__main__":

    mongo = MongoManagement()

    genome_data = {
         "generation_date": "2018-06-24 00:28:49_410237",
         "properties": {
              "firing_patterns": {
                 "A": {
                    "frequency": "100",
                    "magnitude": "80"
                 },
                 "B": {
                    "frequency": "20",
                    "magnitude": "100"
                 }
              },
              "neighbor_locator_rule": {
                 "rule_0": {
                    "param_1": 1,
                    "param_2": 0
                 },
                 "rule_1": {
                    "param_1": 2,
                    "param_2": 1
                 },
                 "rule_2": {
                    "param_1": 5,
                    "param_2": 5,
                    "param_3": 10
                 },
                 "rule_3": {
                    "param_1": 0,
                    "param_2": 0
                 },
                 "rule_4": {
                    "param_1": 25,
                    "param_2": 100
                 },
                 "rule_5": {
                    "param_1": 700,
                    "param_2": 700,
                    "param_3": 700,
                    "param_4": 700,
                    "param_5": 700,
                    "param_6": 700,
                    "param_7": 700
                 },
                 "rule_6": {
                    "param_1": 0,
                    "param_2": 0
                 }
              },
              "IPU_vision_filters": {
                 "3": {
                    "-": [
                       [
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "|": [
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ]
                    ],
                    " ": [
                       [
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0
                       ]
                    ],
                    "o": [
                       [
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          4,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "/": [
                       [
                          -1,
                          -1,
                          1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          1,
                          -1,
                          -1
                       ]
                    ],
                    "\\": [
                       [
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1
                       ]
                    ]
                 },
                 "5": {
                    "-": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          1,
                          1,
                          1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    " ": [
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ]
                    ],
                    "|": [
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ]
                    ],
                    "o": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "/": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "\\": [
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ]
                    ]
                 },
                 "7": {
                    "-": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          1,
                          1,
                          1,
                          1,
                          1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    " ": [
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ]
                    ],
                    "I": [
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "i": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "o": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "/": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "\\": [
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ]
                    ]
                 }
              },
              "location_tolerance": 2,
              "image_color_intensity_tolerance": 250,
              "max_burst_count": 3,
              "evolution_burst_count": 100,
              "performance_stats": {
                 "mnist_view_cnt": 0,
                 "mnist_correct_detection_cnt": 0
              },
              "blueprint": {
                 "vision_v1-1": {
                    "growth_path": "",
                    "direction_sensitivity": "/",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 1,
                    "layer_index": 1,
                    "total_layer_count": 7,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_1"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             5
                          ]
                       }
                    }
                 },
                 "vision_v1-2": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 4,
                    "layer_index": 2,
                    "total_layer_count": 7,
                    "direction_sensitivity": "\\",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 750,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             5
                          ]
                       }
                    }
                 },
                 "vision_v1-3": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 7,
                    "layer_index": 3,
                    "total_layer_count": 7,
                    "direction_sensitivity": "|",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 501,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_3"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-4": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 10,
                    "layer_index": 4,
                    "total_layer_count": 7,
                    "direction_sensitivity": "-",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_4"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-5": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 13,
                    "layer_index": 5,
                    "total_layer_count": 7,
                    "direction_sensitivity": "I",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_5"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-6": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 16,
                    "layer_index": 6,
                    "total_layer_count": 7,
                    "direction_sensitivity": "o",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_6"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-7": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 19,
                    "layer_index": 7,
                    "total_layer_count": 7,
                    "direction_sensitivity": " ",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_7"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v2": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v2",
                    "plot_index": 2,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 1000,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 0.5,
                    "postsynaptic_current_max": 2,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_2",
                    "cortical_mapping_dst": {
                       "vision_IT": {
                          "neighbor_locator_rule_id": "rule_6",
                          "neighbor_locator_rule_param_id": "param_1"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "orientation_selectivity_id": "",
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             500
                          ],
                          "y": [
                             0,
                             500
                          ],
                          "z": [
                             0,
                             200
                          ]
                       }
                    }
                 },
                 "vision_IT": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_IT",
                    "plot_index": 3,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 1000,
                    "location_generation_type": "random",
                    "synapse_attractivity": 80,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 0.5,
                    "postsynaptic_current_max": 2,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_2",
                    "cortical_mapping_dst": {
                       "vision_memory": {
                          "neighbor_locator_rule_id": "rule_4",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 0.5,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             500
                          ],
                          "y": [
                             0,
                             500
                          ],
                          "z": [
                             0,
                             250
                          ]
                       }
                    }
                 },
                 "vision_memory": {
                    "growth_path": "",
                    "group_id": "Memory",
                    "sub_group_id": "vision",
                    "plot_index": 1,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 2000,
                    "location_generation_type": "random",
                    "synapse_attractivity": 10,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 0.5,
                    "plasticity_constant": 0.12,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {},
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 2,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 2,
                       "snooze_length": 4,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             300
                          ],
                          "y": [
                             0,
                             300
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 },
                 "utf8": {
                    "growth_path": "",
                    "group_id": "IPU",
                    "sub_group_id": "IPU_utf8",
                    "plot_index": 1,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 300,
                    "location_generation_type": "sequential",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 1.1,
                    "plasticity_constant": 0.05,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "utf8_memory": {
                          "neighbor_locator_rule_id": "rule_3",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             1
                          ],
                          "y": [
                             0,
                             1
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 },
                 "utf8_memory": {
                    "growth_path": "",
                    "group_id": "Memory",
                    "sub_group_id": "utf8",
                    "plot_index": 2,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 300,
                    "location_generation_type": "sequential",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 2,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "utf8_out": {
                          "neighbor_locator_rule_id": "rule_3",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 20,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 10,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             1
                          ],
                          "y": [
                             0,
                             1
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 },
                 "utf8_out": {
                    "growth_path": "",
                    "group_id": "OPU",
                    "sub_group_id": "OPU_utf8",
                    "plot_index": 1,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 300,
                    "location_generation_type": "sequential",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 0.51,
                    "plasticity_constant": 0.05,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {},
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 20,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 1,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             1
                          ],
                          "y": [
                             0,
                             1
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 }
              }
           },
         }

    # print(type(genome_data))

    # Mongo.insert_genome(genome_data=genome_data)
    #
    for _ in mongo.fitness_array():
        print(_)
    #
    # print(mongo.highest_fitness_genome())
    # print(type(latest_genome))
    # print(latest_genome["properties"])
    # for _ in latest_genome:
    #     print(_)
    #
    # random_genome = mongo.random_genome(1)
    for _ in mongo.id_list_2_genome_list(mongo.random_m_from_top_n(2, 5)):
        print(">> ", _)

    print(">>>", mongo.highest_fitness_genome())

    # print(mongo.random_genome())

    # print(">", mongo.top_n_genome(2))

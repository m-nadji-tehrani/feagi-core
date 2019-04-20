
from influxdb import InfluxDBClient


class InfluxManagement:
    def __init__(self):
        self.client = InfluxDBClient(host='localhost', port=8086)
        self.database = 'feagi3'
        # self.client.drop_database('feagi3')
        self.db_list = self.client.get_list_database()
        if self.database not in [db['name'] for db in self.db_list]:
            print("Creating database named ", self.database)
            self.client.create_database(self.database)
            self.client.switch_database(self.database)
        else:
            print("Database was in there somewhere ;-)")
            self.client.switch_database(self.database)

    def get_db_list(self):
        print(self.client.get_list_database())

    def log_neuron_activity(self, connectome_path, cortical_area, neuron_id, membrane_potential):
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
        self.client.write_points(raw_data)


if __name__ == "__main__":
    influxdb = InfluxManagement()
    influxdb.log_neuron_activity(connectome_path="connectome_3", cortical_area="vision_memory", neuron_id="AAB", membrane_potential=7)
    db_data = list(influxdb.client.query('select * from membranePotential'))

    for _ in db_data[0]:
        print(_)

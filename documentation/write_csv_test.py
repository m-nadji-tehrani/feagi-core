import csv

with open('write_csv_test.csv', 'a') as test_file:
    neuron_mp_writer = csv.writer(test_file, delimiter=',')
    new_data = [(1, 3, 4), (6, 5, 4)]
    neuron_mp_writer.writerows(new_data)

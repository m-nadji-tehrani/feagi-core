

import random

a = {
          "growth_path" : "",
          "direction_sensitivity" : "/",
          "group_id" : "vision",
          "sub_group_id" : "vision_v1",
          "plot_index" : 1,
          "layer_index" : 1,
          "total_layer_count" : 7,
          "orientation_selectivity_pattern" : "",
          "location" : "",
          "kernel_size" : 5,
          "cortical_neuron_count" : 1597,
          "location_generation_type" : "random",
          "synapse_attractivity" : 100,
          "init_synapse_needed" : False,
          "postsynaptic_current" : 20,
          "plasticity_constant" : 0,
          "postsynaptic_current_max" : 1000,
          "neighbor_locator_rule_id" : "rule_1",
          "neighbor_locator_rule_param_id" : "param_1",
          "cortical_mapping_dst" : {
              "vision_v2" : {
                  "neighbor_locator_rule_id" : "rule_5",
                  "neighbor_locator_rule_param_id" : "param_1"
              }
          },
          "neuron_params" : {
              "activation_function_id" : "",
              "depolarization_threshold" : 1.633575495825,
              "orientation_selectivity_id" : "",
              "firing_threshold" : 2.89235403072,
              "firing_pattern_id" : "",
              "refractory_period" : 0,
              "axon_avg_length" : "",
              "leak_coefficient" : 10,
              "axon_avg_connections" : "",
              "axon_orientation function" : "",
              "consecutive_fire_cnt_max" : 0,
              "snooze_length" : 1.659231437448,
              "block_boundaries" : [
                  28,
                  28,
                  1
              ],
              "geometric_boundaries" : {
                  "x" : [
                      0,
                      32
                  ],
                  "y" : [
                      0,
                      32
                  ],
                  "z" : [
                      0,
                      10
                  ]
              }
          }
      }


def pick_a_key(dictionary):
    return random.choice(list(dictionary))


for _ in range(20):

    chosen_key = pick_a_key(a)
    print("..", chosen_key)
    path =
    while type(a[chosen_key]) == dict:
        print(">", chosen_key)
        chosen_key = pick_a_key(a[chosen_key])
        print(">", chosen_key)

    print(">>>", chosen_key)

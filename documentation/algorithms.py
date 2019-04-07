"""
- Neuron growth
- Brain generation
- Learning
- Memory
- Auto training
- Auto testing numbers
    1.
- Gene improvement
-
    1. Generate the brain based on a given Genome
    2. Run auto training for x rounds
        1. Assess the performance
        2.
    3. Make gene changes
    4. back to step 1
- Burst Management
"""


# Burst engine
while burst_engine_flag == true:
    for neuron in fire_candidate_list:
        fire_neuron(neuron)

    if in_training_mode:
        inject_training_data()

    if in_test_mode:
        inject_test_data()

    cortical_activity = measure_cortical_activity()
    if cortical_activity < activity_threshold:
        terminate_brain_instance()

    form_memories()

save_brain_instance_stats_in_database()



# Neuron firing
for every_synapse in firing_neuron_synapse_list:
    update_destination_membrane_potentials()
    if destination_membrane_potential > firing_threshold:
        add_destination_neuron_to_fire_candidate_list()

update_counters_associated_with_firing_neuron()

if consequtive_fire_counter > consequtive_fire_counter_threshold:
    set_snooz_flag_for_firing_neuron()

remove_firing_neuron_from_fire_candidate_list()



# Updating neuron's membrane potential
leak_value = calculate_neuron_potential_leakage_since_last_update()
membrane_potential = old_potential - leak_value + incoming_potential



# Plasticity

# Training

# Testing

# Refractory period
if

# Snooze


"""
This file contains all the Global settings and parameters used throughout the project
"""


# class Timers:
#     # Sleep timer for visualization delay
#     burst_timer = 1e-17
#     idle_burst_timer = 2
#     auto_train_delay = 3
#     auto_train_delay2 = 50
#     auto_test_delay = 3
#     block_size = 10


class Bcolors:
    UPDATE = '\033[94m'
    BURST = '\033[93m'
    FIRE = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'


# class Input:
#     # Variable containing user input to train and control the Brain
#     user_input = ''
#     previous_user_input = ''
#     user_input_param = ''
#     previous_user_input_param = ''
#     opu_char = 'X'
#     comprehended_char = ''


# class Switches:
#     # Flag to enable Verbose mode
#     verbose = False
#     # Flag to show visualizations
#     vis_show = False
#     if vis_show:
#         universal_functions.init_burst_visualization()
#     vis_init_status = False
#     auto_train = True
#     auto_test_comp_attempt_threshold = 3
#     ready_to_exit_burst = False
    # >>>>>>>>>>>>   Items below here should not be needed anymore in Settings file    <<<<<<<<<<<<<<<
    # # todo: Move this to the Genome
    # # A location tolerance factor for Neuron location approximation
    # global image_color_intensity_tolerance
    # image_color_intensity_tolerance = 250
    # global sobel_x, sobel_y
    # sobel_x = [[-1, 0, 1], [-2, 0, 1], [-1, 0, 1]]
    # sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]


# class InitData:
#     # # Flag to read all Connectome data from memory instead of File
#     # read_data_from_memory = True
#     # regenerate_brain = True
#     # # connectome_path defines the folder where all connectome files reside
#     # connectome_path = './connectome/'
#     # # rules_path defines the folder where all connectome files reside
#     # rules_path = './reproduction/rules.json'
#     # # Genome defines the json file name and location which is acting as Human Genome
#     # genome_file = './reproduction/genome.json'
#     genome_metadata = universal_functions.load_genome_metadata_in_memory()
#     genome = universal_functions.load_genome_in_memory()
#     genome_id = ""
#     genome_stats = {"test_stats": {}, "performance_stats": {}}
#     brain = universal_functions.load_brain_in_memory()
#     blueprint = universal_functions.cortical_list()
#     event_id = '_'
#     cortical_areas = universal_functions.cortical_list()
#     rules = universal_functions.load_rules_in_memory()
#     # global max_xyz_range
#     # max_xyz_range = cortical_xyz_range()



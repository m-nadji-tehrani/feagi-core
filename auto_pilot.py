import random
import mnist
from datetime import datetime
from time import sleep
import multiprocessing as mp
import brain_functions
import universal_functions
if universal_functions.parameters["Switches"]["vis_show"]:
    import visualizer


def training_num_gen(num):
    rand_num = random.randrange(10, 500, 1)
    mnist_data = mnist.read_image(rand_num)
    while int(num) != mnist_data[1]:
        rand_num = random.randrange(10, 500, 1)
        mnist_data = mnist.read_image(random.randrange(10, 500, 1))
    return rand_num, mnist_data


def auto_train(FCL_queue, event_queue):
    b = brain_functions.Brain()
    training_start_time = datetime.now()
    print("---------------------------------------------------------------------Auto training has been initiated.")
    for number in range(10):
        mnist_num, mnist_img = training_num_gen(number)
        if universal_functions.parameters["Switches"]["vis_show"]:
            visualizer.cortical_heatmap(mnist.read_image(mnist_num), [])
        # Following for loop help to train for a single number n number of times
        for x in range(int(universal_functions.parameters["Input"]["user_input_param"])):
            print(">>  >>  >>  >>  >>  >>  >>  >>  >>  Training round %i for number %s" % (x + 1, mnist_img[1]))
            mnist_img_char = str(mnist_img[1])
            process_5 = mp.Process(name='Seeing_MNIST_image',
                                   target=b.see_from_mnist,
                                   args=(mnist_img, FCL_queue, event_queue))
            process_6 = mp.Process(name='Reading input char',
                                   target=b.read_char,
                                   args=(str(mnist_img_char), FCL_queue))
            process_5.start()
            sleep(universal_functions.parameters["Timers"]["auto_train_delay"])
            process_6.start()
            # process_5.join()
            # process_6.join()

        # Placing training on hold till neuronal activities for previous training set is ramped down
        fcl = FCL_queue.get()
        fcl_length = len(fcl)
        FCL_queue.put(fcl)
        while fcl_length > 0:
            sleep(5)
            fcl = FCL_queue.get()
            fcl_length = len(fcl)
            FCL_queue.put(fcl)

    training_duration = datetime.now() - training_start_time
    print("---------------------------------------------------------------------Auto training has been completed.")
    print("Training lasted %s " % training_duration)
    print("--------------------------------------------------------------")
    universal_functions.parameters["Input"]["user_input"] = 'x'
    return


def auto_test(FCL_queue, event_queue):
    """
    Test approach:

    - Ask user for number of times testing every digit call it x
    - Inject each number x rounds with each round conclusion being a "Comprehensions"
    - Count the number of True vs. False Comprehensions
    - Collect stats for each number and report at the end of testing

    """

    print('Testing Testing Testing', universal_functions.parameters["Input"]["comprehended_char"])
    b = brain_functions.Brain()
    testing_start_time = datetime.now()
    print("---------------------------------------------------------------------Auto testing has been initiated.")

    test_stats = list()

    for number in range(10):
        mnist_num, mnist_img = training_num_gen(number)
        if universal_functions.parameters["Switches"]["vis_show"]:
            visualizer.cortical_heatmap(mnist.read_image(mnist_num), [])

        # Following For loop test brain comprehension of a character x number of times
        true_comprehensions = 0
        total_comprehensions = 0
        for x in range(int(universal_functions.parameters["Input"]["user_input_param"])):
            print(">>  >>  >>  >>  >>  >>  >>  >>  >>  Testing round %i out of %i for number %s"
                  % (x + 1, int(universal_functions.parameters["Input"]["user_input_param"]), mnist_img[1]))
            mnist_img_char = str(mnist_img[1])

            # Periodically check to see what Character was comprehended and evaluate True or False
            comprehension = False
            comprehension_attempts = 0
            while not comprehension:
                # The following process starts reading from MNIST and injecting it into the brain
                process_7 = mp.Process(name='Seeing_MNIST_image', target=b.see_from_mnist,
                                       args=(mnist_img, FCL_queue, event_queue))
                process_7.start()
                comprehension_attempts += 1
                print("This is comprehension attempt # %i" % comprehension_attempts)
                if comprehension_attempts >= \
                        universal_functions.parameters["Switches"]["auto_test_comp_attempt_threshold"]:
                    print("Comprehension attempt threshold for this round has been exceeded!!")
                    break
                # Read the flag to see if there has been comprehension
                comprehended_value = universal_functions.parameters["Input"]["comprehended_char"]
                print("++++++++   ++++  ++  + The value for comprehended_char is currently: ", comprehended_value)
                if comprehended_value:
                    print("$$$$$$      Current comprehended value is:", comprehended_value)
                    total_comprehensions += 1
                    if comprehended_value == mnist_img_char:
                        true_comprehensions += 1
                    universal_functions.parameters["Input"]["comprehended_char"] = ''
                print("So far there were %i correct comprehension out of total of %i"
                      % (true_comprehensions, total_comprehensions))

                sleep(universal_functions.parameters["Timers"]["auto_test_delay"])
                # process_5.join()
                # process_6.join()

        test_stats.append([number, total_comprehensions, true_comprehensions])

        # Placing training on hold till neuronal activities for previous training set is ramped down
        fcl = FCL_queue.get()
        fcl_length = len(fcl)
        FCL_queue.put(fcl)
        while fcl_length > 0:
            sleep(5)
            fcl = FCL_queue.get()
            fcl_length = len(fcl)
            FCL_queue.put(fcl)

    testing_duration = datetime.now() - testing_start_time
    print("---------------------------------------------------------------------Auto testing has been completed.")
    print("Testing lasted %s " % testing_duration)
    print("--------------------------------------------------------------")
    print("Test Stats")
    print(test_stats)
    print("--------------------------------------------------------------")

    # logging stats into Genome
    universal_functions.genome_stats["test_stats"] = test_stats

    universal_functions.parameters["Input"]["user_input"] = 'x'
    return

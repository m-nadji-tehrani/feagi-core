

import multiprocessing as mp
from misc import stats
import sys
from tty import setraw
import termios
sys.path.append('/Users/mntehrani/PycharmProjects/Metis/venv/lib/python3.7/site-packages/')
import numpy as np
from configuration import settings
from PUs import IPU_vision
from configuration import runtime_data
from datetime import datetime


class Brain:
    @staticmethod
    def print_basic_info():
        cp = mp.current_process()
        print("\rstarting", cp.name, cp.pid)
        print("\rConnectome database =                  %s" %
              runtime_data.parameters["InitData"]["connectome_path"])
        print("\rTotal neuron count in the connectome  %s  is: %i" %
              (runtime_data.parameters["InitData"]["connectome_path"] + 'vision_v1.json',
               stats.connectome_neuron_count(cortical_area='vision_v1')))
        print(' \rexiting', cp.name, cp.pid)
        return

    def retina2(self, num, seq, mnist_type, random_num):
        """
        Input:
        Output: List of neurons from various Vision V1 layers that are activated
        """

        mnist = IPU_vision.MNIST()

        print("Retina has been exposed to a version of :", num)
        neuron_list = {}

        vision_group = self.cortical_sub_group_members('vision_v1')

        # todo: the following is assuming all cortical vision v1 sublayers have the same kernel size (hardcoded value)
        kernel_size = runtime_data.genome['blueprint']['vision_v1-1']['kernel_size']

        kernel = IPU_vision.Kernel()

        polarized_image = mnist.mnist_img_fetcher3(num=num,
                                                   kernel_size=kernel_size,
                                                   seq=seq,
                                                   mnist_type=mnist_type,
                                                   random_num=random_num)

        if runtime_data.parameters['Logs']['print_polarized_img']:
            image = polarized_image['original_image']
            npimage = np.array(image)
            for _ in npimage:
                print(_)

        for cortical_area in vision_group:
            neuron_list[cortical_area] = set()
            cortical_direction_sensitivity = runtime_data.genome['blueprint'][cortical_area][
                'direction_sensitivity']

            for key in polarized_image:
                if key == cortical_direction_sensitivity:
                    try:
                        # print(np.array2string(np.array(polarized_image[cortical_direction_sensitivity]), max_line_width=np.inf))

                        # ipu_vision_array = \
                        #     IPU_vision.Image.convert_direction_matrix_to_coordinates(
                        #         polarized_image[cortical_direction_sensitivity])

                        ipu_vision_array = polarized_image[cortical_direction_sensitivity]

                        # print(">>> IPU vision array:", ipu_vision_array)

                        if runtime_data.parameters['Logs']['print_activation_counters']:
                            print("\n Bipolar cell activation count in %s is  %i" %
                                  (cortical_area, len(ipu_vision_array)))

                        neuron_id_list = IPU_vision.Image.convert_image_locations_to_neuron_ids(ipu_vision_array,
                                                                                                cortical_area)
                        # print("Neuron id list: ", neuron_id_list)

                        if runtime_data.parameters['Logs']['print_activation_counters']:
                            print("Neuron id count activated in layer %s is %i\n\n" %
                                  (cortical_area, len(neuron_id_list)))

                        neuron_list[cortical_area].update(set(neuron_id_list))
                    except:
                        print("Error on direction selectivity")

                # if runtime_data.parameters['Logs']['print_polarized_img']:
                #     print("\nPrinting polarized image for ", cortical_area)
                #     for row in polarized_image[cortical_direction_sensitivity]:
                #         print(" ***")
                #         for item in row:
                #             print(settings.Bcolors.YELLOW + item + settings.Bcolors.ENDC, end='')
                #             if item == '':
                #                 print(settings.Bcolors.RED + '.' + settings.Bcolors.ENDC, end='')

        return neuron_list

    @staticmethod
    def inject_to_fcl(fire_list, fcl_queue):
        # print("Injecting to FCL.../\/\/\/")
        # Update FCL with new input data. FCL is read from the Queue and updated
        flc = fcl_queue.get()
        for item in fire_list:
            flc.append(item)
        fcl_queue.put(flc)
        # print("Injected to FCL.../\/\/\/")
        return

    @staticmethod
    def read_user_input():
        print("Func: read_user_input : start")
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            setraw(sys.stdin.fileno())
            runtime_data.parameters["Input"]["user_input"] = sys.stdin.read(1)
            # sys.stdout.write("\r%s" % user_input_queue)
            print("hahaha______hehehe")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # sys.stdout.flush()
        print("Func: read_user_input : end")
        return

    # def kernel_view(self):
        # IPU_vision.image_read_block(mnist.read_image(image_number), 3, [27, 27])

        # print("Direction matrix with Kernel 3")
        # a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 3))
        # for items in range(0, np.shape(a)[0]):
        #     print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))
        #
        # print("Direction matrix with Kernel 5")
        # a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 5))
        # for items in range(0, np.shape(a)[0]):
        #     print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))
        #
        # print("Direction matrix with Kernel 7")
        # a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 7))
        # for items in range(0, np.shape(a)[0]):
        #     print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))
        #
        #
        # print(IPU_vision.direction_stats(a))
        # return

    @staticmethod
    def cortical_area_neuron_count(cortical_area):
        """
        Returns number of Neurons in the connectome
        """
        data = runtime_data.brain[cortical_area]
        neuron_count = 0
        for key in data:
            neuron_count += 1
        return neuron_count

    @staticmethod
    def cortical_area_synapse_count(cortical_area):
        """
        Returns number of Neurons in the connectome
        """
        data = runtime_data.brain[cortical_area]
        synapse_count = 0
        for neuron in data:
            for _ in data[neuron]['neighbors']:
                synapse_count += 1
        return synapse_count

    @staticmethod
    def cortical_sub_group_members(group):
        members = []
        for item in runtime_data.cortical_list:
            if runtime_data.genome['blueprint'][item]['sub_group_id'] == group:
                members.append(item)
        return members

    def connectome_neuron_count(self):
        total_neuron_count = 0
        for cortical_area in runtime_data.cortical_list:
            total_neuron_count += self.cortical_area_neuron_count(cortical_area)
        return total_neuron_count

    def connectome_synapse_count(self):
        total_synapse_count = 0
        for cortical_area in runtime_data.cortical_list:
            total_synapse_count += self.cortical_area_synapse_count(cortical_area)

        return total_synapse_count

    @staticmethod
    def terminate():
        """To terminate the brain activities without recording the genome in database or recording any stat.
        This function to be used when a brain instance is detected to be dysfunctional."""

        return

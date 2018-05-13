# library to read a character from keyboard and have it converted to neuron firing

from architect import neuron_finder
import universal_functions


def convert_char_to_fire_list(char):
    utf_value = ord(char)
    fire_list = []
    for key in universal_functions.brain["utf8"]:
        if utf_value == universal_functions.brain["utf8"][key]["location"][2]:
            fire_list.append(["utf8", key])
    return fire_list

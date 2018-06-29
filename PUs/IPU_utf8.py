# library to read a character from keyboard and have it converted to neuron firing

from configuration import runtime_data


def convert_char_to_fire_list(char):
    utf_value = ord(char)
    fire_list = []
    for key in runtime_data.brain["utf8"]:
        if utf_value == runtime_data.brain["utf8"][key]["location"][2]:
            fire_list.append(["utf8", key])
    return fire_list

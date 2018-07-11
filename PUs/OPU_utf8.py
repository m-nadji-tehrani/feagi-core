
from configuration import runtime_data

"""
Library of Output Proecssing Unit (OPU) functions responsible for translating neuronal activities into a read world 
event.
"""


def convert_neuron_acticity_to_utf8_char(cortical_area, neuron_id):

    char = int(runtime_data.brain[cortical_area][neuron_id]["location"][2])
    activity_history = runtime_data.brain[cortical_area][neuron_id]['activity_history']
    activity_rank = sum(activity_history) / len(activity_history)
    return chr(char), activity_rank


if __name__ == '__main__':
    import tkinter
    master = tkinter.Tk()

    text = "Comprehended Character is: " + runtime_data.parameters["Input"]["opu_char"]
    tkinter.Label(master, text=text, font=("Helvetica", 24)).grid(row=0)

    # master.update_idletasks()
    # master.update()

    master.mainloop()

from misc import universal_functions

"""
Library of Output Proecssing Unit (OPU) functions responsible for translating neuronal activities into a read world 
event.
"""


def convert_neuron_acticity_to_utf8_char(cortical_area, neuron_id):

    char = int(universal_functions.brain[cortical_area][neuron_id]["location"][2])

    return chr(char)


if __name__ == '__main__':
    import tkinter
    master = tkinter.Tk()

    text = "Comprehended Character is: " + universal_functions.parameters["Input"]["opu_char"]
    tkinter.Label(master, text=text, font=("Helvetica", 24)).grid(row=0)


    # master.update_idletasks()
    # master.update()

    master.mainloop()

# The game should comply with the PEP8 standard

from tkinter import Tk, IntVar, Label, PhotoImage

# All your functions go here
def configure_window():
    window.geometry("600x600")
    window.configure(background="#ffffff")
    window.title("F r o g g y  B u l l e t")

window = Tk()
configure_window()

# All your global stuff goes here
user_answer = IntVar()

current_score = 0
score = Label(window, text="Score: 0", font=("Arial Bold",50), background="#000000")
score.grid(column=2, row=2, columnspan=4, sticky="E")

# Place the images here
# Frog
# Butterfly
# Bug
# Bug1
# Bug2
# Bat

window.mainloop()
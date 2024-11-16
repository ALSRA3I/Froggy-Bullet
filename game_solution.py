# The game should comply with the PEP8 standard

from tkinter import Tk, IntVar, Label, PhotoImage, messagebox, Button

# All your functions go here
def configure_window():
    window.geometry("600x600")
    window.configure(background="#ffffff")
    window.title("F r o g g y  B u l l e t")

def start_game():
    for widget in window.winfo_children():
        widget.destroy()

    # Add a score
    score = IntVar(value=0)
    score_label = Label(window, text="Score: 0", font=("Arial", 16), background="#ffffff")
    score_label.pack(anchor="nw", padx=10, pady=10)

    # Adding the Frogg
    frog = PhotoImage(file="green_frog1.png")
    frog_label = Label(window, image=frog, bg="#ffffff")
    frog_label.image = frog
    frog_label.place(relx=0.5, rely=0.5, anchor="center")

def show_leaderboard():
    messagebox.showinfo("Leaderboard", "Displaying leaderboard...")

def open_settings():
    messagebox.showinfo("Settings", "Opening settings...")

window = Tk()
configure_window()

# All your global stuff goes here
start_button = Button(window, text="Start", command=start_game, font=("Arial", 16))
leaderboard_button = Button(window, text="Leaderboard", command=show_leaderboard, font=("Arial", 16))
settings_button = Button(window, text="Settings", command=open_settings, font=("Arial", 16))

# Position the buttons on the window
start_button.pack(pady=20)
leaderboard_button.pack(pady=10)
settings_button.pack(pady=10)

window.mainloop()
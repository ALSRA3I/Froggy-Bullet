from tkinter import Tk, IntVar, Label, PhotoImage, messagebox, Button
import random


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

    # Add the Frog
    frog = PhotoImage(file="green_frog1.png")
    frog_label = Label(window, image=frog, bg="#ffffff")
    frog_label.image = frog
    frog_label.place(relx=0.5, rely=0.5, anchor="center")

    # Pause and Unpause
    is_paused = False

    def pause_toggle():
        nonlocal is_paused
        is_paused = not is_paused
        pause_button.config(text="Unpause" if is_paused else "Pause")

    pause_button = Button(window, text="Pause", command=pause_toggle, font=("Arial", 14))
    pause_button.pack(pady=10)

    bug = PhotoImage(file="")
    butterfly = PhotoImage(file="")
    bat = PhotoImage(file="")
    enemy_images = [bug, butterfly, bat]

    speeds = {
        'bug': 3,
        'butterfly': 3,
        'bat': 7
    }

    def spawn_enemy(enemy_type):
        if not is_paused:
            if enemy_type == 'bug':
                enemy_img = bug
            elif enemy_type == 'butterfly':
                enemy_img = butterfly
            elif enemy_type == 'bat':
                enemy_img = bat
            
            enemy_label = Label(window, image=enemy_img, background="#ffffff")
            enemy_label.image = enemy_img

            side = random.randint(1,4)
            if side == 1:
                enemy_label.place(x=random.randint(0,600), y =-50)
            elif side == 2:
                enemy_label.place(x=-50, y=random.randint(0,600))
            elif side == 3:
                enemy_label.place(x=650, y=random.randint(0, 600))
            elif side == 4:
                enemy_label.place(x=random.randint(0,600), y=650)

            move_enemy(enemy_label, enemy_type)

        if enemy_type == 'bug':
            window.after(random.randint(1500, 3000), lambda: spawn_enemy('bug'))
        if enemy_type == 'butterfly':
            window.after(random.randint(2500, 4000), lambda: spawn_enemy('butterfly'))
        if enemy_type == 'bat':
            window.after(random.randint(1000, 2000), lambda: spawn_enemy('bat'))

    def move_enemy(enemy_label, enemy_type):
        if is_paused:
            window.after(100, lambda: move_enemy(enemy_label, enemy_type))
            return
        
        x = enemy_label.winfo_x()
        y = enemy_label.winfo_y()

        frog_x = 300
        frog_y = 300

        dx = frog_x - x
        dy = frog_y - y

        distance = (dx**2 + dy**2) ** 0.5

        pace = speeds.get(enemy_type)
        step_x = dx / distance * pace
        step_y = dy / distance * pace

        new_x = x + step_x
        new_y = y + step_y
        enemy_label.place(x=new_x, y=new_y)


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
from tkinter import Tk, IntVar, Label, PhotoImage, messagebox, Button, Canvas
from PIL import Image, ImageTk
import math
import random


def configure_window():
    window.geometry("600x600")
    window.configure(background="#ffffff")
    window.title("F r o g g y  B u l l e t")


def start_game():
    for widget in window.winfo_children():
        widget.destroy()

    # Add a background for the game
    bg_image = Image.open("background.jpg")
    bg_img = ImageTk.PhotoImage(bg_image)
    bg_label = Label(window, image=bg_img)
    bg_label.image = bg_img
    bg_label.place(relwidth=1, relheight=1)

    # Add a score
    global score
    score_label = Label(window, text="Score: 0", font=("Arial", 16), background="#ffffff")
    score_label.pack(anchor="nw", padx=10, pady=10)

    # Add the Frog
    frog_img = Image.open("green_frog1.png")
    frog = ImageTk.PhotoImage(frog_img)
    frog_label = Label(window, image=frog, background="#ffffff")
    frog_label.image = frog
    frog_label.place(relx=0.5, rely=0.5, anchor="center")

    def update_frog_image():
        rotated_img = frog_img.rotate(rotation_angle)
        frog_label.image = ImageTk.PhotoImage(rotated_img)
        frog_label.config(image=frog_label.image)

    def rotate_left(event=None):
        global rotation_angle
        rotation_angle = (rotation_angle + 10) % 360
        update_frog_image()

    def rotate_right(event=None):
        global rotation_angle
        rotation_angle = (rotation_angle - 10) % 360
        update_frog_image()
    
    def fire(event=None):
        tongue_img = Image.open("tongue.jpg").resize((5,5))
        rotated_tongue = tongue_img.rotate(rotation_angle, resample=Image.BICUBIC, center=(2.5,0))
        tongue = ImageTk.PhotoImage(rotated_tongue)
        tongue_label = Label(window, image=tongue, background="#f7c3c3")
        tongue_label.image = tongue
        tongue_label.place(relx=0.5, rely=0.5, anchor="center")

        window.after(100, tongue_label.destroy)

    window.bind("<Left>", rotate_left)
    window.bind("<Right>", rotate_right)
    window.bind("<space>", fire)
        
    # Pause and Unpause
    is_paused = False

    def pause_toggle():
        nonlocal is_paused
        is_paused = not is_paused
        pause_button.config(text="Unpause" if is_paused else "Pause")

    pause_button = Button(window, text="Pause", command=pause_toggle, font=("Arial", 14))
    pause_button.pack(pady=10)

    bug_img = Image.open("fly.png")
    bug_img = bug_img.resize((20,20))
    bug = ImageTk.PhotoImage(bug_img)

    butterfly_img = Image.open("butterfly.png")
    butterfly_img = butterfly_img.resize((40,40))
    butterfly = ImageTk.PhotoImage(butterfly_img)

    bat_img = Image.open("bat.png")
    bat_img = bat_img.resize((30,30))
    bat = ImageTk.PhotoImage(bat_img)

    enemy_images = [bug, butterfly, bat]

    speeds = {
        'bug': 2,
        'butterfly': 2,
        'bat': 2
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

            side = random.choice(["top", "left", "right", "bottom"])
            if side == "top":
                x_pos = random.randint(0,600)
                y_pos = -50
                enemy_label.place(x=x_pos, y=y_pos)
            elif side == "left":
                x_pos = -50
                y_pos = random.randint(0,600)
                enemy_label.place(x=x_pos, y=y_pos)
            elif side == "right":
                x_pos = 650
                y_pos = random.randint(0,600)
                enemy_label.place(x=x_pos, y=y_pos)
            elif side == "bottom":
                x_pos = random.randint(0,600)
                y_pos = 650
                enemy_label.place(x=x_pos, y=y_pos)

            window.update_idletasks()

            move_enemy(enemy_label, enemy_type)

        if enemy_type == 'bug':
            window.after(5000, lambda: spawn_enemy('bug'))
        if enemy_type == 'butterfly':
            window.after(5000, lambda: spawn_enemy('butterfly'))
        if enemy_type == 'bat':
            window.after(7000, lambda: spawn_enemy('bat'))

    def move_enemy(enemy_label, enemy_type):
        if is_paused:
            window.after(100, lambda: move_enemy(enemy_label, enemy_type))
            return
        
        if not enemy_label.winfo_exists():
            return
        

        x = enemy_label.winfo_x()
        y = enemy_label.winfo_y()

        frog_x = 300
        frog_y = 300

        dx = frog_x - x
        dy = frog_y - y

        distance = math.sqrt(dx**2 + dy**2)

        pace = speeds.get(enemy_type)
        step_x = dx / distance * pace
        step_y = dy / distance * pace

        new_x = x + step_x
        new_y = y + step_y
        enemy_label.place(x=new_x, y=new_y)

        if abs(new_x - frog_x) < 30 and abs(new_y - frog_y) < 30:
            enemy_label.destroy()
            enemy_death(enemy_type)
            return

        window.after(50, lambda: move_enemy(enemy_label, enemy_type))

    def enemy_death(enemy_type):
        global score
        if enemy_type == 'bug':
            score.set(score.get() + 10)
        elif enemy_type == 'butterfly':
            score.set(score.get() + 20)
        elif enemy_type == 'bat':
            score.set(score.get() + 30)

        score_label.config(text=f"Score: {score.get()}")

    def game_over():
        messagebox.showinfo("Game Over", "Game Over!")
        pass

    spawn_enemy('bug')
    spawn_enemy('butterfly')
    spawn_enemy('bat')


def show_leaderboard():
    for widget in window.winfo_children():
        widget.destroy()
    title = Label(window, text="Leaderboard", font=("Arial", 16), background="#ffffff")
    title.pack(anchor="center", pady=10) 

def open_settings():
    for widget in window.winfo_children():
        widget.destroy()
    title = Label(window, text="Settings", font=("Arial", 16), background="#ffffff")
    title.pack(anchor="center", pady=10)

window = Tk()
configure_window()

# All your global stuff goes here
title = Label(window, text="Froggy Bullet", font=("Arial", 16), background="#ffffff")
start_button = Button(window, text="Start", command=start_game, font=("Arial", 16))
leaderboard_button = Button(window, text="Leaderboard", command=show_leaderboard, font=("Arial", 16))
settings_button = Button(window, text="Settings", command=open_settings, font=("Arial", 16))
rotation_angle = 0
score = IntVar(value=0)


# Position the buttons on the window
title.pack(anchor="center", pady=10)
start_button.pack(pady=20)
leaderboard_button.pack(pady=10)
settings_button.pack(pady=10)

window.mainloop()
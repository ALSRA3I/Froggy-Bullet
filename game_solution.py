from tkinter import Tk, IntVar, Label, PhotoImage, messagebox, Button, Canvas, BooleanVar, Entry
from PIL import Image, ImageTk
import math
import random


def configure_window():
    window.geometry("800x800")
    window.configure(background="#ffffff")
    window.title("F r o g g y  B u l l e t")


def show_home():
    global player_name, name_entry
    for widget in window.winfo_children():
        widget.destroy()
    title = Label(window, text="Froggy Bullet", font=("Arial", 16), background="#ffffff")
    start_button = Button(window, text="Start", command=start_game, font=("Arial", 16))
    leaderboard_button = Button(window, text="Leaderboard", command=show_leaderboard, font=("Arial", 16))
    settings_button = Button(window, text="Settings", command=open_settings, font=("Arial", 16))
    name_entry = Entry(window, text="", width=30)

    title.pack(anchor="center", pady=10)
    start_button.pack(pady=20)
    name_entry.pack()
    leaderboard_button.pack(pady=10)
    settings_button.pack(pady=10)


def start_game():
    global player_name, name_entry
    name = name_entry.get()
    player_name = name
    print(player_name)
    if player_name == "":
        messagebox.showerror("missing name", "Please Enter your name in the box")
        return

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
    frog_img = Image.open("frog.png")
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
        global game_over_bool
        if not is_paused or not game_over_bool.get():
            tongue_img = Image.open("tongue.jpg").resize((10, 10))
            tongue = ImageTk.PhotoImage(tongue_img)
            tongue_label = Label(window, image=tongue, background="#f7c3c3")
            tongue_label.image = tongue
            tongue_label.place(x=400, y=400)
            window.update_idletasks()

            def move_tongue():
                x = tongue_label.winfo_x()
                y = tongue_label.winfo_y()

                corrected_angle = rotation_angle + 90

                radians = math.radians(corrected_angle)
                dx = math.cos(radians)
                dy = -math.sin(radians) 

                pace = 50
                step_x = dx * pace
                step_y = dy * pace

                new_x = x + step_x
                new_y = y + step_y
                
                tongue_label.place(x=new_x, y=new_y)

                for enemy_label, enemy_type in enemies:
                    ex, ey = enemy_label.winfo_x(), enemy_label.winfo_y()
                    if abs(new_x - ex) < 25 and abs(new_y - ey) < 25:
                        enemy_label.destroy()  # Remove enemy
                        tongue_label.destroy()  # Remove tongue
                        enemies.remove((enemy_label, enemy_type))  # Remove from list
                        enemy_death(enemy_type)  # Update score
                        return  # Stop tongue movement

                if not (0 <= new_x <= 800 and 0 <= new_y <= 800):
                    tongue_label.destroy() 
                    return

                window.after(50, lambda: move_tongue())
                
            move_tongue()
    
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
    butterfly_img = butterfly_img.resize((30,30))
    butterfly = ImageTk.PhotoImage(butterfly_img)

    bat_img = Image.open("bat.png")
    bat_img = bat_img.resize((25,25))
    bat = ImageTk.PhotoImage(bat_img)

    more_speed = float(score.get()) * 0.001
    speeds = {
        'bug': 2 + more_speed,
        'butterfly': 2 + more_speed,
        'bat': 2 + more_speed
    }

    def spawn_enemy(enemy_type):
        global enemies, game_over_bool
        if not is_paused or not game_over_bool.get():
            if enemy_type == 'bug':
                enemy_img = bug
            elif enemy_type == 'butterfly':
                enemy_img = butterfly
            elif enemy_type == 'bat':
                enemy_img = bat
            
            enemy_label = Label(window, image=enemy_img, background="#ffffff")
            enemies.append((enemy_label, enemy_type))
            enemy_label.image = enemy_img

            side = random.choice(["top", "left", "right", "bottom"])
            if side == "top":
                x_pos = random.randint(0,800)
                y_pos = -50
            elif side == "left":
                x_pos = -50
                y_pos = random.randint(0,800)
               
            elif side == "right":
                x_pos = 850
                y_pos = random.randint(0,800)
               
            elif side == "bottom":
                x_pos = random.randint(0,800)
                y_pos = 850

            enemy_label.place(x=x_pos, y=y_pos)

            window.update_idletasks()

            move_enemy(enemy_label, enemy_type)

            if enemy_type == 'bug':
                window.after(5000, lambda: spawn_enemy('bug'))
            if enemy_type == 'butterfly':
                window.after(8000, lambda: spawn_enemy('butterfly'))
            if enemy_type == 'bat':
                window.after(10000, lambda: spawn_enemy('bat'))

    def move_enemy(enemy_label, enemy_type):
        global game_over_bool
        if is_paused or game_over_bool.get():
            window.after(100, lambda: move_enemy(enemy_label, enemy_type))
            return
        
        if not enemy_label.winfo_exists():
            return

        x = enemy_label.winfo_x()
        y = enemy_label.winfo_y()

        frog_x = 400
        frog_y = 400

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
            game_over()
            return

        window.after(50, lambda: move_enemy(enemy_label, enemy_type))

    def enemy_death(enemy_type):
        global score
        if enemy_type == 'bug':
            score.set(score.get() + 10)
        elif enemy_type == 'butterfly':
            score.set(score.get() + 20)
        elif enemy_type == 'bat':
            score.set(score.get() + 20)

        score_label.config(text=f"Score: {score.get()}")

    spawn_enemy('bug')
    spawn_enemy('butterfly')
    spawn_enemy('bat')


def game_over():
        global game_over_bool, score, player_name
        game_over_bool.set(True)
        for widget in window.winfo_children():
            widget.destroy()
        
        with open("leaderboard.txt", "a") as leaderboard_dict:
            leaderboard_dict.write(f"{player_name},{score.get()}\n")

        title = Label(window, text="Game Over", font=("Arial", 20), background="#ffffff")
        leaderboard_button = Button(window, text="Leaderboard", command=show_leaderboard, font=("Arial", 16))
        score_label = Label(window, text=f"Your Score: {score.get()}", font=("Arial", 16), background="#ffffff")
        
        title.pack(anchor="center", pady=10)
        score_label.pack(pady=10)
        leaderboard_button.pack(pady=10)

def show_leaderboard():
    for widget in window.winfo_children():
        widget.destroy()
    
    title = Label(window, text="Leaderboard", font=("Arial", 16), background="#ffffff")
    home_button = Button(window, text="Back to Home", command=show_home, font=("Arial", 16))
    scores = []
    with open("leaderboard.txt", "r") as file:
        for line in file:
            player_name, score = line.strip().split(',')
            scores.append((player_name, int(score)))

    scores.sort(key=lambda x: x[1], reverse=True)

    title.pack(anchor="center", pady=10)
    for i in range(min(5, len(scores))):
        player_name, score = scores[i]
        rank_label = Label(window, text=f"{i+1}.  {player_name}: {score}", font=("Arial", 12), background="#ffffff")
        rank_label.pack(anchor="center", pady=10)

    home_button.pack(pady=20) 

def open_settings():
    for widget in window.winfo_children():
        widget.destroy()
    title = Label(window, text="Settings", font=("Arial", 16), background="#ffffff")
    home_button = Button(window, text="Back to Home", command=show_home, font=("Arial", 16))

    title.pack(anchor="center", pady=10)
    home_button.pack(pady=20)

window = Tk()
configure_window()
show_home()

# Here are the global variables
rotation_angle = 0  # for frog rotation
score = IntVar(value=0)
game_over_bool = BooleanVar(value=False)    # To prevent movement during the end of the game
enemies = []
player_name = ""

window.mainloop()
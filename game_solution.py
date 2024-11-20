from tkinter import Tk, IntVar, Label, messagebox, Button, BooleanVar, Entry
from tkinter import Toplevel, Spinbox, END
from PIL import Image, ImageTk
import math
import random


def configure_window():
    """
    Configures the main game window with geometry, background, and title.
    """
    window.geometry("800x800")
    window.configure(background="#ffffff")
    window.title("F r o g g y  B u l l e t")


def show_home():
    """
    Displays the home screen of the game with options for start, leaderboard,
    settings, and entering the player's name.
    """
    global player_name, name_entry
    for widget in window.winfo_children():
        widget.destroy()

    # Title and buttons for home screen
    title = Label(window, text="Froggy Bullet",
                  font=("Arial", 16), background="#ffffff")
    start_button = Button(window, text="Start",
                          command=start_game, font=("Arial", 16))
    leaderboard_button = Button(window, text="Leaderboard",
                                command=show_leaderboard, font=("Arial", 16))
    settings_button = Button(window, text="Settings",
                             command=open_settings, font=("Arial", 16))
    name_entry = Entry(window, text="", width=30)

    # Pack widgets into the window
    title.pack(anchor="center", pady=10)
    start_button.pack(pady=20)
    name_entry.pack()
    leaderboard_button.pack(pady=10)
    settings_button.pack(pady=10)


def start_game():
    """
    Initializes the game state, sets up the game screen with background,
    score, and the player's frog character. Handles rotation,
    shooting, and enemy spawning.
    """
    global player_name, name_entry, game_over_bool, right_button, left_button
    global fire_button
    game_over_bool.set(False)
    name = name_entry.get()
    player_name = name

    if player_name == "":
        messagebox.showerror("Missing Name",
                             "Please enter your name in the box")
        return

    for widget in window.winfo_children():
        widget.destroy()

    # Background setup
    bg_image = Image.open("background.jpg")
    bg_img = ImageTk.PhotoImage(bg_image)
    bg_label = Label(window, image=bg_img)
    bg_label.image = bg_img
    bg_label.place(relwidth=1, relheight=1)

    # Score display
    global score
    score_label = Label(window, text="Score: 0",
                        font=("Arial", 16), background="#ffffff")
    score_label.pack(anchor="nw", padx=10, pady=10)

    # Frog character setup
    frog_img = Image.open("frog.png")
    frog = ImageTk.PhotoImage(frog_img)
    frog_label = Label(window, image=frog, background="#ffde59")
    frog_label.image = frog
    frog_label.place(relx=0.5, rely=0.5, anchor="center")

    def update_frog_image():
        """Updates the frog image to reflect the current rotation angle."""
        rotated_img = frog_img.rotate(rotation_angle)
        frog_label.image = ImageTk.PhotoImage(rotated_img)
        frog_label.config(image=frog_label.image)

    def rotate_left(event=None):
        """Rotates the frog to the left by increasing the rotation angle."""
        global rotation_angle, rotation_speed
        rotation_angle = (rotation_angle + rotation_speed) % 360
        update_frog_image()

    def rotate_right(event=None):
        """Rotates the frog to the right by decreasing the rotation angle."""
        global rotation_angle, rotation_speed
        rotation_angle = (rotation_angle - rotation_speed) % 360
        update_frog_image()

    def fire(event=None):
        """
        Fires a tongue projectile in the direction the frog is facing.
        Handles collision detection with enemies and boundary conditions.
        """
        global game_over_bool
        if not is_paused or not game_over_bool.get():
            tongue_img = Image.open("tongue.jpg").resize((10, 10))
            tongue = ImageTk.PhotoImage(tongue_img)
            tongue_label = Label(window, image=tongue, background="#f7c3c3")
            tongue_label.image = tongue
            tongue_label.place(x=400, y=400)
            window.update_idletasks()

            def move_tongue():
                """
                Moves the tongue projectile in the direction of rotation.
                Checks for collisions with enemies or boundaries.
                """
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
                        enemies.remove((enemy_label, enemy_type))
                        enemy_death(enemy_type)  # Update score
                        return  # Stop tongue movement

                if not (0 <= new_x <= 800 and 0 <= new_y <= 800):
                    tongue_label.destroy()
                    return

                window.after(50, lambda: move_tongue())

            move_tongue()

    # Bind keys for movement and fire actions
    window.bind(f"<{left_button}>", rotate_left)
    window.bind(f"<{right_button}>", rotate_right)
    window.bind(f"<{fire_button}>", fire)

    # Pause functionality
    is_paused = False

    def pause_toggle():
        """Toggles the paused state of the game."""
        nonlocal is_paused
        is_paused = not is_paused
        pause_button.config(text="Unpause" if is_paused else "Pause")

    pause_button = Button(window, text="Pause",
                          command=pause_toggle, font=("Arial", 14))
    pause_button.pack()

    def boss_key(event=None):
        """
        Toggles a fake workspace window for the boss key functionality.
        Minimizes the game window and pauses the game.
        """
        mock_window = Toplevel(window)
        mock_window.title("My Workspace")
        mock_window.geometry("800x800")
        bg_image = Image.open("mock_picture.jpg")
        bg_image = bg_image.resize((800, 800))
        bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = Label(mock_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(relwidth=1, relheight=1)

        window.iconify()
        pause_toggle()

    # Bind boss key (Ctrl+B)
    window.bind('<Control-b>', boss_key)

    def submit_key():
        """
        Handles the submission of cheat codes entered by the user.
        Based on the cheat code:
            - "vanish": Removes all enemies from the screen.
            - "snail": Temporarily slows down enemies' movement for 10 seconds.
            - Invalid code: Displays an error message.

        Also hides the cheat input field after submission.
        """
        global enemy_speed, enemies

        # Retrieve and process the cheat code input
        cheat_code = cheat_entry.get().strip().lower()

        if cheat_code == "vanish":
            # Remove all enemy labels and clear the enemies list
            for enemy_label, _ in enemies:
                if enemy_label.winfo_exists():
                    enemy_label.destroy()
            enemies.clear()
        elif cheat_code == "snail":
            # Temporarily reduce enemy speed and restore it after 10 seconds
            original_speed = enemy_speed
            enemy_speed = 1
            speeds['bug'] = enemy_speed
            speeds['butterfly'] = enemy_speed
            speeds['bat'] = enemy_speed

            def reset_speed():
                """Restores the original speed of the enemies."""
                global enemy_speed
                enemy_speed = original_speed
                speeds['bug'] = enemy_speed
                speeds['butterfly'] = enemy_speed
                speeds['bat'] = enemy_speed

            window.after(10000, reset_speed)
        else:
            # Inform the user of an invalid cheat code
            messagebox.showinfo("Invalid Cheat Code",
                                "The cheat code you entered isn't recognized.")

        # Clear and hide the cheat input field and button
        cheat_entry.delete(0, END)
        cheat_entry.pack_forget()
        submit_button.pack_forget()

    def show_input(event=False):
        """
        Displays the input field and button for entering cheat codes.
        """
        cheat_entry.pack()
        submit_button.pack()
        cheat_entry.focus_set()

    # Create cheat code entry field and button
    # and bind the input trigger to Ctrl+C
    cheat_entry = Entry(window, text="", width=20)
    window.bind("<Control-c>", show_input)
    submit_button = Button(window, text="Enter",
                           command=submit_key, font=("Arial", 8))

    # Load and resize images for different enemy types
    bug_img = Image.open("fly.png").resize((20, 20))
    bug = ImageTk.PhotoImage(bug_img)

    butterfly_img = Image.open("butterfly.png").resize((30, 30))
    butterfly = ImageTk.PhotoImage(butterfly_img)

    bat_img = Image.open("bat.png").resize((25, 25))
    bat = ImageTk.PhotoImage(bat_img)

    # Adjust enemy speeds dynamically based on the score
    more_speed = float(score.get()) * 0.001
    speeds = {
        'bug': enemy_speed + more_speed,
        'butterfly': enemy_speed + more_speed,
        'bat': enemy_speed + more_speed
    }

    def spawn_enemy(enemy_type):
        """
        Spawns an enemy of the given type at a random
        position outside the screen.
        Args:
            enemy_type (str): The type of enemy ('bug', 'butterfly', 'bat').
        """
        global enemies, game_over_bool

        if not is_paused or not game_over_bool.get():
            # Select the appropriate image for the enemy
            enemy_img = {
                'bug': bug,
                'butterfly': butterfly,
                'bat': bat
            }.get(enemy_type)

            enemy_label = Label(window, image=enemy_img, background="#7ed957")
            enemies.append((enemy_label, enemy_type))
            enemy_label.image = enemy_img

            # Randomize the spawn location
            side = random.choice(["top", "left", "right", "bottom"])
            if side == "top":
                x_pos, y_pos = random.randint(0, 800), -50
            elif side == "left":
                x_pos, y_pos = -50, random.randint(0, 800)
            elif side == "right":
                x_pos, y_pos = 850, random.randint(0, 800)
            elif side == "bottom":
                x_pos, y_pos = random.randint(0, 800), 850

            enemy_label.place(x=x_pos, y=y_pos)
            window.update_idletasks()

            # Move the enemy and schedule future spawns
            move_enemy(enemy_label, enemy_type)
            spawn_delays = {'bug': 5000, 'butterfly': 8000, 'bat': 10000}
            window.after(spawn_delays[enemy_type],
                         lambda: spawn_enemy(enemy_type))

    def move_enemy(enemy_label, enemy_type):
        """
        Moves an enemy towards the frog's position.
        If the enemy reaches the frog, the game ends.
        Args:
            enemy_label (Label): The label representing the enemy.
            enemy_type (str): The type of enemy.
        """
        global game_over_bool

        if is_paused or game_over_bool.get():
            window.after(100, lambda: move_enemy(enemy_label, enemy_type))
            return

        if not enemy_label.winfo_exists():
            return

        x, y = enemy_label.winfo_x(), enemy_label.winfo_y()
        frog_x, frog_y = 400, 400  # Frog's position

        # Calculate movement towards the frog
        dx, dy = frog_x - x, frog_y - y
        distance = math.sqrt(dx**2 + dy**2)
        pace = speeds.get(enemy_type)
        step_x, step_y = dx / distance * pace, dy / distance * pace

        # Update position
        new_x, new_y = x + step_x, y + step_y
        enemy_label.place(x=new_x, y=new_y)

        # Check for collision with the frog
        if abs(new_x - frog_x) < 30 and abs(new_y - frog_y) < 30:
            enemy_label.destroy()
            game_over()
            return

        # Schedule next movement
        window.after(50, lambda: move_enemy(enemy_label, enemy_type))

    def enemy_death(enemy_type):
        """
        Handles the scoring when an enemy is defeated.
        Args:
            enemy_type (str): The type of enemy defeated.
        """
        global score
        points = {'bug': 10, 'butterfly': 20, 'bat': 20}
        score.set(score.get() + points.get(enemy_type, 0))
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

    title = Label(window, text="Game Over",
                  font=("Arial", 20), background="#ffffff")
    leaderboard_button = Button(window, text="Leaderboard",
                                command=show_leaderboard, font=("Arial", 16))
    home_button = Button(window, text="Back to Home",
                         command=show_home, font=("Arial", 16))
    score_label = Label(window, text=f"Your Score: {score.get()}",
                        font=("Arial", 16), background="#ffffff")
    title.pack(anchor="center", pady=10)
    score_label.pack(pady=10)
    leaderboard_button.pack(pady=10)
    home_button.pack(pady=20)


def show_leaderboard():
    for widget in window.winfo_children():
        widget.destroy()
    title = Label(window, text="Leaderboard",
                  font=("Arial", 16), background="#ffffff")
    home_button = Button(window, text="Back to Home",
                         command=show_home, font=("Arial", 16))
    scores = []
    with open("leaderboard.txt", "r") as file:
        for line in file:
            player_name, score = line.strip().split(',')
            scores.append((player_name, int(score)))

    scores.sort(key=lambda x: x[1], reverse=True)

    title.pack(anchor="center", pady=10)
    for i in range(min(5, len(scores))):
        player_name, score = scores[i]
        rank_label = Label(window, text=f"{i+1}. {player_name}: {score}",
                           font=("Arial", 12), background="#ffffff")
        rank_label.pack(anchor="center", pady=10)

    home_button.pack(pady=20)


def open_settings():
    for widget in window.winfo_children():
        widget.destroy()

    def set_left_binding(event):
        global left_button
        left_button = event.keysym
        left_label.config(text=f"Left action now bound to: {left_button}")
        window.unbind("<KeyPress>")

    def set_right_binding(event):
        global right_button
        right_button = event.keysym
        right_label.config(text=f"Right action now bound to: {right_button}")
        window.unbind("<KeyPress>")

    def set_fire_binding(event):
        global fire_button
        fire_button = event.keysym
        fire_label.config(text=f"Fire action now bound to: {fire_button}")
        window.unbind("<KeyPress>")

    def change_rotation_func():
        global rotation_speed
        rotation_speed = int(change_rotation.get())
        rotation_label.config(text=f"Rotation Speed: {rotation_speed}")

    title = Label(window, text="Settings",
                  font=("Arial", 16), background="#ffffff")
    home_button = Button(window,
                         text="Back to Home",
                         command=show_home,
                         font=("Arial", 16))
    left_label = Label(window,
                       text=f"Left currently bound to: {left_button}",
                       font=("Arial", 16), background="#ffffff")
    right_label = Label(window,
                        text=f"Right currently bound to: {right_button}",
                        font=("Arial", 16), background="#ffffff")
    fire_label = Label(window,
                       text=f"Fire currently bound to: {fire_button}",
                       font=("Arial", 16), background="#ffffff")
    change_left = Button(window,
                         text="Press any key for Left", font=("Arial", 16),
                         command=lambda: window.bind("<KeyPress>",
                                                     set_left_binding))
    change_right = Button(window,
                          text="Press any key for Right", font=("Arial", 16),
                          command=lambda: window.bind("<KeyPress>",
                                                      set_right_binding))
    change_fire = Button(window,
                         text="Press any key for Fire", font=("Arial", 16),
                         command=lambda: window.bind("<KeyPress>",
                                                     set_fire_binding))

    change_rotation_button = Button(window,
                                    text="Change the rotation speed",
                                    font=("Arial", 16),
                                    command=change_rotation_func)
    change_rotation = Spinbox(window, from_=1, to=20,
                              state="readonly", font=("Arial", 14), width=5)
    change_rotation.delete(0, "end")
    change_rotation.insert(0, rotation_speed)
    rotation_label = Label(window, text=f"Rotation Speed: {rotation_speed}",
                           font=("Arial", 16), background="#ffffff")

    title.pack(anchor="center", pady=10)
    change_left.pack(pady=10)
    left_label.pack()
    change_right.pack(pady=10)
    right_label.pack()

    change_fire.pack(pady=10)
    fire_label.pack()

    change_rotation_button.pack(pady=10)
    change_rotation.pack()
    rotation_label.pack(pady=10)

    home_button.pack(pady=30)


window = Tk()
configure_window()
show_home()

# Here is the global variables
rotation_angle = 0  # for frog rotation
score = IntVar(value=0)
game_over_bool = BooleanVar(value=False)
enemies = []
player_name = ""
right_button = "Right"
left_button = "Left"
fire_button = "space"
rotation_speed = 10
enemy_speed = 2

window.mainloop()

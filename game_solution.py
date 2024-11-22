from tkinter import Tk, IntVar, Label, messagebox, Button, BooleanVar, Entry
from tkinter import Toplevel, Spinbox, END
from PIL import Image, ImageTk
import math
import random
import pickle
import os


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
    start_button = Button(window, text="Start Game",
                          command=start_game, font=("Arial", 16))
    load_button = Button(window, text="Load Game",
                         command=load_game_settings, font=("Arial", 16))
    leaderboard_button = Button(window, text="Leaderboard",
                                command=show_leaderboard, font=("Arial", 16))
    settings_button = Button(window, text="Settings",
                             command=open_settings, font=("Arial", 16))
    name_entry = Entry(window, text="", width=30)

    # Pack widgets into the window
    title_image = Image.open("title.png")
    title_img = ImageTk.PhotoImage(title_image)
    title_label = Label(window, image=title_img)
    title_label.image = title_img
    title_label.pack()
    start_button.pack(pady=20)
    name_entry.pack()
    load_button.pack(pady=10)
    leaderboard_button.pack(pady=10)
    settings_button.pack(pady=10)


def start_game():
    """
    Initializes the game state, sets up the game screen with background,
    score, and the player's frog character. Handles rotation,
    shooting, and enemy spawning.
    """
    global player_name, name_entry, game_over_bool, is_paused, is_loaded
    global fire_button, right_button, left_button, enemies, score
    global bat_spawned, active_timers, more_speed

    # Remove the previous enemies
    for enemy_label, _ in enemies:
        enemy_label.destroy()
    enemies = []

    # Remove the previous spawning schedules
    for timer_id in active_timers:
        window.after_cancel(timer_id)
    active_timers = []

    # Changes that happen only if the game is not loaded
    if not is_loaded.get():
        score.set(0)
        bat_spawned = False
        name = name_entry.get()
        player_name = name

    # Make sure that a name is entered if it's a new game
    if not is_loaded.get() and player_name == "":
        messagebox.showerror("Missing Name",
                             "Please enter your name in the box")
        return

    # Resetting the original states.
    is_loaded.set(False)
    game_over_bool.set(False)
    is_paused.set(False)

    for widget in window.winfo_children():
        widget.destroy()

    # Background setup
    bg_image = Image.open("background.jpg")
    bg_img = ImageTk.PhotoImage(bg_image)
    bg_label = Label(window, image=bg_img)
    bg_label.image = bg_img
    bg_label.place(relwidth=1, relheight=1)

    # Score display
    score_label = Label(window, text=f"Score: {score.get()}",
                        font=("Arial", 16), background="#ffffff")
    score_label.pack(anchor="nw", padx=10, pady=10)

    # Add Save Game button
    save_button = Button(window, text="Save Game",
                         command=save_game_settings, font=("Arial", 10))
    save_button.pack(anchor="nw", padx=10)

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
        global rotation_angle, rotation_speed, is_paused, game_over_bool
        if not is_paused.get() and not game_over_bool.get():
            rotation_angle = (rotation_angle + rotation_speed) % 360
            update_frog_image()

    def rotate_right(event=None):
        """Rotates the frog to the right by decreasing the rotation angle."""
        global rotation_angle, rotation_speed, is_paused, game_over_bool
        if not is_paused.get() and not game_over_bool.get():
            rotation_angle = (rotation_angle - rotation_speed) % 360
            update_frog_image()

    def fire(event=None):
        """
        Fires a tongue in the direction the frog is facing.
        Handles collision detection with enemies and boundary conditions.
        """
        global game_over_bool, is_paused
        if not is_paused.get() and not game_over_bool.get():
            # Create and display the tongue image.
            tongue_img = Image.open("tongue.jpg").resize((10, 10))
            tongue = ImageTk.PhotoImage(tongue_img)
            tongue_label = Label(window, image=tongue, background="#f7c3c3")
            tongue_label.image = tongue
            tongue_label.place(x=400, y=400)
            window.update_idletasks()

            def move_tongue():
                """
                Moves the tongue in the direction of rotation.
                Checks for collisions with enemies or boundaries.
                """
                # Get the current tongue position.
                x = tongue_label.winfo_x()
                y = tongue_label.winfo_y()

                # Calculate movement direction based on the rotation angle.
                corrected_angle = rotation_angle + 90
                radians = math.radians(corrected_angle)  # Convert to radians
                dx = math.cos(radians)
                dy = -math.sin(radians)

                # Movement speed and steps
                pace = 50
                step_x = dx * pace
                step_y = dy * pace
                new_x = x + step_x
                new_y = y + step_y

                # Update tongue position.
                tongue_label.place(x=new_x, y=new_y)

                # Check for collisions with enemies.
                for enemy_label, enemy_type in enemies:
                    ex, ey = enemy_label.winfo_x(), enemy_label.winfo_y()
                    if abs(new_x - ex) < 25 and abs(new_y - ey) < 25:
                        enemy_label.destroy()  # Remove enemy
                        tongue_label.destroy()  # Remove tongue
                        enemies.remove((enemy_label, enemy_type))
                        enemy_death(enemy_type)  # Update score
                        return  # Stop tongue movement

                # Destroy the tongue if it moves out of window
                if not (0 <= new_x <= 800 and 0 <= new_y <= 800):
                    tongue_label.destroy()
                    return

                window.after(50, lambda: move_tongue())

            move_tongue()

    # Bind keys for movement and fire actions
    window.bind(f"<{left_button}>", rotate_left)
    window.bind(f"<{right_button}>", rotate_right)
    window.bind(f"<{fire_button}>", fire)

    def pause_toggle():
        """Toggles the paused state of the game."""
        global is_paused, active_timers, bat_spawned

        is_paused.set(not is_paused.get())
        pause_button.config(text="Unpause" if is_paused.get() else "Pause")

        if is_paused.get():
            for timer_id in active_timers:
                window.after_cancel(timer_id)
            active_timers = []
        else:
            spawn_enemy('bug')
            spawn_enemy('butterfly')
            if bat_spawned:
                spawn_enemy('bat')

    # Add the pause button and display it.
    pause_button = Button(window, text="Pause",
                          command=pause_toggle, font=("Arial", 10))
    pause_button.pack(anchor="nw", padx=10)

    def boss_key(event=None):
        """
        Toggles a fake workspace window for the boss key functionality.
        Minimizes the game window and pauses the game.
        """
        mock_window = Toplevel(window)
        mock_window.title("My Workspace")
        screen_width = mock_window.winfo_screenwidth()
        screen_height = mock_window.winfo_screenheight()
        mock_window.geometry(f"{screen_width}x{screen_height}")
        bg_image = Image.open("mock_picture.png")
        bg_image = bg_image.resize((screen_width, screen_height))
        bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = Label(mock_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(relwidth=1, relheight=1)

        # Minimize the game window and pauses the game
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
            - "oman": Increases the score by 100

        Also hides the cheat input field after submission.
        """
        global enemy_speed, enemies, score

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
                global enemy_speed, more_speed
                enemy_speed = original_speed
                speeds['bug'] = enemy_speed + more_speed
                speeds['butterfly'] = enemy_speed + more_speed
                speeds['bat'] = enemy_speed + 3 + more_speed

            window.after(10000, reset_speed)
        elif cheat_code == "oman":
            new_score = score.get() + 100
            score.set(new_score)

            # Update the score label to reflect the new score
            score_label.config(text=f"Score: {new_score}")
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
    butterfly_img = Image.open("butterfly.png").resize((30, 30))
    bat_img = Image.open("bat.png").resize((30, 30))

    # Adjust enemy speeds dynamically based on the score
    more_speed = float(score.get()) // 300
    speeds = {
        'bug': enemy_speed + more_speed,
        'butterfly': enemy_speed + more_speed,
        'bat': enemy_speed + 3 + more_speed
    }

    def spawn_enemy(enemy_type):
        """
        Spawns an enemy of the given type at a random
        position outside the screen.
        Args:
            enemy_type (str): The type of enemy ('bug', 'butterfly', 'bat').
        """
        global enemies, game_over_bool, is_paused, active_timers

        if not is_paused.get() or not game_over_bool.get():
            # Select the appropriate image for the enemy
            enemy_imgs = {
                'bug': bug_img,
                'butterfly': butterfly_img,
                'bat': bat_img
            }

            original_img = enemy_imgs.get(enemy_type)

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

            # Calculate angle to face the frog
            frog_x, frog_y = 400, 400  # Frog's position
            dx, dy = frog_x - x_pos, frog_y - y_pos
            angle = math.degrees(math.atan2(-dy, dx))
            angle -= 90

            # Rotate the image to face the frog
            rotated_img = original_img.rotate(angle, expand=True)
            enemy_img = ImageTk.PhotoImage(rotated_img)

            enemy_label = Label(window, image=enemy_img, background="#7ed957")
            enemies.append((enemy_label, enemy_type))
            enemy_label.image = enemy_img

            enemy_label.place(x=x_pos, y=y_pos)
            window.update_idletasks()

            # Move the enemy and schedule future spawns
            move_enemy(enemy_label, enemy_type)
            spawn_delays = {'bug': 3000, 'butterfly': 4000, 'bat': 8000}
            timer_id = window.after(spawn_delays[enemy_type],
                                    lambda: spawn_enemy(enemy_type))
            active_timers.append(timer_id)

    def move_enemy(enemy_label, enemy_type):
        """
        Moves an enemy towards the frog's position.
        If the enemy reaches the frog, the game ends.
        Args:
            enemy_label (Label): The label representing the enemy.
            enemy_type (str): The type of enemy.
        """
        global game_over_bool, is_paused

        if is_paused.get() or game_over_bool.get():
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
        step_x = dx / distance * pace
        step_y = dy / distance * pace

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
        global score, bat_spawned
        points = {'bug': 10, 'butterfly': 20, 'bat': 20}
        score.set(score.get() + points.get(enemy_type, 0))
        score_label.config(text=f"Score: {score.get()}")

        # The bat will be spawned after score 200
        if score.get() >= 200 and not bat_spawned:
            bat_spawned = True
            spawn_enemy('bat')

    spawn_enemy('bug')
    spawn_enemy('butterfly')


def game_over():
    """Ends the game and transitions to a "Game Over" screen."""
    global game_over_bool, score, player_name, enemies, active_timers

    # Set the game-over flag to True.
    game_over_bool.set(True)

    # Delete any saved game data.
    delete_saved_game()

    # Remove the previous enemies
    for enemy_label, _ in enemies:
        enemy_label.destroy()
    enemies = []

    # Remove the previous spawning schedules
    for timer_id in active_timers:
        window.after_cancel(timer_id)
    active_timers = []

    # Clear all widgets from the main game window.
    for widget in window.winfo_children():
        widget.destroy()

    # Append the player's name and score to the leaderboard file.
    with open("leaderboard.txt", "a") as leaderboard_dict:
        leaderboard_dict.write(f"{player_name},{score.get()}\n")

    # Create and configure the Leaderboard button.
    leaderboard_button = Button(
        window,
        text="Leaderboard",
        command=show_leaderboard,
        font=("Arial", 16)
    )

    # Create and configure the Home button.
    home_button = Button(
        window,
        text="Back to Home",
        command=show_home,
        font=("Arial", 16)
    )

    # Display the player's final score.
    score_label = Label(
        window,
        text=f"Your Score: {score.get()}",
        font=("Arial", 16),
        background="#ffffff"
    )

    # Load and display the "Game Over" image.
    over_image = Image.open("over.png")
    over_img = ImageTk.PhotoImage(over_image)
    over_label = Label(window, image=over_img)
    over_label.image = over_img

    # Pack the widgets on the "Game Over" screen.
    over_label.pack()
    score_label.pack(pady=10)
    leaderboard_button.pack(pady=10)
    home_button.pack(pady=20)


def show_leaderboard():
    """Displays the leaderboard screen with the top player scores."""

    # Clear all widgets from the main window.
    for widget in window.winfo_children():
        widget.destroy()

    # Create and configure the leaderboard title.
    title = Label(
        window,
        text="Leaderboard",
        font=("Arial", 16),
        background="#ffffff"
    )

    # Create the "Back to Home" button for navigation.
    home_button = Button(
        window,
        text="Back to Home",
        command=show_home,
        font=("Arial", 16)
    )

    # Initialize a list to store scores from the leaderboard file.
    scores = []

    # Read and parse the leaderboard file to extract player names and scores.
    with open("leaderboard.txt", "r") as file:
        for line in file:
            player_name, score = line.strip().split(',')
            scores.append((player_name, int(score)))

    # Sort scores in descending order.
    scores.sort(key=lambda x: x[1], reverse=True)

    # Display the leaderboard title at the top.
    title.pack(anchor="center", pady=10)

    # Display the top 5 scores or fewer if there are less than 5 entries.
    for i in range(min(5, len(scores))):
        player_name, score = scores[i]
        rank_label = Label(
            window,
            text=f"{i+1}. {player_name}: {score}",
            font=("Arial", 12),
            background="#ffffff"
        )
        rank_label.pack(anchor="center", pady=10)

    # Add the "Back to Home" button at the bottom.
    home_button.pack(pady=20)


def open_settings():
    """Displays the settings screen where the user
    can customize game controls and rotation speed."""

    # Clear all widgets from the main window.
    for widget in window.winfo_children():
        widget.destroy()

    # Function to bind the "Left" key action to a new key.
    def set_left_binding(event):
        global left_button
        left_button = event.keysym
        left_label.config(text=f"Left now bound to: {left_button}")
        window.unbind("<KeyPress>")

    # Function to bind the "Right" key action to a new key.
    def set_right_binding(event):
        global right_button
        right_button = event.keysym
        right_label.config(text=f"Right now bound to: {right_button}")
        window.unbind("<KeyPress>")

    # Function to bind the "Fire" key action to a new key.
    def set_fire_binding(event):
        global fire_button
        fire_button = event.keysym
        fire_label.config(text=f"Fire now bound to: {fire_button}")
        window.unbind("<KeyPress>")

    # Function to change the rotation speed of the game.
    def change_rotation_func():
        global rotation_speed
        rotation_speed = int(change_rotation.get())
        rotation_label.config(text=f"Rotation Speed: {rotation_speed}")

    # Title label.
    title = Label(window, text="Settings",
                  font=("Arial", 16), background="#ffffff")

    # "Back to Home" button for navigation.
    home_button = Button(window,
                         text="Back to Home",
                         command=show_home,
                         font=("Arial", 16))

    # Labels to display current key bindings.
    left_label = Label(window,
                       text=f"Left currently bound to: {left_button}",
                       font=("Arial", 16), background="#ffffff")
    right_label = Label(window,
                        text=f"Right currently bound to: {right_button}",
                        font=("Arial", 16), background="#ffffff")
    fire_label = Label(window,
                       text=f"Fire currently bound to: {fire_button}",
                       font=("Arial", 16), background="#ffffff")

    # Buttons to change key bindings.
    change_left = Button(window,
                         text="Press any key for Left",
                         font=("Arial", 16),
                         command=lambda: window.bind("<KeyPress>",
                                                     set_left_binding))
    change_right = Button(window,
                          text="Press any key for Right",
                          font=("Arial", 16),
                          command=lambda: window.bind("<KeyPress>",
                                                      set_right_binding))
    change_fire = Button(window,
                         text="Press any key for Fire",
                         font=("Arial", 16),
                         command=lambda: window.bind("<KeyPress>",
                                                     set_fire_binding))

    # Button and spinbox for adjusting rotation speed.
    change_rotation_button = Button(window,
                                    text="Change the rotation speed",
                                    font=("Arial", 16),
                                    command=change_rotation_func)
    change_rotation = Spinbox(window, from_=1, to=20,
                              state="readonly", font=("Arial", 14), width=5)
    change_rotation.delete(0, "end")  # Clear initial value.
    change_rotation.insert(0, rotation_speed)

    # Label to display the current rotation speed.
    rotation_label = Label(window, text=f"Rotation Speed: {rotation_speed}",
                           font=("Arial", 16), background="#ffffff")

    # Pack UI elements to display them on the settings screen.
    title.pack(anchor="center", pady=10)

    # Key-binding controls.
    change_left.pack(pady=10)
    left_label.pack()
    change_right.pack(pady=10)
    right_label.pack()
    change_fire.pack(pady=10)
    fire_label.pack()

    # Rotation speed controls.
    change_rotation_button.pack(pady=10)
    change_rotation.pack()
    rotation_label.pack(pady=10)

    # Home button at the bottom.
    home_button.pack(pady=30)


def save_game_settings():
    """Saves the current game settings and progress to a file."""
    global score, rotation_angle, player_name, right_button
    global left_button, fire_button, rotation_speed, enemy_speed

    # Create a dictionary containing all settings and game progress to save.
    settings = {
        "score": score.get(),
        "rotation_angle": rotation_angle,
        "player_name": player_name,
        "right_button": right_button,
        "left_button": left_button,
        "fire_button": fire_button,
        "rotation_speed": rotation_speed,
        "enemy_speed": enemy_speed,
    }

    # Save the settings to a binary file using pickle.
    with open(SAVE_FILE, "wb") as file:
        pickle.dump(settings, file)

    # Show a confirmation message to the user.
    messagebox.showinfo("Game Saved", "Your game has been saved.")


def load_game_settings():
    """Loads saved game settings and progress from a file."""
    global score, rotation_angle, player_name, right_button, left_button
    global fire_button, rotation_speed, enemy_speed, is_loaded

    # Check if the save file exists.
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as file:
            settings = pickle.load(file)  # Deserialize the saved settings.

        # Apply loaded settings to the game variables.
        score.set(settings["score"])
        rotation_angle = settings["rotation_angle"]
        player_name = settings["player_name"]
        right_button = settings["right_button"]
        left_button = settings["left_button"]
        fire_button = settings["fire_button"]
        rotation_speed = settings["rotation_speed"]
        enemy_speed = settings["enemy_speed"]

        is_loaded.set(True)
        # Start the game with the loaded settings.
        start_game()

        # Notify the user that the game has been loaded or not found.
        messagebox.showinfo("Game Loaded", "Your game has been loaded.")
    else:
        messagebox.showinfo("No Saved Data", "No saved game data found.")


def delete_saved_game():
    """Deletes saved game settings."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


# Initialize the main application window and configure it.
window = Tk()
configure_window()
show_home()

# Global game variables.
rotation_angle = 0  # Frog's rotation angle.
score = IntVar(value=0)  # Player's score.
game_over_bool = BooleanVar(value=False)  # Tracks game over state.
is_paused = BooleanVar(value=False)  # Tracks pausing state.
is_loaded = BooleanVar(value=False)  # Tracks loading state.
enemies = []  # List of enemies in the game.
player_name = ""  # Player's name.
right_button = "Right"  # Key for moving right.
left_button = "Left"  # Key for moving left.
fire_button = "space"  # Key for firing.
rotation_speed = 10  # Frog's rotation speed.
enemy_speed = 2  # Enemy movement speed.
bat_spawned = False  # Tracks if a bat enemy has spawned.
active_timers = []  # List of schedule enemies in the game.
more_speed = 0  # For speed up the enemies
SAVE_FILE = "game_save.pkl"  # File for saving/loading functionality.

window.mainloop()

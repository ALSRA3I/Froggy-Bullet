from tkinter import Tk, IntVar, Label, messagebox, Button, BooleanVar, Entry
from tkinter import Toplevel, Spinbox, END
from PIL import Image, ImageTk
import math
import random
import pickle
import os


class GameObject:
    """Base class for all game objects."""
    
    def __init__(self, window, x, y, image_path, resize=None):
        """
        Initialize a game object with position and image.
        
        Args:
            window: Tkinter window
            x: x-coordinate
            y: y-coordinate
            image_path: Path to the image file
            resize: Optional tuple (width, height) to resize the image
        """
        self.window = window
        self.x = x
        self.y = y
        
        # Load and process image
        self.original_img = Image.open(image_path)
        if resize:
            self.original_img = self.original_img.resize(resize)
        
        self.img = ImageTk.PhotoImage(self.original_img)
        self.label = Label(window, image=self.img, background="#d4fdc2")
        self.label.image = self.img
        self.place()
    
    def place(self):
        """Position the object on the screen."""
        # Center the object at the specified coordinates
        img_width = self.original_img.width
        img_height = self.original_img.height
        self.label.place(x=self.x - img_width // 2, y=self.y - img_height // 2)
        
    def destroy(self):
        """Remove the object from the screen."""
        self.label.destroy()
        
    def rotate(self, angle):
        """
        Rotate the object's image.
        
        Args:
            angle: Rotation angle in degrees
        """
        # Create a rotated version of the original image
        rotated_img = self.original_img.rotate(angle, expand=False)
        
        # Convert to PhotoImage for display
        self.img = ImageTk.PhotoImage(rotated_img)
        self.label.config(image=self.img)
        self.label.image = self.img
        
        # Keep the object centered at its coordinates
        self.label.place(x=self.x - self.original_img.width // 2, 
                        y=self.y - self.original_img.height // 2)


class Frog(GameObject):
    """Player-controlled frog character."""
    
    def __init__(self, window, game_instance):
        """
        Initialize the frog character.
        
        Args:
            window: Tkinter window
            game_instance: Reference to the Game instance
        """
        super().__init__(window, 400, 400, "frog.png")
        self.rotation_angle = 0
        self.rotation_speed = 10
        self.game = game_instance
    
    def rotate_left(self, event=None):
        """Rotate the frog to the left."""
        if not self.game.is_paused.get() and not self.game.game_over_bool.get():
            self.rotation_angle = (self.rotation_angle + self.rotation_speed) % 360
            self.rotate(self.rotation_angle)
    
    def rotate_right(self, event=None):
        """Rotate the frog to the right."""
        if not self.game.is_paused.get() and not self.game.game_over_bool.get():
            self.rotation_angle = (self.rotation_angle - self.rotation_speed) % 360
            self.rotate(self.rotation_angle)
    
    def fire(self, event=None):
        """Fire the frog's tongue."""
        if not self.game.is_paused.get() and not self.game.game_over_bool.get():
            Tongue(self.window, self.x, self.y, self.rotation_angle, self.game)


class Tongue(GameObject):
    """Frog's tongue projectile."""
    
    def __init__(self, window, x, y, angle, game_instance):
        """
        Initialize the tongue projectile.
        
        Args:
            window: Tkinter window
            x: Starting x-coordinate
            y: Starting y-coordinate
            angle: Direction angle in degrees
            game_instance: Reference to the Game instance
        """
        super().__init__(window, x, y, "tongue.jpg", resize=(10, 10))
        self.label.config(background="#f7c3c3")
        self.angle = angle
        self.game = game_instance
        self.window.update_idletasks()
        
        # Start movement
        self.move_tongue()
    
    def move_tongue(self):
        """Move the tongue in the direction of rotation and check for collisions."""
        
        def check_collision():
            """Check if the tongue collides with any enemies."""
            for enemy in self.game.enemies[:]:  # Use a copy to avoid modification during iteration
                if abs(self.x - enemy.x) < 25 and abs(self.y - enemy.y) < 25:
                    hit_result = enemy.on_hit()
                    if hit_result:
                        self.destroy()
                    return hit_result
            return False
        
        # Calculate movement direction based on the rotation angle
        corrected_angle = self.angle + 90
        radians = math.radians(corrected_angle)
        dx = math.cos(radians)
        dy = -math.sin(radians)
        
        # Movement speed and steps
        pace = 50
        step_x = dx * pace
        step_y = dy * pace
        self.x += step_x
        self.y += step_y
        
        # Update tongue position
        self.label.place(x=self.x, y=self.y)
        
        # Check for collisions with enemies
        if check_collision():
            return
        
        # Destroy the tongue if it moves out of window
        if not (0 <= self.x <= 800 and 0 <= self.y <= 800):
            self.destroy()
            return
        
        self.window.after(50, self.move_tongue)


class Enemy(GameObject):
    """Base class for all enemy types."""
    
    def __init__(self, window, image_path, resize, enemy_type, game_instance):
        """
        Initialize an enemy.
        
        Args:
            window: Tkinter window
            image_path: Path to the enemy image
            resize: Tuple (width, height) to resize the image
            enemy_type: String identifier for the enemy type
            game_instance: Reference to the Game instance
        """
        # Randomize spawn location
        side = random.choice(["top", "left", "right", "bottom"])
        if side == "top":
            x, y = random.randint(0, 800), -50
        elif side == "left":
            x, y = -50, random.randint(0, 800)
        elif side == "right":
            x, y = 850, random.randint(0, 800)
        else:  # bottom
            x, y = random.randint(0, 800), 850
            
        super().__init__(window, x, y, image_path, resize)
        self.enemy_type = enemy_type
        self.game = game_instance
        self.hit_count = 0
        self.img_index = 0
        
        # Calculate angle to face the frog
        frog_x, frog_y = 400, 400
        dx, dy = frog_x - x, frog_y - y
        angle = math.degrees(math.atan2(-dy, dx)) - 90
        
        # Rotate the image to face the frog
        self.rotate(angle)
        self.label.config(background="#1787c8")
        
        # Start movement
        self.move()
    
    def move(self):
        """Move the enemy towards the frog."""
        if self.game.is_paused.get() or self.game.game_over_bool.get():
            self.window.after(100, self.move)
            return
        
        if not self.label.winfo_exists():
            return
        
        frog_x, frog_y = 400, 400  # Frog's position
        
        # Calculate movement towards the frog
        dx, dy = frog_x - self.x, frog_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Get dynamic speed based on enemy type and current score
        more_speed = float(self.game.score.get()) // 300
        base_speed = self.game.enemy_speed + more_speed
        if self.enemy_type == 'bat':
            pace = base_speed + 4
        else:
            pace = base_speed
            
        step_x = dx / distance * pace
        step_y = dy / distance * pace
        
        # Update position
        self.x += step_x
        self.y += step_y
        self.label.place(x=self.x, y=self.y)
        
        # Check for collision with the frog
        if abs(self.x - frog_x) < 30 and abs(self.y - frog_y) < 30:
            self.destroy()
            self.game.game_over()
            return
        
        # Schedule next movement
        self.window.after(50, self.move)
    
    def on_hit(self):
        """Handle what happens when the enemy is hit by the tongue."""
        self.destroy()
        self.game.enemy_death(self.enemy_type)
        return True
    
    def schedule_spawn(self):
        """Schedule the next spawn of this enemy type."""
        spawn_delays = {'bug': 3000, 'butterfly': 6000, 'bat': 8000}
        timer_id = self.window.after(spawn_delays[self.enemy_type], 
                                    lambda: self.game.spawn_enemy(self.enemy_type))
        self.game.active_timers.append(timer_id)


class Bug(Enemy):
    """Bug enemy type."""
    
    def __init__(self, window, game_instance):
        """Initialize a bug enemy."""
        super().__init__(window, "fly.png", (20, 20), 'bug', game_instance)
        self.schedule_spawn()


class Butterfly(Enemy):
    """Butterfly enemy type that requires multiple hits."""
    
    def __init__(self, window, game_instance):
        """Initialize a butterfly enemy."""
        self.butterfly_imgs = [
            Image.open("butterfly.png").resize((30, 30)),
            Image.open("butterfly2.png").resize((30, 30)),
            Image.open("butterfly3.png").resize((30, 30)),
        ]
        super().__init__(window, "butterfly.png", (30, 30), 'butterfly', game_instance)
        self.schedule_spawn()
    
    def on_hit(self):
        """Handle butterfly being hit, which requires 3 hits to destroy."""
        self.hit_count += 1
        if self.hit_count >= 3:
            self.destroy()
            self.game.enemy_death(self.enemy_type)
            return True
        else:
            # Update butterfly image based on damage
            self.img_index = min(self.hit_count, len(self.butterfly_imgs) - 1)
            new_image = self.butterfly_imgs[self.img_index]
            # Calculate angle to face the frog
            frog_x, frog_y = 400, 400
            dx, dy = frog_x - self.x, frog_y - self.y
            angle = math.degrees(math.atan2(-dy, dx)) - 90
            
            rotated_img = new_image.rotate(angle, expand=True)
            self.img = ImageTk.PhotoImage(rotated_img)
            self.label.config(image=self.img)
            self.label.image = self.img
            return True


class Bat(Enemy):
    """Bat enemy type, faster than other enemies."""
    
    def __init__(self, window, game_instance):
        """Initialize a bat enemy."""
        super().__init__(window, "bat.png", (30, 30), 'bat', game_instance)
        self.schedule_spawn()


class Game:
    """Main game class that manages game state and objects."""
    
    def __init__(self, window):
        """
        Initialize the game.
        
        Args:
            window: Tkinter window
        """
        self.window = window
        self.configure_window()
        
        # Game variables
        self.score = IntVar(value=0)
        self.game_over_bool = BooleanVar(value=False)
        self.is_paused = BooleanVar(value=False)
        self.is_loaded = BooleanVar(value=False)
        self.enemies = []
        self.player_name = ""
        self.name_entry = None
        self.right_button = "Right"
        self.left_button = "Left"
        self.fire_button = "space"
        self.rotation_speed = 10
        self.enemy_speed = 2
        self.bat_spawned = False
        self.active_timers = []
        self.SAVE_FILE = "game_save.pkl"
        
        # Initialize frog
        self.frog = None
        
        # Start with home screen
        self.show_home()
    
    def configure_window(self):
        """Configure the main game window."""
        self.window.geometry("800x800")
        self.window.configure(background="#ffffff")
        self.window.title("F r o g g y  B u l l e t")
    
    def show_home(self):
        """Display the home screen."""
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Title and buttons for home screen
        start_button = Button(self.window, text="Start Game",
                            command=self.start_game, font=("Arial", 16))
        load_button = Button(self.window, text="Load Game",
                           command=self.load_game_settings, font=("Arial", 16))
        leaderboard_button = Button(self.window, text="Leaderboard",
                                  command=self.show_leaderboard, font=("Arial", 16))
        settings_button = Button(self.window, text="Settings",
                               command=self.open_settings, font=("Arial", 16))
        self.name_entry = Entry(self.window, text="", width=30)
        
        # Pack widgets into the window
        title_image = Image.open("title.png")
        title_img = ImageTk.PhotoImage(title_image)
        title_label = Label(self.window, image=title_img)
        title_label.image = title_img
        title_label.pack()
        start_button.pack(pady=20)
        self.name_entry.pack()
        load_button.pack(pady=10)
        leaderboard_button.pack(pady=10)
        settings_button.pack(pady=10)
    
    def start_game(self):
        """Start or restart the game."""
        # Remove the previous enemies
        for enemy in self.enemies:
            enemy.destroy()
        self.enemies = []
        
        # Remove the previous spawning schedules
        for timer_id in self.active_timers:
            self.window.after_cancel(timer_id)
        self.active_timers = []
        
        # Changes that happen only if the game is not loaded
        if not self.is_loaded.get():
            self.score.set(0)
            self.bat_spawned = False
            name = self.name_entry.get()
            self.player_name = name
        
        # Make sure that a name is entered if it's a new game
        if not self.is_loaded.get() and self.player_name == "":
            messagebox.showerror("Missing Name", "Please enter your name in the box")
            return
        
        # Resetting the original states
        self.is_loaded.set(False)
        self.game_over_bool.set(False)
        self.is_paused.set(False)
        
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Background setup
        bg_image = Image.open("background.png")
        bg_img = ImageTk.PhotoImage(bg_image)
        bg_label = Label(self.window, image=bg_img)
        bg_label.image = bg_img
        bg_label.place(relwidth=1, relheight=1)
        
        # Score display
        score_label = Label(self.window, text=f"Score: {self.score.get()}",
                          font=("Arial", 16), background="#ffffff")
        score_label.pack(anchor="nw", padx=10, pady=10)
        
        # Add Save Game button
        save_button = Button(self.window, text="Save Game",
                           command=self.save_game_settings, font=("Arial", 10))
        save_button.pack(anchor="nw", padx=10)
        
        # Create the frog
        self.frog = Frog(self.window, self)
        
        # Set up key bindings
        self.window.bind(f"<{self.left_button}>", self.frog.rotate_left)
        self.window.bind(f"<{self.right_button}>", self.frog.rotate_right)
        self.window.bind(f"<{self.fire_button}>", self.frog.fire)
        
        # Add the pause button and display it
        pause_button = Button(self.window, text="Pause",
                            command=self.pause_toggle, font=("Arial", 10))
        pause_button.pack(anchor="nw", padx=10)
        
        # Bind boss key (Ctrl+B)
        self.window.bind('<Control-b>', self.boss_key)
        
        # Set up cheat code functionality
        self.setup_cheat_system()
        
        # Start spawning enemies
        self.spawn_enemy('bug')
        self.spawn_enemy('butterfly')
    
    def pause_toggle(self):
        """Toggle the paused state of the game."""
        self.is_paused.set(not self.is_paused.get())
        
        for widget in self.window.winfo_children():
            if hasattr(widget, 'cget') and widget.cget('text') == "Pause" or widget.cget('text') == "Unpause":
                widget.config(text="Unpause" if self.is_paused.get() else "Pause")
        
        if self.is_paused.get():
            for timer_id in self.active_timers:
                self.window.after_cancel(timer_id)
            self.active_timers = []
        else:
            self.spawn_enemy('bug')
            self.spawn_enemy('butterfly')
            if self.bat_spawned:
                self.spawn_enemy('bat')
    
    def boss_key(self, event=None):
        """Toggle a fake workspace window when boss key is pressed."""
        mock_window = Toplevel(self.window)
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
        
        # Minimize the game window and pause the game
        self.window.iconify()
        self.pause_toggle()
    
    def setup_cheat_system(self):
        """Set up the cheat code input system."""
        # Create cheat code entry field and button
        self.cheat_entry = Entry(self.window, text="", width=20)
        self.window.bind("<Control-c>", self.show_input)
        self.submit_button = Button(self.window, text="Enter",
                                 command=self.submit_key, font=("Arial", 8))
    
    def show_input(self, event=None):
        """Display the input field and button for entering cheat codes."""
        self.cheat_entry.pack()
        self.submit_button.pack()
        self.cheat_entry.focus_set()
    
    def submit_key(self):
        """Handle the submission of cheat codes."""
        # Retrieve and process the cheat code input
        cheat_code = self.cheat_entry.get().strip().lower()
        
        if cheat_code == "vanish":
            # Remove all enemies
            for enemy in self.enemies[:]:
                enemy.destroy()
            self.enemies.clear()
        elif cheat_code == "snail":
            # Temporarily reduce enemy speed
            original_speed = self.enemy_speed
            self.enemy_speed = 1
            
            def reset_speed():
                """Restore the original speed of the enemies."""
                self.enemy_speed = original_speed
            
            self.window.after(10000, reset_speed)
        elif cheat_code == "oman":
            # Increase score
            new_score = self.score.get() + 100
            self.score.set(new_score)
            
            # Update the score label
            for widget in self.window.winfo_children():
                if hasattr(widget, 'cget') and widget.cget('text').startswith("Score:"):
                    widget.config(text=f"Score: {new_score}")
        else:
            # Inform the user of an invalid cheat code
            messagebox.showinfo("Invalid Cheat Code",
                              "The cheat code you entered isn't recognized.")
        
        # Clear and hide the cheat input field and button
        self.cheat_entry.delete(0, END)
        self.cheat_entry.pack_forget()
        self.submit_button.pack_forget()
    
    def spawn_enemy(self, enemy_type):
        """Spawn an enemy of the given type."""
        if not self.is_paused.get() or not self.game_over_bool.get():
            # Create the appropriate enemy type
            if enemy_type == 'bug':
                enemy = Bug(self.window, self)
            elif enemy_type == 'butterfly':
                enemy = Butterfly(self.window, self)
            elif enemy_type == 'bat':
                enemy = Bat(self.window, self)
            
            # Add enemy to the list
            self.enemies.append(enemy)
    
    def enemy_death(self, enemy_type):
        """Handle the scoring when an enemy is defeated."""
        points = {'bug': 10, 'butterfly': 20, 'bat': 20}
        self.score.set(self.score.get() + points.get(enemy_type, 0))
        
        # Update the score label
        for widget in self.window.winfo_children():
            if hasattr(widget, 'cget') and widget.cget('text').startswith("Score:"):
                widget.config(text=f"Score: {self.score.get()}")
        
        # The bat will be spawned after score 200
        if self.score.get() >= 200 and not self.bat_spawned:
            self.bat_spawned = True
            self.spawn_enemy('bat')
    
    def game_over(self):
        """End the game and show the game over screen."""
        # Set the game-over flag to True
        self.game_over_bool.set(True)
        
        # Delete any saved game data
        self.delete_saved_game()
        
        # Remove the previous enemies
        for enemy in self.enemies:
            enemy.destroy()
        self.enemies = []
        
        # Remove the previous spawning schedules
        for timer_id in self.active_timers:
            self.window.after_cancel(timer_id)
        self.active_timers = []
        
        # Clear all widgets from the main game window
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Append the player's name and score to the leaderboard file
        with open("leaderboard.txt", "a") as leaderboard_dict:
            leaderboard_dict.write(f"{self.player_name},{self.score.get()}\n")
        
        # Create and configure the Leaderboard button
        leaderboard_button = Button(
            self.window,
            text="Leaderboard",
            command=self.show_leaderboard,
            font=("Arial", 16)
        )
        
        # Create and configure the Home button
        home_button = Button(
            self.window,
            text="Back to Home",
            command=self.show_home,
            font=("Arial", 16)
        )
        
        # Display the player's final score
        score_label = Label(
            self.window,
            text=f"Your Score: {self.score.get()}",
            font=("Arial", 16),
            background="#ffffff"
        )
        
        # Load and display the "Game Over" image
        over_image = Image.open("over.png")
        over_img = ImageTk.PhotoImage(over_image)
        over_label = Label(self.window, image=over_img)
        over_label.image = over_img
        
        # Pack the widgets on the "Game Over" screen
        over_label.pack()
        score_label.pack(pady=10)
        leaderboard_button.pack(pady=10)
        home_button.pack(pady=20)
    
    def show_leaderboard(self):
        """Display the leaderboard screen."""
        # Clear all widgets from the main window
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Create and configure the leaderboard title
        title = Label(
            self.window,
            text="Leaderboard",
            font=("Arial", 16),
            background="#ffffff"
        )
        
        # Create the "Back to Home" button for navigation
        home_button = Button(
            self.window,
            text="Back to Home",
            command=self.show_home,
            font=("Arial", 16)
        )
        
        # Initialize a list to store scores from the leaderboard file
        scores = []
        
        # Read and parse the leaderboard file
        with open("leaderboard.txt", "r") as file:
            for line in file:
                player_name, score = line.strip().split(',')
                scores.append((player_name, int(score)))
        
        # Sort scores in descending order
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Display the leaderboard title at the top
        title.pack(anchor="center", pady=10)
        
        # Display the top 5 scores or fewer if there are less than 5 entries
        for i in range(min(5, len(scores))):
            player_name, score = scores[i]
            rank_label = Label(
                self.window,
                text=f"{i+1}. {player_name}: {score}",
                font=("Arial", 12),
                background="#ffffff"
            )
            rank_label.pack(anchor="center", pady=10)
        
        # Add the "Back to Home" button at the bottom
        home_button.pack(pady=20)
    
    def open_settings(self):
        """Display the settings screen."""
        # Clear all widgets from the main window
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Title label
        title = Label(self.window, text="Settings",
                    font=("Arial", 16), background="#ffffff")
        
        # "Back to Home" button for navigation
        home_button = Button(self.window,
                           text="Back to Home",
                           command=self.show_home,
                           font=("Arial", 16))
        
        # Labels to display current key bindings
        left_label = Label(self.window,
                         text=f"Left currently bound to: {self.left_button}",
                         font=("Arial", 16), background="#ffffff")
        right_label = Label(self.window,
                          text=f"Right currently bound to: {self.right_button}",
                          font=("Arial", 16), background="#ffffff")
        fire_label = Label(self.window,
                         text=f"Fire currently bound to: {self.fire_button}",
                         font=("Arial", 16), background="#ffffff")
        
        # Define nested functions for key bindings
        def set_left_binding(event):
            """Bind the 'Left' key action to a new key."""
            self.left_button = event.keysym
            left_label.config(text=f"Left now bound to: {self.left_button}")
            self.window.unbind("<KeyPress>")
        
        def set_right_binding(event):
            """Bind the 'Right' key action to a new key."""
            self.right_button = event.keysym
            right_label.config(text=f"Right now bound to: {self.right_button}")
            self.window.unbind("<KeyPress>")
        
        def set_fire_binding(event):
            """Bind the 'Fire' key action to a new key."""
            self.fire_button = event.keysym
            fire_label.config(text=f"Fire now bound to: {self.fire_button}")
            self.window.unbind("<KeyPress>")
        
        # Buttons to change key bindings
        change_left = Button(self.window,
                           text="Press any key for Left",
                           font=("Arial", 16),
                           command=lambda: self.window.bind("<KeyPress>", set_left_binding))
        change_right = Button(self.window,
                            text="Press any key for Right",
                            font=("Arial", 16),
                            command=lambda: self.window.bind("<KeyPress>", set_right_binding))
        change_fire = Button(self.window,
                           text="Press any key for Fire",
                           font=("Arial", 16),
                           command=lambda: self.window.bind("<KeyPress>", set_fire_binding))
        
        # Function to change the rotation speed
        def change_rotation_func():
            """Change the rotation speed of the frog."""
            self.rotation_speed = int(change_rotation.get())
            rotation_label.config(text=f"Rotation Speed: {self.rotation_speed}")
            if self.frog:
                self.frog.rotation_speed = self.rotation_speed
        
        # Button and spinbox for adjusting rotation speed
        change_rotation_button = Button(self.window,
                                      text="Change the rotation speed",
                                      font=("Arial", 16),
                                      command=change_rotation_func)
        change_rotation = Spinbox(self.window, from_=1, to=20,
                                state="readonly", font=("Arial", 14), width=5)
        change_rotation.delete(0, "end")
        change_rotation.insert(0, self.rotation_speed)
        
        # Label to display the current rotation speed
        rotation_label = Label(self.window, text=f"Rotation Speed: {self.rotation_speed}",
                             font=("Arial", 16), background="#ffffff")
        
        # Pack UI elements
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

    def save_game_settings(self):
        """Save the current game settings and progress to a file."""
        # Create a dictionary containing all settings and game progress to save
        settings = {
            "score": self.score.get(),
            "rotation_angle": self.frog.rotation_angle if self.frog else 0,
            "player_name": self.player_name,
            "right_button": self.right_button,
            "left_button": self.left_button,
            "fire_button": self.fire_button,
            "rotation_speed": self.rotation_speed,
            "enemy_speed": self.enemy_speed,
        }
        
        # Save the settings to a binary file using pickle
        with open(self.SAVE_FILE, "wb") as file:
            pickle.dump(settings, file)
        
        # Show a confirmation message to the user
        messagebox.showinfo("Game Saved", "Your game has been saved.")
    
    def load_game_settings(self):
        """Load saved game settings and progress from a file."""
        # Check if the save file exists
        if os.path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "rb") as file:
                settings = pickle.load(file)  # Deserialize the saved settings
            
            # Apply loaded settings to the game variables
            self.score.set(settings["score"])
            rotation_angle = settings["rotation_angle"]
            self.player_name = settings["player_name"]
            self.right_button = settings["right_button"]
            self.left_button = settings["left_button"]
            self.fire_button = settings["fire_button"]
            self.rotation_speed = settings["rotation_speed"]
            self.enemy_speed = settings["enemy_speed"]
            
            # Set the loaded flag to True
            self.is_loaded.set(True)
            
            # Start the game with the loaded settings
            self.start_game()
            
            # Update frog's rotation angle if a frog exists
            if self.frog:
                self.frog.rotation_angle = rotation_angle
                self.frog.rotate(rotation_angle)
            
            # Notify the user that the game has been loaded
            messagebox.showinfo("Game Loaded", "Your game has been loaded.")
        else:
            messagebox.showinfo("No Saved Data", "No saved game data found.")
    
    def delete_saved_game(self):
        """Delete saved game settings."""
        if os.path.exists(self.SAVE_FILE):
            os.remove(self.SAVE_FILE)


def main():
    """Main function to start the game."""
    window = Tk()
    game = Game(window)
    window.mainloop()


if __name__ == "__main__":
    main()
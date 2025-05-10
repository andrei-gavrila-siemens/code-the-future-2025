import RPi.GPIO as GPIO
import time

class JoystickController:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        GPIO.setmode(GPIO.BCM)
        self.buttons = {
            "A": 6,    
            "B": 5,    
            "C": 22,  
            "D": 27,   
            "E": 17,   
            "F": 4     
        }
        for name, pin in self.buttons.items():
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            except Exception as e:
                print(f"Error setting up GPIO pin {pin} for button {name}: {e}")

        self.selected_cluster_color = None
        self.current_color_index = 0
        self.move_step = 5 
        self.last_button_state = {name: GPIO.HIGH for name in self.buttons}
        self.debounce_time = 0.2  
        self.last_press_time = {name: 0 for name in self.buttons}
        self.cluster_offsets = []

        print("Joystick controller initialized")

    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            GPIO.cleanup()
            print("GPIO cleaned up")
        except Exception as e:
            print(f"Error during GPIO cleanup: {e}")

    def update(self, atoms, settings):
        """Read button states and update particle positions.

        Args:
            atoms: List of atoms [x, y, vx, vy, color].
            settings: Simulation settings dictionary with 'colors' and 'color_to_index'.

        Returns:
            selected_cluster_color: The currently selected cluster color or None.
        """
        if not atoms:
            print("No atoms to update in joystick controller")
            return self.selected_cluster_color

        
        for name, pin in self.buttons.items():
            try:
                current_state = GPIO.input(pin)
            except Exception as e:
                print(f"Error reading GPIO pin {pin} for button {name}: {e}")
                continue

            current_time = time.time()

           
            if (current_state == GPIO.LOW and 
                self.last_button_state[name] == GPIO.HIGH and 
                current_time - self.last_press_time[name] > self.debounce_time):
                self.last_press_time[name] = current_time
                self.handle_button_press(name, atoms, settings)

            self.last_button_state[name] = current_state

        return self.selected_cluster_color

    def handle_button_press(self, button, atoms, settings):
        """Handle a button press event.

        Args:
            button: Name of the button ('A', 'B', 'C', 'D', 'E', 'F').
            atoms: List of atoms.
            settings: Simulation settings dictionary.
        """
        print(f"Button {button} pressed")

        if button == "A" and self.selected_cluster_color is not None: 
            for a in atoms:
                if a[4] == self.selected_cluster_color:
                    new_y = a[1] - self.move_step
                    if 0 <= new_y <= self.screen_height: 
                        a[1] = new_y
                        a[2] = 0  
                        a[3] = 0
        elif button == "B" and self.selected_cluster_color is not None: 
            for a in atoms:
                if a[4] == self.selected_cluster_color:
                    new_y = a[1] + self.move_step
                    if 0 <= new_y <= self.screen_height:
                        a[1] = new_y
                        a[2] = 0
                        a[3] = 0
        elif button == "C" and self.selected_cluster_color is not None: 
            for a in atoms:
                if a[4] == self.selected_cluster_color:
                    new_x = a[0] - self.move_step
                    if 0 <= new_x <= self.screen_width:
                        a[0] = new_x
                        a[2] = 0
                        a[3] = 0
        elif button == "D": 
            if settings['colors']:
                self.current_color_index = (self.current_color_index + 1) % len(settings['colors'])
                self.selected_cluster_color = settings['colors'][self.current_color_index]
                print(f"Selected cluster with color {self.selected_cluster_color}")
               
                cluster_atoms = [a for a in atoms if a[4] == self.selected_cluster_color]
                if cluster_atoms:
                    centroid_x = sum(a[0] for a in cluster_atoms) / len(cluster_atoms)
                    centroid_y = sum(a[1] for a in cluster_atoms) / len(cluster_atoms)
                    self.cluster_offsets = [(a[0] - centroid_x, a[1] - centroid_y) for a in cluster_atoms]
                else:
                    self.cluster_offsets = []
                    print("No atoms found for selected color")


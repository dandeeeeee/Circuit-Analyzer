
import pyray as rl
import tkinter as tk
from tkinter import colorchooser

selected_color = rl.Color(255, 0, 0, 255)  

def show_color_picker():
    global selected_color

    # Tkinter window for the color picker
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open the color chooser dialog and get the selected color
    color = colorchooser.askcolor()[1]  # Returns a tuple (RGB, hex)
    if color:
        # Convert hex to RGB
        selected_color = rl.Color(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)
        print(f"Selected color: {selected_color.r}, {selected_color.g}, {selected_color.b}")

    root.quit()  # Close the Tkinter main loop

def main():
    global selected_color

    # Initialize Raylib window
    rl.init_window(800, 600, "Raylib with Tkinter Color Picker")

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.DARKGRAY)

        # Draw the button-like rectangle that when clicked will trigger the Tkinter color picker
        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            # Check if the mouse click is within the button area
            if 50 < mouse_x < 350 and 100 < mouse_y < 140:
                # Call the color picker without threading (runs in the main loop)
                show_color_picker()

        # Draw the button with the selected color
        rl.draw_rectangle(50, 100, 300, 40, selected_color)  # Use selected_color for the button background
        rl.draw_text("Choose Color", 150, 110, 20, rl.WHITE)

        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
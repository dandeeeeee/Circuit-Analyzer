from pyray import *
import threading
from fractions import Fraction


# ONE BACKSPACE     - FLOW
# TWO BACKSPACE     - FUNCTIONS
# THREE BACKSPACE   - CLASSES


# GLOBALS
global log
global RM

# CONSTANTS
APP_WIDTH = 1920 # 1920
APP_HEIGHT = 1080  # 1080

MATTE_BLACK = Color(51, 51, 51, 255)
GOLDEN_YELLOW = Color(255, 223, 0, 255)

TEXTURE = 0
IMAGE = 1
FONT = 2
SOUND = 3
MUSIC = 4



# INTERFACES
class Circle:

    def __init__(self, pos: Vector2, rad: float):

        self.position = pos
        self.radius = rad



# MAIN CLASSES
class TraceLog:

    _instance = None
    _lock = threading.Lock()

    colors = {
        TraceLogLevel.LOG_INFO: "\033[34m",         # Blue
        TraceLogLevel.LOG_WARNING: "\033[33m",      # Yellow
        TraceLogLevel.LOG_ERROR: "\033[31m",        # Red
    }

    def __new__(cls, *args, **kwargs):

        with cls._lock: 

            if not cls._instance:
                cls._instance = super().__new__(cls)

        return cls._instance
    

    def __call__(self, level: int, text: str):

        with self._lock: 

            color = self.colors.get(level, "\033[37m")
            reset_color = "\033[0m"

            level_names = {
                TraceLogLevel.LOG_INFO: "[INFO]",
                TraceLogLevel.LOG_WARNING: "[WARNING]",
                TraceLogLevel.LOG_ERROR: "[ERROR]",
            }

            print(f"{color}{level_names.get(level, '[UNKNOWN]')}: {text}{reset_color}")



class ResourceManager:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "resources"):
            self.resources = {}

    def load(self, ID: str, filepath: str, type: int):
        enumerate_resources = {
            0: load_texture,
            1: load_image,
            2: load_font_ex,
            3: load_sound,
            4: load_music_stream,
        }

        if type in enumerate_resources:
            if type == FONT: # font loading exception
                self.resources[ID] = enumerate_resources[type](filepath, 320, None, 0)
            else: 
                self.resources[ID] = enumerate_resources[type](filepath)
        else:
            log(TraceLogLevel.LOG_ERROR, "Unknown resource type")

    def get(self, ID: str):
        return self.resources.get(ID, None)


class Button:
    
    def __init__(self, rec: Rectangle, color: Color, text=None, font_size=50, icon=None, roundness=None):

        self.rectangle = rec
        self.color = color
        self.text = text
        self.font = RM.get("mainfont")
        self.font_size = font_size
        self.icon = icon
        self.roundness = roundness

    def render(self):

        if self.roundness:
            draw_rectangle_rounded(self.rectangle, self.roundness, 0, self.color)
        else:
            draw_rectangle_rec(self.rectangle, self.color)
        
        if self.text and self.font:
            self.draw_text_centered(self.text, self.font, self.font_size)

    def draw_text_centered(self, text, font, font_size):

        text_width = measure_text_ex(font, text, font_size, 0).x
        text_height = font_size 

        x = self.rectangle.x + (self.rectangle.width - text_width) / 2
        y = self.rectangle.y + (self.rectangle.height - text_height) / 2

        draw_text_ex(self.font, text, Vector2(x, y), font_size, 0, DARKGRAY if not self.is_hovered() else GOLDEN_YELLOW)


    def is_hovered(self) -> bool:

        mouse = get_mouse_position()
        if check_collision_point_rec(mouse, self.rectangle):
            if self.roundness:
                draw_rectangle_rounded_lines(self.rectangle, self.roundness, 0, 10, GOLDEN_YELLOW)
            else:
                draw_rectangle_lines_ex(self.rectangle, 10, GOLDEN_YELLOW)
            return True
        return False


    def is_clicked(self) -> bool:

        if self.is_hovered() and is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
            return True
        return False


    def set_color(self, color: Color):

        self.color = color



class Canvas:

    
    def __init__(self):

        self.buttons = {
            "PENCIL": Button(Rectangle((APP_WIDTH / 2) - 50, APP_HEIGHT - 125, 100, 100), WHITE, text="PENCIL", font_size=20),
        }
        self.on_hand = None  # Active tool (e.g., Pencil)

        # Camera2D setup for grid panning and zooming
        self.camera = Camera2D(
            Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),  # target
            Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),  # offset
            0,                                       # rotation
            1.0                                      # zoom
        )

        # Mouse panning state
        self.is_panning = False
        self.last_mouse_position = Vector2(0, 0)

    def handle_camera_input(self):
        """Handle Camera2D input for zooming and panning."""
        # Zoom with the mouse wheel
        mouse_wheel = get_mouse_wheel_move()
        if mouse_wheel != 0:
            self.camera.zoom += mouse_wheel * 0.25  # Adjust zoom speed
            self.camera.zoom = max(0.1, min(self.camera.zoom, 10.0))  # Clamp zoom level

        # Pan with middle mouse button
        if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_MIDDLE):
            self.is_panning = True
            self.last_mouse_position = get_mouse_position()

        if self.is_panning:
            if is_mouse_button_down(MouseButton.MOUSE_BUTTON_MIDDLE):
                current_mouse_position = get_mouse_position()
                delta = Vector2(
                    current_mouse_position.x - self.last_mouse_position.x,
                    current_mouse_position.y - self.last_mouse_position.y,
                )
                self.camera.target.x -= delta.x / self.camera.zoom
                self.camera.target.y -= delta.y / self.camera.zoom
                self.last_mouse_position = current_mouse_position
            else:
                self.is_panning = False

    def update(self):
        # Handle camera input
        self.handle_camera_input()

        # Render buttons and handle clicks
        for key, button in self.buttons.items():
            button.render()
            if button.is_clicked():
                match key:
                    case "PENCIL":
                        self.on_hand = self.Pencil(self.camera)  # Pass camera to Pencil
                    case _:
                        print(f"Unknown button '{key}' clicked.")

        # Start drawing within the camera context
        begin_mode_2d(self.camera)
        if self.on_hand:
            self.on_hand.render()
        if is_key_pressed(KeyboardKey.KEY_ENTER):
            take_screenshot("canvas.png")
        end_mode_2d()

        return "canvas"
    

    class Pencil:


        def __init__(self, camera, stroke_color=GOLDEN_YELLOW, stroke_width=8, stroke_threshold=1):

            self.camera = camera
            self.stroke_color = stroke_color
            self.stroke_width = stroke_width
            self.stroke_threshold = stroke_threshold
            self.current_stroke = []  # Temporary stroke being drawn
            self.strokes = []  # All completed strokes

        def render(self):
            # Undo last stroke
            if is_key_pressed(KeyboardKey.KEY_Z) and is_key_down(KeyboardKey.KEY_LEFT_CONTROL):
                if self.strokes:
                    self.strokes.pop()

            # Clear all strokes
            if is_key_pressed(KeyboardKey.KEY_R):
                self.strokes.clear()

            # Start a new stroke
            if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                self.current_stroke.clear()

            # Add points to the current stroke
            if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
                current_mouse_position = get_screen_to_world_2d(get_mouse_position(), self.camera)
                if not self.current_stroke or vector_2distance(self.current_stroke[-1][0], current_mouse_position) > self.stroke_threshold:
                    self.current_stroke.append([current_mouse_position, Circle(current_mouse_position, self.stroke_width / 2)])

            # Finalize the stroke
            if is_mouse_button_released(MouseButton.MOUSE_BUTTON_LEFT) and self.current_stroke:
                self.strokes.append(self.current_stroke[:])
                self.current_stroke.clear()

            # Render completed strokes
            for stroke in self.strokes:
                for i in range(1, len(stroke)):
                    draw_line_ex(stroke[i - 1][0], stroke[i][0], self.stroke_width, self.stroke_color)
                    draw_circle_v(stroke[i][1].position, stroke[i][1].radius, self.stroke_color)

            # Render the current stroke being drawn
            for i in range(1, len(self.current_stroke)):
                draw_line_ex(self.current_stroke[i - 1][0], self.current_stroke[i][0], self.stroke_width, self.stroke_color)
                draw_circle_v(self.current_stroke[i][1].position, self.current_stroke[i][1].radius, self.stroke_color)



    def toggle_menu(self):

        SLIDING_ANIMATION_SPEED = 1500
        MENU_INITIAL_POSITION = -300
        
        if self.menu_open:
            if self.menu_horizontal_position <= 0:
                self.menu_horizontal_position += int(SLIDING_ANIMATION_SPEED * get_frame_time())
                if self.menu_horizontal_position > 0:
                    self.menu_horizontal_position = 0
            draw_rectangle(self.menu_horizontal_position, 0, 300, 450, GRAY)

        else:
            if self.menu_horizontal_position >= MENU_INITIAL_POSITION:
                self.menu_horizontal_position -= int(SLIDING_ANIMATION_SPEED * get_frame_time())
                if self.menu_horizontal_position < MENU_INITIAL_POSITION:
                    self.menu_horizontal_position = MENU_INITIAL_POSITION
            draw_rectangle(self.menu_horizontal_position, 0, 300, 450, GRAY)

    

    def toggle_menu(self):

        SLIDING_ANIMATION_SPEED = 1500
        MENU_INITIAL_POSITION = -300
        
        if self.menu_open:
            if self.menu_horizontal_position <= 0:
                self.menu_horizontal_position += int(SLIDING_ANIMATION_SPEED * get_frame_time())
                if self.menu_horizontal_position > 0:
                    self.menu_horizontal_position = 0
            draw_rectangle(self.menu_horizontal_position, 0, 300, 450, GRAY)

        else:
            if self.menu_horizontal_position >= MENU_INITIAL_POSITION:
                self.menu_horizontal_position -= int(SLIDING_ANIMATION_SPEED * get_frame_time())
                if self.menu_horizontal_position < MENU_INITIAL_POSITION:
                    self.menu_horizontal_position = MENU_INITIAL_POSITION
            draw_rectangle(self.menu_horizontal_position, 0, 300, 450, GRAY)
            


def draw_centered_text_ex(text, font, font_size, y_position, color=RAYWHITE):
    # Measure the width of the text with the specified font and font size
    text_width = measure_text_ex(font, text, font_size, 1).x

    # Calculate the horizontal center position
    x_position = (APP_WIDTH - text_width) // 2

    # Draw the text at the calculated position using draw_text_ex
    draw_text_ex(font, text, Vector2(x_position, y_position), font_size, 0, color)



class MessageBox: # TODO: COMBINE MESSAGEBOX AND BUTTON CLASS

    def __init__(self, rect: Rectangle, font, base_font_size=250, min_font_size=10, roundness=0.25, background_color=GRAY, hovered_color=LIGHTGRAY, text_color=RAYWHITE):
        
        self.rect = rect
        self.font = font
        self.text = ""
        self.is_focused = False
        self.base_font_size = base_font_size
        self.min_font_size = min_font_size
        self.roundness = roundness  # Roundness of the rectangle edges (0.0 to 1.0)
        self.backrgound_color = background_color
        self.hovered_color = hovered_color
        self.text_color = text_color


    def handle_input(self):
        """Handle keyboard input when the message box is focused."""
        if self.is_focused:
            key = get_key_pressed()
            while key > 0:  # Process each key press
                if key == KeyboardKey.KEY_BACKSPACE and len(self.text) > 0:
                    self.text = self.text[:-1]
                elif key == KeyboardKey.KEY_MINUS:  # Allow the '-' character for negative numbers
                    self.text += "-"
                elif key == KeyboardKey.KEY_SLASH:  # Allow the '/' character for fractions
                    self.text += "/"
                elif key == KeyboardKey.KEY_PERIOD:  # Allow the '.' character for floats
                    self.text += "."
                elif 48 <= key <= 57:  # Allow numeric input (keys 0-9)
                    self.text += chr(key)
                key = get_key_pressed()


    def validate_input(self):
        """
        Validate the text as either a valid fraction or float.
        Returns True if valid, False otherwise.
        """
        if not self.text:
            return False
        try:
            # Try to parse as a fraction or float
            float(Fraction(self.text))
            return True
        except ValueError:
            return False


    def get_value(self):
        """
        Return the numeric value of the input as a float.
        If the input is invalid, raise a ValueError.
        """
        if not self.validate_input():
            raise ValueError(f"Invalid input: '{self.text}'")
        return float(Fraction(self.text))


    def fit_text_size(self) -> int:
        """Adjust font size to fit the text inside the rectangle."""
        font_size = self.base_font_size
        text_width = measure_text_ex(self.font, self.text, font_size, 0).x

        while text_width > self.rect.width - 10 and font_size > self.min_font_size:
            font_size -= 1
            text_width = measure_text_ex(self.font, self.text, font_size, 0).x

        return font_size


    def render(self):
        """Render the message box with its current text."""
        # Draw the rounded rectangle
        draw_rectangle_rounded(self.rect, self.roundness, 10, self.backrgound_color if not self.is_focused else self.hovered_color)

        # Calculate text position and size
        font_size = self.fit_text_size()
        text_width = measure_text_ex(self.font, self.text, font_size, 0).x
        text_height = measure_text_ex(self.font, self.text, font_size, 0).y
        text_x = self.rect.x + (self.rect.width - text_width) / 2
        text_y = self.rect.y + (self.rect.height - text_height) / 2

        # Draw the text
        draw_text_ex(self.font, self.text, Vector2(text_x, text_y), font_size, 0, self.text_color)


    def check_focus(self):
        """Check if the message box is clicked and toggle focus."""
        if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
            mouse_pos = get_mouse_position()
            if check_collision_point_rec(mouse_pos, self.rect):
                self.is_focused = True
            else:
                self.is_focused = False


    def set_color(self, background_color=GRAY, hovered_color=LIGHTGRAY, text_color=RAYWHITE):
        """Set the colors for the message box."""
        self.backrgound_color = background_color
        self.hovered_color = hovered_color
        self.text_color = text_color



class Notifier:


    def __init__(self, message: str, rec=Rectangle(100, 50, APP_WIDTH - 200, APP_HEIGHT - 100)):

        self.font = RM.get("mainfont")
        self.message = message
        self.rectangle = rec
        self.button = {}
        self.button["OK"] = Button(Rectangle(325, 340, 150, 50), GRAY, text="CONTINUE", font_size=25)

    
    def render(self):

        # draw_rectangle_rec(Rectangle(100, 50, APP_WIDTH - 200, APP_HEIGHT - 100), GRAY)
        draw_rectangle_rounded(self.rectangle, 0.08, 10, GRAY)
        draw_centered_text_ex(self.message, self.font, 30, 150, RAYWHITE)
        self.button["OK"].render()


class PopupWindow:

    def __init__(self, message, font, rect=Rectangle(100, 100, APP_WIDTH - 200, APP_HEIGHT - 200), font_size=40, line_spacing=1.5):
        self.message = message
        self.font = font
        self.rect = rect
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.is_visible = False
        self.scroll_offset = 0  # Tracks how far the content is scrolled
        self.scroll_speed = 30  # Controls scroll sensitivity
        self.close_button = Button(Rectangle(rect.x + rect.width - 250, rect.y + rect.height - 125, 200, 80), color=GRAY, text="Close", font_size=40)
    
    def show(self, message):

        """Display the popup window with the given message."""
        self.message = message
        self.is_visible = True
        self.scroll_offset = 0  # Reset scroll offset when a new message is shown

    def render(self):
        """Render the popup window if it is visible."""
        if not self.is_visible:
            return

        # Draw the popup background
        draw_rectangle_rec(self.rect, DARKGRAY)
        draw_rectangle_lines_ex(self.rect, 5, RAYWHITE)

        # Split the message into lines
        lines = self.message.split("\n")
        line_height = int(self.font_size * self.line_spacing)
        total_content_height = len(lines) * line_height
        visible_content_height = self.rect.height - 40  # Account for padding
        max_scroll = max(0, total_content_height - visible_content_height)

        # Adjust scroll offset with mouse wheel
        self.scroll_offset += get_mouse_wheel_move() * -self.scroll_speed
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        # Draw the content inside the popup with scrolling
        text_start_y = self.rect.y + 20 - self.scroll_offset
        text_x = self.rect.x + 20

        # Calculate visible line range to avoid rendering extra lines
        start_line = max(0, self.scroll_offset // line_height)  # First visible line
        visible_lines = visible_content_height // line_height   # Number of fully visible lines
        end_line = min(len(lines), start_line + visible_lines)  # Last fully visible line

        for i in range(int(start_line),int(end_line)):
            line_y = text_start_y + i * line_height
            if self.rect.y <= line_y < self.rect.y + self.rect.height:  # Only render visible lines
                draw_text_ex(self.font, lines[i], Vector2(text_x, line_y), self.font_size, 2, RAYWHITE)

        # Draw the scrollbar
        if total_content_height > visible_content_height:
            scrollbar_height = visible_content_height * (visible_content_height / total_content_height)
            scrollbar_y = self.rect.y + 20 + (self.scroll_offset / total_content_height) * (visible_content_height - scrollbar_height)
            draw_rectangle(int(self.rect.x + self.rect.width - 20), int(scrollbar_y), 10, int(scrollbar_height), LIGHTGRAY)

        # Render the Close button
        self.close_button.render()
        if self.close_button.is_clicked():
            self.is_visible = False





class Calculator:

    def __init__(self):
        # Message boxes for matrix size input
        self.column_box = MessageBox(Rectangle(475, 350, 350, 350), RM.get("mainfont"))
        self.row_box = MessageBox(Rectangle(1100, 350, 350, 350), RM.get("mainfont"))

        # Buttons
        self.buttons = {
            "NEXT": Button(Rectangle(810, 800, 300, 100), GRAY, text="NEXT", font_size=50),
            "SOLVE": Button(Rectangle(810, 950, 300, 100), GRAY, text="SOLVE", font_size=50)
        }

        # Matrix message boxes
        self.matrix_boxes = []  # List of message boxes for matrix input
        self.matrix_size = 0  # Current matrix size (determined by row/column input)

        # Camera2D setup for grid panning and zooming
        self.camera = Camera2D(
        Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),        # target
        Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),        # offset
        0,                                             # rotation                   
        5.0)                                           # zoom

        # Mouse panning state
        self.is_panning = False
        self.last_mouse_position = Vector2(0, 0)

        # self.show_answer = False

        self.popup = PopupWindow("", RM.get("mainfont"))

        self.solution = ""


    def collect_matrix_input(self):
        """Collect matrix input from the message boxes and format it for computation."""
        matrix = []
        try:
            for row_boxes in self.matrix_boxes:
                row = []
                for box in row_boxes:
                    row.append(box.get_value())  # Use get_value to handle fractions and floats
                matrix.append(row)

            # Ensure augmented matrix size (n x n+1)
            if len(matrix) != self.matrix_size or any(len(row) != self.matrix_size + 1 for row in matrix):
                raise ValueError("Invalid matrix size! Ensure it's n x n+1.")

            return matrix

        except ValueError as e:
            log(TraceLogLevel.LOG_WARNING, f"Input Error: {str(e)}")
            return None


    def generate_matrix_boxes(self):
        """Generate a grid of message boxes for matrix input based on matrix size."""
        self.matrix_boxes.clear()  # Clear any existing matrix boxes

        # Fixed cell size for simplicity
        cell_size = 50
        padding = 5  # Space between cells

        # Calculate starting position for the grid
        grid_width = (self.matrix_size + 1) * (cell_size + padding) - padding  # Include the extra column
        grid_height = self.matrix_size * (cell_size + padding) - padding
        start_x = (APP_WIDTH - grid_width) // 2
        start_y = (APP_HEIGHT - grid_height) // 2

        for i in range(self.matrix_size):
            row_boxes = []
            for j in range(self.matrix_size + 1):  # Add the extra column for augmented matrix
                x = start_x + j * (cell_size + padding)
                y = start_y + i * (cell_size + padding)
                rect = Rectangle(x, y, cell_size, cell_size)
                row_boxes.append(MessageBox(rect, RM.get("mainfont"), base_font_size=30, min_font_size=10))
            self.matrix_boxes.append(row_boxes)


    def render_matrix_boxes(self):
        """Render all matrix message boxes and handle their interactions."""
        # Dimensions and position calculations
        if not self.matrix_boxes:
            return

        # Determine overall matrix dimensions
        num_rows = len(self.matrix_boxes)
        num_cols = len(self.matrix_boxes[0])
        cell_width = self.matrix_boxes[0][0].rect.width
        cell_height = self.matrix_boxes[0][0].rect.height
        padding = 5

        # Calculate the bounds of the matrix grid
        matrix_x = self.matrix_boxes[0][0].rect.x
        matrix_y = self.matrix_boxes[0][0].rect.y
        matrix_width = num_cols * (cell_width + padding) - padding
        matrix_height = num_rows * (cell_height + padding) - padding

        # Bracket dimensions
        bracket_thickness = 5
        bracket_offset_left = 25  # Gap between the brackets and the matrix
        bracket_offset_right = 40  # Vertical offset for the brackets

        # Left bracket
        left_bracket_rects = [
            Rectangle(matrix_x - bracket_offset_left - bracket_thickness, matrix_y, bracket_thickness, matrix_height),  # Vertical line
            Rectangle(matrix_x - bracket_offset_left, matrix_y, cell_width // 4, bracket_thickness),  # Top horizontal line
            Rectangle(matrix_x - bracket_offset_left, matrix_y + matrix_height - bracket_thickness, cell_width // 4, bracket_thickness),  # Bottom horizontal line
        ]

        # Right bracket
        right_bracket_rects = [
            Rectangle(matrix_x + matrix_width + bracket_offset_right, matrix_y, bracket_thickness, matrix_height),  # Vertical line
            Rectangle(matrix_x + matrix_width + bracket_offset_right - cell_width // 4, matrix_y, cell_width // 4, bracket_thickness),  # Top horizontal line
            Rectangle(matrix_x + matrix_width + bracket_offset_right - cell_width // 4, matrix_y + matrix_height - bracket_thickness, cell_width // 4, bracket_thickness),  # Bottom horizontal line
        ]

        # Draw brackets
        for rect in left_bracket_rects + right_bracket_rects:
            draw_rectangle_rec(rect, RAYWHITE)

        LAST_CELL_GAP = 15  # Gap between the matrix and the buttons
        # Render matrix message boxes
        for row_idx, row in enumerate(self.matrix_boxes):
            for col_idx, box in enumerate(row):
                # Calculate the adjusted position for the last column
                if col_idx == len(row) - 1:  # Last column
                    box.set_color(text_color=GOLDEN_YELLOW)
                    box.rect.x += LAST_CELL_GAP  # Add an extra gap before the last column

                # Translate the mouse position to the world position
                mouse_pos_world = get_screen_to_world_2d(get_mouse_position(), self.camera)

                # Update the rectangle's focus state based on the translated mouse position
                if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                    if check_collision_point_rec(mouse_pos_world, box.rect):
                        box.is_focused = True
                    else:
                        box.is_focused = False

                # Handle input and render the box
                box.handle_input()
                box.render()

                # Add a separator before the last column
                if col_idx == len(row) - 2:  # Second-to-last column
                    separator_x = box.rect.x + box.rect.width + 5
                    separator_y = box.rect.y + box.rect.height / 2
                    draw_text_ex(RM.get("mainfont"), ":", Vector2(separator_x, separator_y - 10), 20, 0, WHITE)

            # Reset the position of the last column after rendering to avoid permanent shifts
            if len(row) > 0:
                row[-1].rect.x -= LAST_CELL_GAP  # Restore original position



    def handle_camera_input(self):
        """Handle Camera2D input for zooming and panning."""
        # Zoom with the mouse wheel
        mouse_wheel = get_mouse_wheel_move()
        if mouse_wheel != 0:
            self.camera.zoom += mouse_wheel * 0.1  # Adjust zoom speed
            self.camera.zoom = max(0.1, min(self.camera.zoom, 10.0))  # Clamp zoom level

        # Pan with middle mouse button
        if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_MIDDLE):
            self.is_panning = True
            self.last_mouse_position = get_mouse_position()

        if self.is_panning:
            if is_mouse_button_down(MouseButton.MOUSE_BUTTON_MIDDLE):
                current_mouse_position = get_mouse_position()
                delta = Vector2(
                    current_mouse_position.x - self.last_mouse_position.x,
                    current_mouse_position.y - self.last_mouse_position.y,
                )
                self.camera.target.x -= delta.x / self.camera.zoom
                self.camera.target.y -= delta.y / self.camera.zoom
                self.last_mouse_position = current_mouse_position
            else:
                self.is_panning = False


    def update_matrix_size(self) -> bool:
        """Handle matrix size input and transition to matrix content input."""
        # Draw title
        draw_centered_text_ex("Specify Matrix Size", RM.get("mainfont"), 120, 50, GOLDEN_YELLOW)

        # Check and handle input for row and column boxes
        self.column_box.check_focus()
        self.row_box.check_focus()
        self.column_box.handle_input()
        self.row_box.handle_input()

        # Render row and column boxes
        self.column_box.render()
        self.row_box.render()

        # Draw "X" between the boxes
        draw_centered_text_ex("X", RM.get("mainfont"), 320, 370, RAYWHITE)

        # Render buttons
        self.buttons["NEXT"].render()
        if self.buttons["NEXT"].is_clicked():
            try:
                column_count = int(self.column_box.text)
                row_count = int(self.row_box.text)

                # Ensure it's a square matrix
                if column_count == row_count and column_count > 0:
                    self.matrix_size = column_count
                    self.generate_matrix_boxes()
                    return True  # Transition to matrix input
                else:
                    log(TraceLogLevel.LOG_WARNING, "Matrix must be square and non-zero!")
                    self.popup.show("Matrix must be square and non-zero!")

            except ValueError:
                log(TraceLogLevel.LOG_WARNING, "Invalid matrix size input!")
                self.popup.show("Invalid matrix size input!")
        
        return False

    # (Other methods and initializations remain unchanged)
    def gaussian_elimination(self, matrix):
        """
        Perform Gaussian elimination step-by-step and log the process.
        The input matrix is modified in place to transform it to row-echelon form.
        """
        n = len(matrix)
        if len(matrix[0]) != n + 1:
            raise ValueError("Matrix dimensions do not match for an augmented system.")

        log(TraceLogLevel.LOG_INFO, "Starting Gaussian elimination...")
        self.solution += "Starting Gaussian elimination...\n"

        for i in range(n):
            # Step 1: Find the pivot element
            pivot = matrix[i][i]
            if abs(pivot) < 1e-12:  # Small epsilon for near-zero pivot
                log(TraceLogLevel.LOG_WARNING, f"Near-zero pivot encountered at row {i}.")
                self.solution += f"Near-zero pivot encountered at row {i}.\n"
                # Swap with a non-zero row if possible
                for k in range(i + 1, n):
                    if abs(matrix[k][i]) > 1e-12:
                        matrix[i], matrix[k] = matrix[k], matrix[i]
                        log(TraceLogLevel.LOG_INFO, f"Swapped row {i} with row {k}.")
                        self.solution += f"Swapped row {i} with row {k}.\n"
                        pivot = matrix[i][i]
                        break
                else:
                    raise ValueError("Matrix is singular and cannot be solved.")

            # Step 2: Normalize the pivot row
            matrix[i][i:] = [x / pivot for x in matrix[i][i:]]
            log(TraceLogLevel.LOG_INFO, f"Normalized row {i}: {matrix[i]}")
            self.solution += f"Normalized row {i}: {matrix[i]}\n"

            # Step 3: Eliminate below the pivot
            for k in range(i + 1, n):
                factor = matrix[k][i]
                matrix[k][i:] = [matrix[k][j] - factor * matrix[i][j] for j in range(i, n + 1)]
                log(TraceLogLevel.LOG_INFO, f"Eliminated row {k} using row {i}: {matrix[k]}")
                self.solution += f"Eliminated row {k} using row {i}: {matrix[k]}\n"

        log(TraceLogLevel.LOG_INFO, "Gaussian elimination complete.")
        self.solution += "Gaussian elimination complete.\n"
        return matrix



    def back_substitution(self, matrix):
        """
        Perform back substitution on a row-echelon matrix to find the solution.
        """
        n = len(matrix)
        solution = [0] * n

        for i in range(n - 1, -1, -1):
            solution[i] = matrix[i][n]
            for j in range(i + 1, n):
                solution[i] -= matrix[i][j] * solution[j]
            solution[i] /= matrix[i][i]
            log(TraceLogLevel.LOG_INFO, f"Back substitution at row {i}: x[{i}] = {solution[i]}")
            self.solution += f"Back substitution at row {i}: x[{i}] = {solution[i]}\n"

        return solution

    def solve_matrix(self):
        """
        Collect the matrix, perform Gaussian elimination, and display the solution step by step.
        """
        matrix = self.collect_matrix_input()
        if not matrix:
            self.popup.show("Matrix input is invalid. Please check your entries.")
            return

        try:
            # Perform Gaussian elimination
            log(TraceLogLevel.LOG_INFO, "Performing Gaussian elimination...")
            self.solution += "Performing Gaussian elimination...\n"
            self.gaussian_elimination(matrix)

            # Perform back substitution
            log(TraceLogLevel.LOG_INFO, "Performing back substitution...")
            self.solution += "Performing back substitution...\n"
            solution = self.back_substitution(matrix)

            # Display solution in the popup
            solution_text = "\n".join([f"x[{i}] = {x:.2f}" for i, x in enumerate(solution)])
            self.solution += f"Solution:\n{solution_text}\n"

        except ValueError as e:
            log(TraceLogLevel.LOG_WARNING, f"Error: {str(e)}")
            self.solution += f"Error: {str(e)}\n"

    def update(self) -> str:
        """Main update loop."""
        if self.matrix_size == 0:  # Determine matrix size
            if self.update_matrix_size():
                log(TraceLogLevel.LOG_INFO, "Matrix size input completed.")
        else:  # Collect matrix content
            self.handle_camera_input()

            # Begin Camera2D mode
            begin_mode_2d(self.camera)
            self.render_matrix_boxes()
            end_mode_2d()

            # Check if Enter key is pressed to solve the matrix
            self.buttons["SOLVE"].render()
            if self.buttons["SOLVE"].is_clicked() or is_key_pressed(KeyboardKey.KEY_ENTER):
                self.solve_matrix()
                self.popup.show(self.solution)
                self.solution = ""

            # if is_key_pressed(KeyboardKey.KEY_ENTER):
            #     self.solve_matrix()

        self.popup.render()

        return "calculator"



class MainMenu:

    def __init__(self):

        self.font = RM.get("mainfont")

        # Title animation
        self.title = "Circuit "
        self.words = ["Calculator", "Analyzer"]  
        self.current_word_index = 0
        self.position = Vector2(110, 50)
        self.font_size = 160
        self.spacing = 0
        self.text_color = GOLDEN_YELLOW
        self.displayed_text = ""
        self.char_index = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.typing_speed = 0.1  # seconds per letter
        self.cursor_blink_speed = 0.5  # seconds for cursor to toggle visibility
        self.start_time = get_time()
        self.is_typing = True  # True if typing, False if erasing

        self.buttons = {}
        self.buttons["FREEHAND"] = Button(Rectangle(110, 250, 830, 325), DARKGRAY)
        self.buttons["MATRIX"] = Button(Rectangle(1000, 250, 800, 700), DARKGRAY)


    def animate_title(self):

        current_time = get_time()

        if self.is_typing:
            full_text = self.title + self.words[self.current_word_index]
            if self.char_index < len(full_text) and current_time - self.start_time >= self.typing_speed:
                self.displayed_text += full_text[self.char_index]
                self.char_index += 1
                self.start_time = current_time
            elif self.char_index == len(full_text):  
                self.is_typing = False
                self.start_time = current_time + 2 # Wait a bit before erasing
        else:
            if self.char_index > len(self.title) and current_time - self.start_time >= self.typing_speed:
                self.char_index -= 1
                self.displayed_text = self.displayed_text[:-1]
                self.start_time = current_time
            elif self.char_index == len(self.title):  # Fully erased back to "Circuit "
                self.current_word_index = (self.current_word_index + 1) % len(self.words)  # Cycle words
                self.is_typing = True
                self.start_time = current_time + 0.5  # Wait a bit before typing again

        # Cursor blink
        self.cursor_timer += get_frame_time()
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # Drawing
        draw_text_ex(self.font, self.displayed_text, self.position, self.font_size, self.spacing, self.text_color)

        # Draw cursor
        if self.cursor_visible:
            cursor_x = self.position.x + measure_text_ex(self.font, self.displayed_text, self.font_size, self.spacing).x + 5
            cursor_y = self.position.y + self.font_size * 0.12
            cursor_width = 50
            cursor_height = int(self.font_size * 0.7)
            draw_rectangle(int(cursor_x), int(cursor_y), int(cursor_width), int(cursor_height), fade(RAYWHITE, 0.9))


    def update(self) -> str:

        # draw_rectangle_gradient_v(0, 0, APP_WIDTH, APP_HEIGHT, GRAY, LIGHTGRAY)
        draw_rectangle(0, 0, APP_WIDTH, APP_HEIGHT, MATTE_BLACK) 

        self.animate_title()

        for key, button in self.buttons.items():
            button.render()
            if button.is_clicked():
                match key:
                    case "FREEHAND":
                        log(TraceLogLevel.LOG_INFO, "Freehand button clicked")
                        return "canvas"
                        
                    case "MATRIX":
                        log(TraceLogLevel.LOG_INFO, "Matrix button clicked")
                        return "calculator"
                        
                    case _:
                        print(f"Unknown button '{key}' clicked.")

        return "main_menu"
        


def load_resources():

        RM.load("mainfont", "assets/fonts/JetBrainsMono-Bold.ttf", FONT)
        RM.load("mainfont-mid", "assets/fonts/JetBrainsMono-Medium.ttf", FONT)
        RM.load("mainfont-reg", "assets/fonts/JetBrainsMono-Regular.ttf", FONT)
        RM.load("mainfont-semi", "assets/fonts/JetBrainsMono-SemiBold.ttf", FONT)
    


class Application():

    def __init__(self, window_width: int, window_height: int):

        self.window_width = window_width
        self.window_height = window_height
        
        set_config_flags(ConfigFlags.FLAG_WINDOW_RESIZABLE | ConfigFlags.FLAG_VSYNC_HINT)
        init_window(self.window_width, self.window_height, "Circuit Calculator")
        set_target_fps(60)
        set_exit_key(KeyboardKey.KEY_NULL)

        load_resources()

        self.target = load_render_texture(APP_WIDTH, APP_HEIGHT)
        if is_render_texture_ready(self.target):
            log(TraceLogLevel.LOG_INFO, "Render Texture loaded successfully")

        set_texture_filter(self.target.texture, TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.camera = Camera2D(
        Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),        # target
        Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),        # offset
        0,                                             # rotation                   
        1.0)                                           # zoom

        self.canvas = Canvas()
        self.calculator = Calculator()
        self.main_menu = MainMenu()

        self.states = {
            "canvas": self.canvas.update,
            "calculator": self.calculator.update,
            "main_menu": self.main_menu.update,
        }

        self.app_state = "main_menu"


        self.test = Notifier("Hello World")

        maximize_window()



    def __call__(self):

        while not window_should_close():
                
            scale = min(get_screen_width() / APP_WIDTH, get_screen_height() / APP_HEIGHT)

            mouse = get_mouse_position()
            virtual_mouse = vector2_zero()
            virtual_mouse.x = (mouse.x - (get_screen_width() - APP_WIDTH * scale) * 0.5) / scale
            virtual_mouse.y = (mouse.y - (get_screen_height() - APP_HEIGHT * scale) * 0.5) / scale
            virtual_mouse = vector2_clamp(virtual_mouse, vector2_zero(), Vector2(APP_WIDTH, APP_HEIGHT))

            set_mouse_offset(int(-(get_screen_width() - (APP_WIDTH * scale)) * 0.5), int(-(get_screen_height() - (APP_HEIGHT * scale)) * 0.5))
            set_mouse_scale(1 / scale, 1 / scale)

            # if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
            #     delta = get_mouse_delta()
            #     self.rot.x += delta.x * -0.008 / self.camera.zoom
            #     self.rot.y += delta.y * 0.008 / self.camera.zoom
            #     if self.camera.zoom != 1.0: 
            #         self.rot.y = clamp(self.rot.y, -self.camera.zoom / 2.5, self.camera.zoom / 2.5)
            #     else:
            #         self.rot.y = clamp(self.rot.y, 0, 0)

            # mouse_wheel_move = get_mouse_wheel_move()
            # if mouse_wheel_move is not None:
            #     self.camera.zoom += mouse_wheel_move * 0.1  
            #     self.camera.zoom = clamp(self.camera.zoom, 1.0, 5.0)  

            begin_texture_mode(self.target)
            
            clear_background(MATTE_BLACK)

            # BOOM GUMANA SPAGHETTI CODE 101% WORKING
            if self.app_state in self.states.keys():
                self.app_state = self.states[self.app_state]()

            if is_key_pressed(KeyboardKey.KEY_ESCAPE):
                self.app_state = "main_menu"

            # self.test.render()

                        
            end_texture_mode()
 
            begin_drawing()
            # begin_mode_2d(self.camera)
            clear_background(BLANK)
            draw_texture_pro(
                self.target.texture, 
                Rectangle(0, 0, APP_WIDTH, -APP_HEIGHT), 
                Rectangle((get_screen_width() - APP_WIDTH * scale) * 0.5, (get_screen_height() - APP_HEIGHT * scale) * 0.5, 
                          APP_WIDTH * scale, APP_HEIGHT * scale), 
                Vector2(0, 0), 
                0, 
                WHITE)
            
            # end_mode_2d()
            end_drawing()
        
    
    def __del__(self):

        log(TraceLogLevel.LOG_INFO, "Closing application")
        close_window()



if __name__ == "__main__":

    log = TraceLog()
    RM = ResourceManager()
    window = Application(800, 600)
    window()
    del window
from pyray import *
import threading

# ONE BACKSPACE     - FLOW
# TWO BACKSPACE     - FUNCTIONS
# THREE BACKSPACE   - CLASSES


# GLOBALS
global log


# CONSTANTS
APP_WIDTH = 800
APP_HEIGHT = 450



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



class Button:
    
    def __init__(self, rec: Rectangle, color: Color, text = None, font_size = None, icon = None, roundness = None):

        self.rectangle = rec
        self.color = color
        self.text = text
        self.font_size = font_size
        self.icon = icon
        self.roundness = roundness


    def render(self):

        if self.roundness:

            draw_rectangle_rounded(self.rectangle, self.roundness, 0, self.color)
            
            # add text rendering 

        else:

            draw_rectangle_rec(self.rectangle, self.color)
            

    def is_hovered(self) -> bool:

        mouse = get_mouse_position()
        if check_collision_point_rec(mouse, self.rectangle):

            if self.roundness:

                draw_rectangle_rounded_lines(self.rectangle, self.roundness, 0, 1, RAYWHITE)

            else:
                
                draw_rectangle_lines_ex(self.rectangle, 1, RAYWHITE)

            return True
        
        return False
    

    def is_clicked(self) -> bool:

        if self.is_hovered() and is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):

            return True
        
        return False
        

    def set_color(self, color: Color):

        self.color = color  



class Component:

    def __init__(self, position: Vector2, name: str):
        self.position = position  
        self.name = name          
        self.is_dragging = False 
        self.color = YELLOW


    def update(self):

        if self.is_dragging:
            self.position = get_mouse_position()  


    def start_drag(self):

        self.is_dragging = True


    def stop_drag(self):

        self.is_dragging = False



# class Wire(Component):

#     def __init__(self):
#         current_mouse_pos = get_mouse_position()
#         rec = Rectangle(current_mouse_pos.x, current_mouse_pos.y, 50, 8)
#         super().__init__(Vector2(rec.x, rec.y), "Wire")
#         self.rectangle = rec
#         self.drag_offset = Vector2(0, 0)  
#         self.rotation = 0
#         self.stop_drag()

#     def update(self):

#         self.rectangle.x = self.position.x
#         self.rectangle.y = self.position.y

#         if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT) and is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
#             if self.is_dragging:
#                 mouse_pos = get_mouse_position()
#                 self.position = Vector2(mouse_pos.x - self.drag_offset.x, mouse_pos.y - self.drag_offset.y)
#                 if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_RIGHT):
#                     self.rotation += 45
#             elif check_collision_point_rec(
#                 get_mouse_position(),
#                 Rectangle(
#                     self.rectangle.x,
#                     self.rectangle.y,
#                     self.rectangle.width,
#                     self.rectangle.height,
#                 ),
#             ):
#                 mouse_pos = get_mouse_position()
#                 self.drag_offset = Vector2(mouse_pos.x - self.position.x, mouse_pos.y - self.position.y)
#                 self.start_drag()
#         else:
#             self.stop_drag()

#         draw_rectangle_pro(self.rectangle, vector2_zero(), self.rotation, self.color)

#         if not self.is_dragging and check_collision_point_rec(
#             get_mouse_position(),
#             Rectangle(
#                 self.rectangle.x,
#                 self.rectangle.y,
#                 self.rectangle.width,
#                 self.rectangle.height,
#             ),
#         ):
#             draw_rectangle_lines_ex(
#                 Rectangle(
#                     self.rectangle.x - 5,
#                     self.rectangle.y - 5,
#                     self.rectangle.width + 10,
#                     self.rectangle.height + 10,
#                 ),
#                 1,
#                 RAYWHITE,
#             )



class Terminal(Component):

    def __init__(self):
        current_mouse_pos = get_mouse_position()
        rec = Rectangle(current_mouse_pos.x, current_mouse_pos.y, 80, 80)
        self.texture = load_texture("assets/terminal.png")
        super().__init__(Vector2(rec.x, rec.y), "Terminal")
        self.rectangle = rec
        self.drag_offset = Vector2(0, 0)  
        self.rotation = 0
        self.stop_drag()


    def get_hitbox(self) -> Rectangle:
        return Rectangle(
            self.rectangle.x - self.rectangle.width / 2,
            self.rectangle.y - self.rectangle.height / 2,
            self.rectangle.width,
            self.rectangle.height,
        )

    
    def update(self):
        self.rectangle.x = self.position.x
        self.rectangle.y = self.position.y

        if  is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
            if self.is_dragging:
                mouse_pos = get_mouse_position()
                self.position = Vector2(mouse_pos.x - self.drag_offset.x, mouse_pos.y - self.drag_offset.y)
    
            elif check_collision_point_rec(
                get_mouse_position(),
                Rectangle(
                    self.rectangle.x - self.rectangle.width / 2,
                    self.rectangle.y - self.rectangle.width / 2,
                    self.rectangle.width,
                    self.rectangle.width,
                ),
            ):
                mouse_pos = get_mouse_position()
                self.drag_offset = Vector2(mouse_pos.x - self.position.x, mouse_pos.y - self.position.y)
                self.start_drag()
        else:
            self.stop_drag()

        # draw_rectangle_pro(self.rectangle, Vector2(self.rectangle.width / 2, self.rectangle.height / 2), self.rotation, self.color)
        draw_texture_pro(self.texture, Rectangle(0, 0, self.texture.width, self.texture.height), Rectangle(self.rectangle.x, self.rectangle.y, self.rectangle.width, self.rectangle.height), Vector2(self.rectangle.width / 2, self.rectangle.height / 2), self.rotation, WHITE)

        if not self.is_dragging and check_collision_point_rec(
            get_mouse_position(),
            Rectangle(
                self.rectangle.x - self.rectangle.width / 2,
                self.rectangle.y - self.rectangle.width / 2,
                self.rectangle.width,
                self.rectangle.width,
            ),
        ):
            draw_rectangle_lines_ex(
                Rectangle(
                    self.rectangle.x - self.rectangle.width / 2,
                    self.rectangle.y - self.rectangle.width / 2,
                    self.rectangle.width,
                    self.rectangle.width,
                ),
                1,
                RAYWHITE,
            )

            if is_key_pressed(KeyboardKey.KEY_A) or is_key_pressed(KeyboardKey.KEY_LEFT):
                    self.rotation -= 45

            if is_key_pressed(KeyboardKey.KEY_D) or is_key_pressed(KeyboardKey.KEY_RIGHT):
                    self.rotation += 45



class Canvas:

    def __init__(self):

        self.buttons = {}
        self.buttons["MENU"] = Button(Rectangle(5, 5, 25, 20), GRAY)
        self.menu_open = False
        self.menu_horizontal_position = -300 # flag for menu position

        self.texture = load_texture("assets/three_dots.jpg")

        self.test = []


    def update(self):

        if is_key_pressed(KeyboardKey.KEY_SPACE):

            self.test.append(Terminal())
            log(TraceLogLevel.LOG_INFO, "Wire added to canvas")

        if self.test:
            for wire in self.test:
                wire.update()

        if is_key_pressed(KeyboardKey.KEY_R):
            self.test.clear()

        self.toggle_menu()

        for key, button in self.buttons.items():
            button.render()
            if button.is_clicked():
                match key:
                    case "MENU":
                        if self.menu_open:
                            self.menu_open = False
                            self.buttons["MENU"].set_color(GRAY)
                        else:
                            self.menu_open = True
                            self.buttons["MENU"].set_color(DARKGRAY)

                    case "EXIT":
                        log(TraceLogLevel.LOG_INFO, "Exiting application")
                        close_window()
                    case _:
                        print(f"Unknown button '{key}' clicked.")

        

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



class Application():

    def __init__(self, window_width: int, window_height: int):

        self.window_width = window_width
        self.window_height = window_height
        
        set_config_flags(ConfigFlags.FLAG_WINDOW_RESIZABLE | ConfigFlags.FLAG_VSYNC_HINT)
        set_config_flags(ConfigFlags.FLAG_WINDOW_RESIZABLE | ConfigFlags.FLAG_VSYNC_HINT)
        init_window(self.window_width, self.window_height, "Circuit Calculator")
        set_target_fps(60)

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
            
            clear_background(DARKGRAY)

            self.canvas.update()
                        
            end_texture_mode()
 
            begin_drawing()
            begin_mode_2d(self.camera)
            clear_background(BLANK)
            draw_texture_pro(
                self.target.texture, 
                Rectangle(0, 0, APP_WIDTH, -APP_HEIGHT), 
                Rectangle((get_screen_width() - APP_WIDTH * scale) * 0.5, (get_screen_height() - APP_HEIGHT * scale) * 0.5, 
                          APP_WIDTH * scale, APP_HEIGHT * scale), 
                Vector2(0, 0), 
                0, 
                WHITE)
            
            end_mode_2d()
            end_drawing()
        
    
    def __del__(self):

        log(TraceLogLevel.LOG_INFO, "Closing application")
        close_window()



if __name__ == "__main__":

    log = TraceLog()
    window = Application(800, 600)
    window()
    del window
class Calculator:

    def __init__(self):
        # Message boxes for matrix size input
        self.column_box = MessageBox(Rectangle(200, 125, 150, 150), RM.get("mainfont"))
        self.row_box = MessageBox(Rectangle(450, 125, 150, 150), RM.get("mainfont"))

        # Buttons
        self.buttons = {
            "NEXT": Button(Rectangle(325, 350, 150, 50), GRAY, text="NEXT"),
            "SOLVE": Button(Rectangle(325, 350, 150, 50), GRAY, text="SOLVE")
        }

        # Matrix message boxes
        self.matrix_boxes = []  # List of message boxes for matrix input
        self.matrix_size = 0  # Current matrix size (determined by row/column input)

        # Camera2D setup for grid panning and zooming
        self.camera = Camera2D(
        Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),        # target
        Vector2(APP_WIDTH / 2, APP_HEIGHT / 2),        # offset
        0,                                             # rotation                   
        1.0)  

        # Mouse panning state
        self.is_panning = False
        self.last_mouse_position = Vector2(0, 0)


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
        draw_centered_text_ex("GAUSSIAN ELIMINATION", RM.get("mainfont"), 50, 25, RAYWHITE)

        # Check and handle input for row and column boxes
        self.column_box.check_focus()
        self.row_box.check_focus()
        self.column_box.handle_input()
        self.row_box.handle_input()

        # Render row and column boxes
        self.column_box.render()
        self.row_box.render()

        # Draw "X" between the boxes
        draw_centered_text_ex("X", RM.get("mainfont"), 100, 150, RAYWHITE)

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

            except ValueError:
                log(TraceLogLevel.LOG_WARNING, "Invalid matrix size input!")
        
        return False

    # (Other methods and initializations remain unchanged)
    def gaussian_elimination(self, matrix):
        """
        Perform Gaussian elimination step-by-step and log the process.
        The input matrix is modified in place to transform it to row-echelon form.
        """
        n = len(matrix)
        log(TraceLogLevel.LOG_INFO, "Starting Gaussian elimination...")

        for i in range(n):
            # Step 1: Find the pivot element
            pivot = matrix[i][i]
            if pivot == 0:
                log(TraceLogLevel.LOG_WARNING, f"Zero pivot encountered at row {i}.")
                # Swap with a non-zero row if possible
                for k in range(i + 1, n):
                    if matrix[k][i] != 0:
                        matrix[i], matrix[k] = matrix[k], matrix[i]
                        log(TraceLogLevel.LOG_INFO, f"Swapped row {i} with row {k}.")
                        pivot = matrix[i][i]
                        break
                else:
                    raise ValueError("Matrix is singular and cannot be solved.")

            # Step 2: Normalize the pivot row
            for j in range(i, n + 1):
                matrix[i][j] /= pivot
            log(TraceLogLevel.LOG_INFO, f"Normalized row {i}: {matrix[i]}")

            # Step 3: Eliminate below the pivot
            for k in range(i + 1, n):
                factor = matrix[k][i]
                for j in range(i, n + 1):
                    matrix[k][j] -= factor * matrix[i][j]
                log(TraceLogLevel.LOG_INFO, f"Eliminated row {k} using row {i}: {matrix[k]}")

        log(TraceLogLevel.LOG_INFO, "Gaussian elimination complete.")
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

        return solution

    def solve_matrix(self):
        """
        Collect the matrix, perform Gaussian elimination, and display the solution step by step.
        """
        matrix = self.collect_matrix_input()
        if not matrix:
            log(TraceLogLevel.LOG_WARNING, "Matrix input is invalid.")
            return

        try:
            # Perform Gaussian elimination
            log(TraceLogLevel.LOG_INFO, "Performing Gaussian elimination...")
            self.gaussian_elimination(matrix)

            # Perform back substitution
            log(TraceLogLevel.LOG_INFO, "Performing back substitution...")
            solution = self.back_substitution(matrix)

            # Display solution
            log(TraceLogLevel.LOG_INFO, "Solution obtained:")
            for i, x in enumerate(solution):
                print(f"x[{i}] = {x}")

        except ValueError as e:
            log(TraceLogLevel.LOG_WARNING, f"Error during solving: {e}")

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
            if is_key_pressed(KeyboardKey.KEY_ENTER):
                self.solve_matrix()

        return "calculator"
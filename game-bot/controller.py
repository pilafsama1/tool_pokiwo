"""
Mouse Controller Module
Controls mouse movements and performs drag actions
"""

import pyautogui
import time
import random
from typing import Tuple
from logic import Position, Move


class MouseController:
    """Handles mouse control for game interaction"""
    
    def __init__(self, board_top: int, board_left: int, 
                 cell_width: int, cell_height: int,
                 drag_duration: float = 0.3,
                 random_delay_min: float = 0.1,
                 random_delay_max: float = 0.3):
        """
        Initialize mouse controller
        
        Args:
            board_top: Top pixel coordinate of the board
            board_left: Left pixel coordinate of the board
            cell_width: Width of a cell in pixels
            cell_height: Height of a cell in pixels
            drag_duration: Duration of drag action in seconds
            random_delay_min: Minimum random delay
            random_delay_max: Maximum random delay
        """
        self.board_top = board_top
        self.board_left = board_left
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.drag_duration = drag_duration
        self.random_delay_min = random_delay_min
        self.random_delay_max = random_delay_max
        
        # Safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions
    
    def grid_to_screen(self, pos: Position) -> Tuple[int, int]:
        """
        Convert grid coordinates to screen coordinates
        
        Args:
            pos: Grid position
            
        Returns:
            Tuple of (screen_x, screen_y) at center of cell
        """
        screen_x = self.board_left + (pos.col * self.cell_width) + (self.cell_width // 2)
        screen_y = self.board_top + (pos.row * self.cell_height) + (self.cell_height // 2)
        
        return (screen_x, screen_y)
    
    def add_human_variation(self, x: int, y: int) -> Tuple[int, int]:
        """
        Add small random variation to coordinates to mimic human input
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Modified (x, y) coordinates
        """
        # Add small random offset (±5 pixels)
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        
        return (x + offset_x, y + offset_y)
    
    def human_delay(self):
        """Add a random human-like delay"""
        delay = random.uniform(self.random_delay_min, self.random_delay_max)
        time.sleep(delay)
    
    def move_to_position(self, pos: Position, add_variation: bool = True):
        """
        Move mouse to a grid position
        
        Args:
            pos: Grid position
            add_variation: Whether to add human-like variation
        """
        x, y = self.grid_to_screen(pos)
        
        if add_variation:
            x, y = self.add_human_variation(x, y)
        
        # Use human-like movement curve
        duration = random.uniform(0.2, 0.4)
        pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
    
    def drag_gems(self, from_pos: Position, to_pos: Position, 
                  add_variation: bool = True):
        """
        Perform a drag action from one position to another
        
        Args:
            from_pos: Starting position
            to_pos: Ending position
            add_variation: Whether to add human-like variation
        """
        # Get screen coordinates
        from_x, from_y = self.grid_to_screen(from_pos)
        to_x, to_y = self.grid_to_screen(to_pos)
        
        # Add variation
        if add_variation:
            from_x, from_y = self.add_human_variation(from_x, from_y)
            to_x, to_y = self.add_human_variation(to_x, to_y)
        
        # Move to starting position
        move_duration = random.uniform(0.2, 0.4)
        pyautogui.moveTo(from_x, from_y, duration=move_duration, 
                        tween=pyautogui.easeInOutQuad)
        
        # Small delay before clicking
        time.sleep(random.uniform(0.05, 0.15))
        
        # Perform drag
        pyautogui.drag(to_x - from_x, to_y - from_y, 
                      duration=self.drag_duration,
                      button='left',
                      tween=pyautogui.easeInOutQuad)
        
        # Small delay after drag
        time.sleep(random.uniform(0.05, 0.15))
    
    def click_position(self, pos: Position, add_variation: bool = True):
        """
        Click on a grid position
        
        Args:
            pos: Grid position to click
            add_variation: Whether to add human-like variation
        """
        x, y = self.grid_to_screen(pos)
        
        if add_variation:
            x, y = self.add_human_variation(x, y)
        
        # Move to position
        duration = random.uniform(0.2, 0.4)
        pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
        
        # Click
        time.sleep(random.uniform(0.05, 0.1))
        pyautogui.click()
    
    def execute_move(self, move: Move, add_variation: bool = True):
        """
        Execute a game move
        
        Args:
            move: Move object to execute
            add_variation: Whether to add human-like variation
        """
        print(f"Executing move: {move.from_pos} -> {move.to_pos}")
        
        # Add pre-move delay
        self.human_delay()
        
        # Perform drag
        self.drag_gems(move.from_pos, move.to_pos, add_variation)
        
        # Add post-move delay
        self.human_delay()
    
    def get_current_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position
        
        Returns:
            Tuple of (x, y) screen coordinates
        """
        return pyautogui.position()
    
    def is_mouse_in_board(self) -> bool:
        """
        Check if mouse is currently within the board area
        
        Returns:
            True if mouse is in board area
        """
        x, y = pyautogui.position()
        
        in_x = self.board_left <= x <= self.board_left + (self.cell_width * 8)  # Assuming 8 cols
        in_y = self.board_top <= y <= self.board_top + (self.cell_height * 8)  # Assuming 8 rows
        
        return in_x and in_y
    
    def emergency_stop(self):
        """
        Emergency stop - move mouse to corner
        (Triggers PyAutoGUI failsafe)
        """
        pyautogui.moveTo(0, 0)
    
    def update_board_coordinates(self, board_top: int, board_left: int,
                                cell_width: int, cell_height: int):
        """
        Update board coordinates (useful for calibration)
        
        Args:
            board_top: New top coordinate
            board_left: New left coordinate
            cell_width: New cell width
            cell_height: New cell height
        """
        self.board_top = board_top
        self.board_left = board_left
        self.cell_width = cell_width
        self.cell_height = cell_height


class MouseCalibration:
    """Helper class for calibrating mouse coordinates"""
    
    @staticmethod
    def get_click_position() -> Tuple[int, int]:
        """
        Wait for user to click and return the position
        
        Returns:
            Clicked position (x, y)
        """
        print("Move mouse to desired position and press Enter...")
        input()
        return pyautogui.position()
    
    @staticmethod
    def calibrate_board() -> dict:
        """
        Interactive calibration for board coordinates
        
        Returns:
            Dictionary with board configuration
        """
        print("=== Board Calibration ===")
        print("This will help you set up the correct board coordinates.\n")
        
        print("1. Click on the TOP-LEFT corner of the board")
        top_left = MouseCalibration.get_click_position()
        print(f"   Top-left: {top_left}\n")
        
        print("2. Click on the BOTTOM-RIGHT corner of the board")
        bottom_right = MouseCalibration.get_click_position()
        print(f"   Bottom-right: {bottom_right}\n")
        
        # Calculate dimensions
        board_left = top_left[0]
        board_top = top_left[1]
        board_width = bottom_right[0] - top_left[0]
        board_height = bottom_right[1] - top_left[1]
        
        print("Enter number of rows (default 8):")
        rows = input().strip() or "8"
        rows = int(rows)
        
        print("Enter number of columns (default 8):")
        cols = input().strip() or "8"
        cols = int(cols)
        
        cell_width = board_width // cols
        cell_height = board_height // rows
        
        config = {
            "board_top": board_top,
            "board_left": board_left,
            "board_width": board_width,
            "board_height": board_height,
            "rows": rows,
            "cols": cols,
            "cell_width": cell_width,
            "cell_height": cell_height
        }
        
        print("\n=== Calibration Complete ===")
        print(f"Board position: ({board_left}, {board_top})")
        print(f"Board size: {board_width}x{board_height}")
        print(f"Grid: {rows}x{cols}")
        print(f"Cell size: {cell_width}x{cell_height}")
        
        return config


if __name__ == "__main__":
    # Test mouse controller
    print("Testing mouse controller...")
    print("Note: This will move your mouse. Press Ctrl+C to abort.\n")
    
    # Example coordinates (adjust for your setup)
    controller = MouseController(
        board_top=200,
        board_left=400,
        cell_width=100,
        cell_height=100
    )
    
    # Test grid to screen conversion
    test_pos = Position(3, 3)
    screen_x, screen_y = controller.grid_to_screen(test_pos)
    print(f"Grid position {test_pos} -> Screen position ({screen_x}, {screen_y})")
    
    # Uncomment to run calibration
    # config = MouseCalibration.calibrate_board()
    # print("\nCalibration config:")
    # for key, value in config.items():
    #     print(f"  {key}: {value}")

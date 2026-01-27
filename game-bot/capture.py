"""
Screen Capture Module
Captures the game board region from the screen using mss
"""

import mss
import numpy as np
from typing import Tuple
import cv2


class ScreenCapture:
    """Handles screen capture of the game board"""
    
    def __init__(self, top: int, left: int, width: int, height: int):
        """
        Initialize screen capture with board coordinates
        
        Args:
            top: Top pixel coordinate of the board
            left: Left pixel coordinate of the board
            width: Width of the board in pixels
            height: Height of the board in pixels
        """
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.sct = mss.mss()
        
        # Define monitor region
        self.monitor = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        
    def capture_board(self) -> np.ndarray:
        """
        Capture the current game board
        
        Returns:
            numpy array representing the captured image (BGR format)
        """
        # Capture screenshot
        screenshot = self.sct.grab(self.monitor)
        
        # Convert to numpy array
        img = np.array(screenshot)
        
        # Convert from BGRA to BGR (remove alpha channel)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def capture_board_rgb(self) -> np.ndarray:
        """
        Capture the current game board in RGB format
        
        Returns:
            numpy array representing the captured image (RGB format)
        """
        img = self.capture_board()
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    def get_board_dimensions(self) -> Tuple[int, int]:
        """
        Get the dimensions of the captured board
        
        Returns:
            Tuple of (width, height)
        """
        return (self.width, self.height)
    
    def update_region(self, top: int, left: int, width: int, height: int):
        """
        Update the capture region
        
        Args:
            top: New top coordinate
            left: New left coordinate
            width: New width
            height: New height
        """
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        
        self.monitor = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        
    def save_screenshot(self, filename: str):
        """
        Save a screenshot to file
        
        Args:
            filename: Path to save the screenshot
        """
        img = self.capture_board()
        cv2.imwrite(filename, img)
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'sct'):
            self.sct.close()


if __name__ == "__main__":
    # Test the capture module
    print("Testing screen capture...")
    
    # Create capture object with example coordinates
    capture = ScreenCapture(top=200, left=400, width=800, height=800)
    
    # Capture board
    board_img = capture.capture_board()
    print(f"Captured image shape: {board_img.shape}")
    
    # Save test screenshot
    capture.save_screenshot("test_capture.png")
    print("Test screenshot saved as 'test_capture.png'")
    
    # Display for 2 seconds if OpenCV display is available
    cv2.imshow("Board Capture Test", board_img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

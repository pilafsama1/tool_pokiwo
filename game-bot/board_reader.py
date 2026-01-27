"""
Board Reader Module
Recognizes gems on the board using template matching
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
from pathlib import Path


class BoardReader:
    """Reads and recognizes gems on the game board"""
    
    def __init__(self, rows: int, cols: int, gem_types: List[str], 
                 templates_dir: str, threshold: float = 0.7):
        """
        Initialize board reader
        
        Args:
            rows: Number of rows on the board
            cols: Number of columns on the board
            gem_types: List of gem type names
            templates_dir: Directory containing template images
            threshold: Matching threshold (0-1)
        """
        self.rows = rows
        self.cols = cols
        self.gem_types = gem_types
        self.threshold = threshold
        self.templates_dir = Path(templates_dir)
        
        # Load templates
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, np.ndarray]:
        """
        Load template images for each gem type
        
        Returns:
            Dictionary mapping gem type to template image
        """
        templates = {}
        
        for gem_type in self.gem_types:
            # Try common image extensions
            for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                template_path = self.templates_dir / f"{gem_type}{ext}"
                
                if template_path.exists():
                    # Load template in grayscale for better matching
                    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        templates[gem_type] = template
                        print(f"Loaded template: {gem_type} ({template.shape})")
                        break
        
        if not templates:
            print(f"WARNING: No templates loaded from {self.templates_dir}")
            print(f"Expected gem types: {self.gem_types}")
        
        return templates
    
    def split_board_into_cells(self, board_img: np.ndarray) -> List[List[np.ndarray]]:
        """
        Split board image into individual cell images
        
        Args:
            board_img: Full board image
            
        Returns:
            2D list of cell images [row][col]
        """
        height, width = board_img.shape[:2]
        
        cell_height = height // self.rows
        cell_width = width // self.cols
        
        cells = []
        for row in range(self.rows):
            row_cells = []
            for col in range(self.cols):
                # Extract cell region
                y1 = row * cell_height
                y2 = (row + 1) * cell_height
                x1 = col * cell_width
                x2 = (col + 1) * cell_width
                
                cell_img = board_img[y1:y2, x1:x2]
                row_cells.append(cell_img)
            
            cells.append(row_cells)
        
        return cells
    
    def recognize_gem(self, cell_img: np.ndarray) -> Tuple[str, float]:
        """
        Recognize the gem type in a cell using template matching
        
        Args:
            cell_img: Image of a single cell
            
        Returns:
            Tuple of (gem_type, confidence)
        """
        if not self.templates:
            return ("UNKNOWN", 0.0)
        
        # Convert cell to grayscale
        if len(cell_img.shape) == 3:
            cell_gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
        else:
            cell_gray = cell_img
        
        best_match = None
        best_confidence = 0.0
        
        # Try each template
        for gem_type, template in self.templates.items():
            # Resize template to match cell size if needed
            if template.shape != cell_gray.shape:
                template_resized = cv2.resize(template, 
                                             (cell_gray.shape[1], cell_gray.shape[0]))
            else:
                template_resized = template
            
            # Perform template matching
            result = cv2.matchTemplate(cell_gray, template_resized, 
                                      cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            # Update best match
            if max_val > best_confidence:
                best_confidence = max_val
                best_match = gem_type
        
        # Return best match if above threshold
        if best_match and best_confidence >= self.threshold:
            return (best_match, best_confidence)
        else:
            return ("UNKNOWN", best_confidence)
    
    def read_board(self, board_img: np.ndarray) -> List[List[str]]:
        """
        Read the entire board and recognize all gems
        
        Args:
            board_img: Full board image
            
        Returns:
            2D list of gem types [row][col]
        """
        # Split into cells
        cells = self.split_board_into_cells(board_img)
        
        # Recognize each cell
        board = []
        for row_idx, row_cells in enumerate(cells):
            row_gems = []
            for col_idx, cell_img in enumerate(row_cells):
                gem_type, confidence = self.recognize_gem(cell_img)
                row_gems.append(gem_type)
                
                # Debug output
                if confidence < self.threshold:
                    print(f"Warning: Low confidence at ({row_idx}, {col_idx}): "
                          f"{gem_type} ({confidence:.2f})")
            
            board.append(row_gems)
        
        return board
    
    def visualize_board(self, board_img: np.ndarray, board: List[List[str]], 
                       save_path: Optional[str] = None):
        """
        Create a visualization of the recognized board
        
        Args:
            board_img: Original board image
            board: Recognized board state
            save_path: Optional path to save visualization
        """
        vis_img = board_img.copy()
        height, width = vis_img.shape[:2]
        
        cell_height = height // self.rows
        cell_width = width // self.cols
        
        # Draw grid and labels
        for row in range(self.rows):
            for col in range(self.cols):
                # Draw grid lines
                x1 = col * cell_width
                y1 = row * cell_height
                x2 = (col + 1) * cell_width
                y2 = (row + 1) * cell_height
                
                cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                
                # Add text label
                gem_type = board[row][col]
                label = gem_type[:3]  # First 3 characters
                
                # Calculate text position (center of cell)
                text_x = x1 + 5
                text_y = y1 + 20
                
                cv2.putText(vis_img, label, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # Display or save
        if save_path:
            cv2.imwrite(save_path, vis_img)
        else:
            cv2.imshow("Board Recognition", vis_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        return vis_img
    
    def get_cell_coordinates(self, board_img: np.ndarray, row: int, col: int) -> Tuple[int, int, int, int]:
        """
        Get pixel coordinates for a specific cell
        
        Args:
            board_img: Board image
            row: Row index
            col: Column index
            
        Returns:
            Tuple of (x1, y1, x2, y2) coordinates
        """
        height, width = board_img.shape[:2]
        
        cell_height = height // self.rows
        cell_width = width // self.cols
        
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = (col + 1) * cell_width
        y2 = (row + 1) * cell_height
        
        return (x1, y1, x2, y2)
    
    def get_cell_center(self, board_img: np.ndarray, row: int, col: int) -> Tuple[int, int]:
        """
        Get center coordinates of a cell
        
        Args:
            board_img: Board image
            row: Row index
            col: Column index
            
        Returns:
            Tuple of (center_x, center_y)
        """
        x1, y1, x2, y2 = self.get_cell_coordinates(board_img, row, col)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return (center_x, center_y)


if __name__ == "__main__":
    # Test the board reader module
    print("Testing board reader...")
    
    # Create a test board reader
    reader = BoardReader(
        rows=8,
        cols=8,
        gem_types=["RED_FIRE", "BLUE_LIGHTNING", "GREEN_HEART", "YELLOW_STAR"],
        templates_dir="assets/templates",
        threshold=0.7
    )
    
    print(f"Loaded {len(reader.templates)} templates")

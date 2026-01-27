"""
Debug tool to compare templates with actual game cells
"""

import cv2
import numpy as np
from pathlib import Path

# Load debug board image
board_img = cv2.imread('debug_board_1769417076.png')
if board_img is None:
    print("❌ Không tìm thấy debug_board image")
    exit()

print(f"Board size: {board_img.shape[1]}x{board_img.shape[0]}")

# Calculate cell size
rows, cols = 8, 8
cell_width = board_img.shape[1] // cols
cell_height = board_img.shape[0] // rows

print(f"Cell size: {cell_width}x{cell_height}")

# Extract some cells
cells_to_check = [(0, 0), (0, 1), (1, 0), (2, 2)]

for row, col in cells_to_check:
    x = col * cell_width
    y = row * cell_height
    cell_img = board_img[y:y+cell_height, x:x+cell_width]
    
    # Save cell
    cv2.imwrite(f"debug_cell_{row}_{col}.png", cell_img)
    print(f"Saved cell ({row},{col}): {cell_img.shape[1]}x{cell_img.shape[0]}")

# Load and show templates
templates_dir = Path("assets/templates")
print("\nTemplates:")
for template_file in templates_dir.glob("*.png"):
    template = cv2.imread(str(template_file))
    print(f"  {template_file.name}: {template.shape[1]}x{template.shape[0]}")
    
    # Try matching with first cell
    cell_img = board_img[0:cell_height, 0:cell_width]
    
    # Resize template to cell size
    template_resized = cv2.resize(template, (cell_width, cell_height))
    
    # Try different methods
    methods = {
        'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
        'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
        'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED
    }
    
    print(f"  Matching with cell (0,0):")
    for method_name, method in methods.items():
        result = cv2.matchTemplate(cell_img, template_resized, method)
        confidence = result[0][0]
        print(f"    {method_name}: {confidence:.3f}")

print("\n✓ Check debug_cell_*.png files to see actual game cells")

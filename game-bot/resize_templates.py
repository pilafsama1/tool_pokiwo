"""
Resize all gem templates to match actual game cell size
"""

import cv2
import os
from pathlib import Path

# Target size (based on actual game cells)
TARGET_WIDTH = 90  # Smaller to avoid borders
TARGET_HEIGHT = 60

def resize_templates():
    """Resize all templates in assets/templates"""
    templates_dir = Path("assets/templates")
    
    if not templates_dir.exists():
        print("❌ Templates directory not found!")
        return
    
    # Get all PNG files
    template_files = list(templates_dir.glob("*.png"))
    
    if not template_files:
        print("❌ No template files found!")
        return
    
    print(f"Found {len(template_files)} templates")
    print(f"Resizing to {TARGET_WIDTH}x{TARGET_HEIGHT}...\n")
    
    for template_file in template_files:
        # Read template
        img = cv2.imread(str(template_file))
        
        if img is None:
            print(f"⚠️  Could not read: {template_file.name}")
            continue
        
        original_size = f"{img.shape[1]}x{img.shape[0]}"
        
        # Resize using high-quality interpolation
        resized = cv2.resize(img, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_LANCZOS4)
        
        # Save back
        cv2.imwrite(str(template_file), resized)
        
        print(f"✓ {template_file.name}: {original_size} -> {TARGET_WIDTH}x{TARGET_HEIGHT}")
    
    print(f"\n✅ Resized {len(template_files)} templates successfully!")
    print(f"Target size: {TARGET_WIDTH}x{TARGET_HEIGHT}")

if __name__ == "__main__":
    resize_templates()

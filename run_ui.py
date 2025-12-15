import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    import pygame
except ImportError:
    print("Error: Pygame is not installed.")
    print("Please install it running: pip install pygame")
    sys.exit(1)

from ui.gui import MemoryVisualizer

if __name__ == "__main__":
    print("Starting Virtual Memory Simulator UI...")
    viz = MemoryVisualizer()
    viz.run()

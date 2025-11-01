#!/usr/bin/env python3
"""
START HERE - Demo Launcher
Interactive menu to explore all LED matrix demos!
"""

import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.led_api import create_matrix


def show_loading_screen(matrix):
    """Show ZX Spectrum style loading screen."""
    matrix.clear()

    # Background
    matrix.fill((0, 0, 0))

    # Rainbow border
    colors = [
        (255, 0, 0), (255, 128, 0), (255, 255, 0),
        (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)
    ]

    for i in range(3):
        color = colors[i % len(colors)]
        matrix.rect(i, i, 64 - 2*i, 64 - 2*i, color, fill=False)

    # Title
    matrix.centered_text("PI", 12, (0, 255, 255))
    matrix.centered_text("MATRIX", 20, (0, 255, 255))

    # Loading bars
    bar_y = 32
    for i, color in enumerate(colors[:5]):
        matrix.rect(8 + i*2, bar_y, 40, 2, color, fill=True)
        bar_y += 3

    # Version
    matrix.centered_text("V1.0", 52, (255, 255, 255))

    matrix.show()
    time.sleep(2)


def show_menu(matrix):
    """Show demo selection menu."""
    matrix.clear()

    # Background - cyan (ZX Spectrum style)
    matrix.fill((0, 150, 150))

    # Border
    for i in range(2):
        matrix.rect(i, i, 64 - 2*i, 64 - 2*i, (255, 255, 0), fill=False)

    # Title bar
    matrix.rect(4, 4, 56, 9, (0, 0, 0), fill=True)
    matrix.centered_text("DEMOS", 6, (255, 255, 0))

    # Menu items (compact for 64x64)
    demos = [
        ("1.HELLO", (255, 255, 255)),
        ("2.GRAPH", (255, 255, 255)),
        ("3.TEXT", (255, 255, 255)),
        ("4.UI", (255, 255, 255)),
        ("5.ANIM", (255, 255, 255)),
        ("6.FX", (255, 255, 255)),
    ]

    y = 16
    for text, color in demos:
        matrix.text(text, 8, y, color, (0, 100, 100))
        y += 8

    # Instructions at bottom
    matrix.centered_text("TYPE#", 56, (255, 255, 0))

    matrix.show()


def run_demo(demo_number):
    """Run the selected demo."""
    demos = {
        '1': 'hello_world.py',
        '2': 'graphics_showcase.py',
        '3': 'text_showcase.py',
        '4': 'combined_demo.py',
        '5': 'animation_demo.py',
        '6': 'plasma_demo.py',
    }

    if demo_number in demos:
        demo_file = os.path.join(os.path.dirname(__file__), demos[demo_number])
        print(f"\n\nLaunching: {demos[demo_number]}\n")
        print("=" * 64)
        subprocess.run([sys.executable, demo_file])
        return True
    return False


def main():
    """Main demo launcher."""
    matrix = create_matrix(64, 64, 'rgb')

    # Show loading screen
    show_loading_screen(matrix)

    # Show menu
    show_menu(matrix)

    # Print menu to terminal too
    print("\n")
    print("=" * 64)
    print("PI-MATRIX DEMO LAUNCHER")
    print("=" * 64)
    print()
    print("Available Demos:")
    print()
    print("  1. Hello World       - Quick start example")
    print("  2. Graphics          - All drawing primitives")
    print("  3. Text              - ZX Spectrum font system")
    print("  4. UI Examples       - Combined graphics + text")
    print("  5. Animations        - Moving patterns")
    print("  6. Plasma Effects    - Mathematical visualizations")
    print()
    print("  7. Physics           - Bouncing balls simulation")
    print("  8. Starfield         - Particle systems")
    print("  9. Spectrum Style    - Retro ZX Spectrum screens")
    print()
    print("  0. Exit")
    print()
    print("=" * 64)

    while True:
        choice = input("\nEnter demo number (0 to exit): ").strip()

        if choice == '0':
            print("\nThanks for exploring Pi-Matrix!")
            print("Check out the README.md for API documentation.")
            break
        elif choice == '7':
            demo_file = os.path.join(os.path.dirname(__file__), 'physics_demo.py')
            print(f"\n\nLaunching: physics_demo.py\n")
            print("=" * 64)
            subprocess.run([sys.executable, demo_file])
        elif choice == '8':
            demo_file = os.path.join(os.path.dirname(__file__), 'starfield_demo.py')
            print(f"\n\nLaunching: starfield_demo.py\n")
            print("=" * 64)
            subprocess.run([sys.executable, demo_file])
        elif choice == '9':
            demo_file = os.path.join(os.path.dirname(__file__), 'zx_spectrum_menu.py')
            print(f"\n\nLaunching: zx_spectrum_menu.py\n")
            print("=" * 64)
            subprocess.run([sys.executable, demo_file])
        elif run_demo(choice):
            pass  # Demo ran successfully
        else:
            print("Invalid choice! Please enter a number 0-9.")

        # Show menu again after demo finishes
        if choice != '0':
            print("\n" + "=" * 64)
            print("Press Enter to return to menu...")
            input()
            show_menu(matrix)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting Pi-Matrix Demo Launcher.")
        print("Thanks for exploring!")

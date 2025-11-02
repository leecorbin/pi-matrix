"""
MatrixOS Bootstrap
Initializes the OS and launches the launcher application
"""

from pathlib import Path
from matrixos.led_api import create_matrix
from matrixos.input import KeyboardInput
from matrixos.config import parse_matrix_args
from matrixos.app_framework import OSContext
from matrixos.builtin_apps.launcher import Launcher


def boot(project_root=None):
    """Bootstrap MatrixOS and launch the launcher.
    
    Args:
        project_root: Path to project root (where apps/ folder is located)
                     If None, uses the current directory
    
    Returns:
        Exit code (0 for success)
    """
    args = parse_matrix_args("MatrixOS Launcher")

    print("\n" + "="*64)
    print("MATRIXOS")
    print("="*64)
    print(f"\nResolution: {args.width}x{args.height} ({args.color_mode.upper()})")
    print("\nControls:")
    print("  Arrow Keys - Navigate")
    print("  Enter      - Launch app")
    print("  Tab        - Help")
    print("  ESC/Q      - Exit")
    print("\n" + "="*64 + "\n")

    # Get project root directory
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    # Create matrix
    matrix = create_matrix(args.width, args.height, args.color_mode)

    # Run launcher
    with KeyboardInput() as input_handler:
        # Create OS context for framework apps
        os_context = OSContext(matrix, input_handler)

        launcher = Launcher(matrix, input_handler, os_context, apps_base_dir=project_root)

        if len(launcher.apps) == 0:
            print("No apps found! Create an app folder with main.py and config.json.")
            return 1

        print(f"Found {len(launcher.apps)} apps:")
        for app in launcher.apps:
            print(f"  - {app.name} (v{app.version}) by {app.author}")
        print()

        launcher.run()

    # Clean exit
    print("\n" + "="*64)
    print("MatrixOS shutdown.")
    print("="*64 + "\n")
    
    return 0

#!/usr/bin/env python3
"""
MatrixOS Entry Point
Minimal script that boots the OS
"""

import sys
import os

# Add matrixos to path
sys.path.insert(0, os.path.dirname(__file__))

from matrixos.bootstrap import boot


if __name__ == '__main__':
    try:
        sys.exit(boot(project_root=os.path.dirname(__file__)))
    except KeyboardInterrupt:
        print("\n\nMatrixOS interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

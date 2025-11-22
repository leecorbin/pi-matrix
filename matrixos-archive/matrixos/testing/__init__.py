"""
MatrixOS Testing Framework

Integrated testing system for MatrixOS apps with:
- Headless display adapter for buffer inspection
- Input event simulation
- Sprite tracking and collision detection
- Rich assertion library
- YAML-based test specifications

Example usage:
    from matrixos.testing import TestRunner
    
    runner = TestRunner("examples.snake.main")
    runner.wait(0.5)
    runner.inject(InputEvent.RIGHT)
    assert runner.text_visible("GAME OVER")
"""

from .display_adapter import HeadlessDisplay
from .input_simulator import InputSimulator
from .runner import TestRunner
from .assertions import Assertions

__all__ = [
    'HeadlessDisplay',
    'InputSimulator', 
    'TestRunner',
    'Assertions',
]

__version__ = '1.0.0'

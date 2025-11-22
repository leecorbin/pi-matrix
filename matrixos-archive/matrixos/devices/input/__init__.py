"""Input drivers for MatrixOS"""

from .terminal import TerminalInputDriver

try:
    from .pygame_input import PygameInputDriver
    __all__ = ['TerminalInputDriver', 'PygameInputDriver']
except ImportError:
    __all__ = ['TerminalInputDriver']

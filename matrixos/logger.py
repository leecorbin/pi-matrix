#!/usr/bin/env python3
"""
MatrixOS Logging System

Provides a simple logging mechanism for apps and the OS itself.
Logs are written to settings/logs/ with automatic timestamps.
"""

import os
import sys
from datetime import datetime
from pathlib import Path


class MatrixLogger:
    """Logger for MatrixOS apps and system components."""
    
    def __init__(self, app_name, log_dir=None):
        """
        Initialize logger for an app.
        
        Args:
            app_name: Name of the app (used for log filename)
            log_dir: Optional custom log directory (defaults to settings/logs/)
        """
        self.app_name = app_name
        
        # Determine log directory
        if log_dir is None:
            # Default to settings/logs/ in project root
            project_root = Path(__file__).parent.parent
            self.log_dir = project_root / "settings" / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        # Create logs directory if needed
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file path (sanitize app name for filename)
        safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in app_name.lower())
        self.log_file = self.log_dir / f"{safe_name}.log"
        
        # Write session start marker
        self._write_raw(f"\n{'='*60}\n")
        self._write_raw(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self._write_raw(f"{'='*60}\n")
    
    def _write_raw(self, message):
        """Write raw message to log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(message)
        except Exception as e:
            # Fallback to stderr if file writing fails
            print(f"[LOG ERROR] {e}: {message}", file=sys.stderr)
    
    def _format_timestamp(self):
        """Get formatted timestamp for log entries."""
        return datetime.now().strftime('%H:%M:%S.%f')[:-3]  # Include milliseconds
    
    def debug(self, message):
        """Log debug message."""
        timestamp = self._format_timestamp()
        self._write_raw(f"[{timestamp}] DEBUG: {message}\n")
    
    def info(self, message):
        """Log info message."""
        timestamp = self._format_timestamp()
        self._write_raw(f"[{timestamp}] INFO: {message}\n")
    
    def warning(self, message):
        """Log warning message."""
        timestamp = self._format_timestamp()
        self._write_raw(f"[{timestamp}] WARNING: {message}\n")
    
    def error(self, message):
        """Log error message."""
        timestamp = self._format_timestamp()
        self._write_raw(f"[{timestamp}] ERROR: {message}\n")
    
    def log(self, message, level="INFO"):
        """
        Generic log method with custom level.
        
        Args:
            message: The message to log
            level: Log level string (default: "INFO")
        """
        timestamp = self._format_timestamp()
        self._write_raw(f"[{timestamp}] {level}: {message}\n")
    
    def separator(self):
        """Write a visual separator line."""
        self._write_raw(f"{'-'*60}\n")


# Global logger instance for MatrixOS system
_system_logger = None

def get_system_logger():
    """Get or create the system-wide logger."""
    global _system_logger
    if _system_logger is None:
        _system_logger = MatrixLogger("MatrixOS")
    return _system_logger


def get_logger(app_name):
    """
    Get a logger instance for an app.
    
    Args:
        app_name: Name of the app
        
    Returns:
        MatrixLogger instance
    """
    return MatrixLogger(app_name)

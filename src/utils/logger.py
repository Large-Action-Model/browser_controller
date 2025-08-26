"""Logging utilities for Browser Controller."""

import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from loguru import logger
from pathlib import Path


class BrowserLogger:
    """Enhanced logger for Browser Controller with structured logging."""
    
    def __init__(self, component: str = "BrowserController", log_level: str = "INFO"):
        self.component = component
        self.log_level = log_level.upper()
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup loguru logger with custom format and handlers."""
        # Remove default handler
        logger.remove()
        
        # Add console handler with custom format
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>[{extra[component]}]</cyan> | "
                   "<level>{message}</level>",
            level=self.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        
        # Add file handler for persistent logging
        log_file = Path("logs") / "browser_controller.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[component]}] | {message}",
            level=self.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            serialize=False,
        )
        
        # Add JSON file handler for structured logging
        json_log_file = Path("logs") / "browser_controller.json"
        logger.add(
            json_log_file,
            format="{message}",
            level=self.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            serialize=True,
        )
    
    def _log_with_context(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message with context and component information."""
        log_context = {
            "component": self.component,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if context:
            log_context.update(context)
        
        logger.bind(**log_context).__getattribute__(level.lower())(message)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log_with_context("DEBUG", message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log_with_context("INFO", message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log_with_context("WARNING", message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Log error message with optional exception details."""
        if exception:
            if context is None:
                context = {}
            context.update({
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
            })
        
        self._log_with_context("ERROR", message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self._log_with_context("CRITICAL", message, context)
    
    def log_browser_action(self, action: str, details: Dict[str, Any]):
        """Log browser action with structured details."""
        context = {
            "action": action,
            "action_type": "browser_action",
            **details
        }
        self.info(f"Browser action: {action}", context)
    
    def log_session_event(self, event: str, session_id: str, details: Optional[Dict[str, Any]] = None):
        """Log session-related event."""
        context = {
            "event": event,
            "session_id": session_id,
            "event_type": "session_event",
            **(details or {})
        }
        self.info(f"Session event: {event}", context)
    
    def log_navigation(self, url: str, method: str = "GET", status_code: Optional[int] = None, load_time: Optional[float] = None):
        """Log navigation event."""
        context = {
            "url": url,
            "method": method,
            "navigation_type": "page_navigation",
        }
        
        if status_code:
            context["status_code"] = status_code
        if load_time:
            context["load_time"] = load_time
        
        self.info(f"Navigation to {url}", context)
    
    def log_element_interaction(self, action: str, element_info: Dict[str, Any]):
        """Log element interaction."""
        context = {
            "interaction_type": "element_interaction",
            "action": action,
            **element_info
        }
        self.info(f"Element interaction: {action}", context)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log performance metric."""
        context = {
            "metric_type": "performance",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
        }
        self.info(f"Performance metric: {metric_name} = {value}{unit}", context)
    
    def create_child_logger(self, child_component: str) -> 'BrowserLogger':
        """Create a child logger for sub-components."""
        full_component = f"{self.component}:{child_component}"
        return BrowserLogger(component=full_component, log_level=self.log_level)


# Global logger instance
_default_logger = None


def get_logger(component: str = "BrowserController") -> BrowserLogger:
    """Get or create logger instance for component."""
    global _default_logger
    if _default_logger is None:
        _default_logger = BrowserLogger(component)
    return _default_logger


def set_log_level(level: str):
    """Set global log level."""
    global _default_logger
    if _default_logger:
        _default_logger.log_level = level.upper()
        _default_logger._setup_logger()

"""
Common functions and classes.
"""

import threading

domain = "https://twitter.com"  # Switch to x.com when that happens


class TimeoutException(Exception):
    """
    Exception for timeouts.
    """

    def __init__(self, message: str = "Timeout"):
        super().__init__(message)


class TimeoutContext:
    """
    Context manager for timeouts.

    Usage (1):
    with TimeoutContext(10):
        # Do something that might take longer than 10 seconds
        function()

    Usage (2):
    try:
        with TimeoutContext(10):
            # Do something that might take longer than 10 seconds
            function()
    except TimeoutError:
        # Handle timeout
        pass
    except Exception as e:
        # Handle other exceptions
        pass
    """

    def __init__(self, timeout_seconds: int or float = 30):
        self.timeout_seconds = timeout_seconds
        self.timeout_event = threading.Event()
        self.is_timed_out = False

    def __enter__(self):
        self.timer = threading.Timer(self.timeout_seconds, self._timeout_handler)
        self.timer.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.timeout_event.set()  # Signal the timeout event
        self.timer.cancel()
        if self.is_timed_out:
            raise TimeoutException(f"Operation timed out after {self.timeout_seconds} seconds.")

    def _timeout_handler(self):
        self.is_timed_out = True
        self.timeout_event.set()  # Signal the timeout event


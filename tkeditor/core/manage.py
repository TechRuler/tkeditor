import time
import threading
from functools import wraps, lru_cache


def debounce(wait_ms=100):
    """
    Debounce decorator: schedules function to run after wait_ms of inactivity.
    Useful for scroll/key/mouse events in Tkinter.
    """
    def decorator(func):
        timer_attr = f"_{func.__name__}_debounce_timer"

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            widget = getattr(self, 'text', None)
            if widget is None:
                return func(self, *args, **kwargs)
            if hasattr(self, timer_attr):
                widget.after_cancel(getattr(self, timer_attr))
            timer_id = widget.after(wait_ms, lambda: func(self, *args, **kwargs))
            setattr(self, timer_attr, timer_id)

        return wrapper
    return decorator



def throttle(wait_ms=100):
    """
    Throttle decorator: ensures function is called at most once every wait_ms.
    Useful for limiting heavy UI updates.
    """
    def decorator(func):
        last_call_attr = f"_{func.__name__}_last_call"

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            now = time.time() * 1000  # convert to ms
            last_call = getattr(self, last_call_attr, 0)
            if now - last_call >= wait_ms:
                setattr(self, last_call_attr, now)
                return func(self, *args, **kwargs)

        return wrapper
    return decorator


def timeit(func):
    """
    Timeit decorator: prints how long the function took to execute.
    Good for debugging performance bottlenecks.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result

    return wrapper


@lru_cache(maxsize=256)
def cached_measure_indent(font_str: str) -> int:
    """
    Cache example: measure indent width (only for pure functions).
    Use this pattern for any non-GUI repeated heavy calls.
    """
    import tkinter.font as tkfont
    return tkfont.Font(font=font_str).measure("    ")

def run_in_thread(func):
    """
    Run function in a separate thread.
    Useful for long-running tasks that shouldn't block the UI.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper

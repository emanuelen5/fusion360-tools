import time
from functools import wraps


def debounced(f, timeout=0.5):
    next_call_time = time.time() + timeout

    @wraps(f)
    def callback(*args, **kwargs):
        nonlocal next_call_time
        current_time = time.time()
        if current_time < next_call_time:
            return

        next_call_time = current_time + timeout
        return f(*args, **kwargs)

    return callback
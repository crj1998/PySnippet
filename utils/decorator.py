from typing import Optional
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = time.time()
        r = func(*args, **kwargs)
        print(func.__name__, time.time() - t)
        return r
    return wrapper

def retry(max_retries: int = 3, interval: Optional[int] = None, ignore: bool = False):
    """ function retry
    Usage:
        @retry(max_retries=3, interval=1, ignore=True)
        def func():
            pass

    Args:
        max_retries (int, optional): retry. Defaults to 3.
        interval (int, optional): retry interval. Defaults to None.
        ignore (bool, optional): ignore error when max retry reach. Defaults to False.

    Raises:
        e: execute error

    """
    assert isinstance(max_retries, int) and max_retries > 0, f"max_retries {max_retries} should be int and greater than 0."
    assert interval is None or isinstance(interval, (float, int)), f"interval {interval} should be number."
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = max_retries
            ret = None
            while retries > 0:
                try:
                    ret = func(*args, **kwargs)
                    break
                except Exception as e:
                    retries -= 1
                    if not ignore and retries == 0: raise e
                    if retries > 0 and interval: time.sleep(interval)
            return ret
        return wrapper
    return decorator


if __name__ == "__main__":
    @timer
    def f(n):
        while n>0:
            n-=1
        return n

    n = f(10000)
import functools
import shelve

def persistent_cache(filepath, ignore=None):
    ignore = set(ignore or [])

    def decorator(func):
        import inspect
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Связываем args/kwargs с именами параметров
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Убираем игнорируемые параметры из ключа
            key_params = {
                k: v for k, v in bound.arguments.items()
                if k not in ignore
            }
            key = str(sorted(key_params.items()))

            with shelve.open(filepath) as cache:
                if key in cache:
                    return cache[key]
                result = func(*args, **kwargs)
                cache[key] = result
                return result

        return wrapper
    return decorator
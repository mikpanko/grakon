from django.core.cache import cache

def cache_function(key, timeout):
    def decorator(func):
        def new_func(*args, **kwargs):
            res = cache.get(key)
            if res:
                return res

            res = func(*args, **kwargs)
            cache.set(key, res, timeout)
            return res

        return new_func

    return decorator

def cache_view(key_generator, timeout, only_anonym=True):
    """ key_generator = lambda args, kwargs: key """
    def decorator(func):
        def new_func(request, *args, **kwargs):
            if (only_anonym and not request.user.is_authenticated()) or not only_anonym:
                key = key_generator(args, kwargs)

                res = cache.get(key)
                if res:
                    return res

                res = func(request, *args, **kwargs)
                cache.set(key, res, timeout)
            else:
                res = func(request, *args, **kwargs)

            return res

        return new_func

    return decorator

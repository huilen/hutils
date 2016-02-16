import pickle
import logging
import xxhash


logger = logging.getLogger(__name__)


def memoized(path_pattern):
    def memoize(fn):
        def memoize_wrapper(*args, **kwargs):
            hash = xxhash.xxh64(str(args) + str(kwargs)).intdigest()
            path = path_pattern.format(hash=hash)
            try:
                with open(path, 'rb') as file:
                    logger.debug("Loading pickle %s", path)
                    data = pickle.load(file)
            except (FileNotFoundError, EOFError):
                data = fn(*args, **kwargs)
                with open(path, 'wb') as file:
                    pickle.dump(data, file)
            return data
        return memoize_wrapper
    return memoize

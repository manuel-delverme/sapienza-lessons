import hashlib
import os
import pickle


def disk_cache(f):
    def wrapper(*args, **kwargs):
        if args:
            fid = f.__name__ + "/"
            cache_folder = "cache/" + fid
            if not os.path.exists(cache_folder):
                os.mkdir(cache_folder)
            str_args = "::".join(str(arg) for arg in args)
            cache_file = "{}{}.pkl".format(cache_folder, str_args)
        else:
            fid = f.__name__
            cache_file = "cache/{}.pkl".format(fid)

        try:
            with open(cache_file, "rb") as fin:
                retr = pickle.load(fin)
        except FileNotFoundError:
            retr = f(*args, **kwargs)
            with open(cache_file, "wb") as fout:
                pickle.dump(retr, fout)
        return retr
    return wrapper

from threading import Lock, Timer
import atexit


class Cache(dict):
    def __init__(self, update_interval, update_func, args=()):
        self.args = args
        self.lock = Lock()
        self.thread = None
        self.update_func = update_func
        self.update_interval = update_interval

        self.update_cache()
        atexit.register(self.cleanup)

    def update_cache(self):
        new_cache = self.update_func(*self.args)
        with self.lock:
            self.clear()
            self.update(new_cache)
        self.thread = Timer(self.update_interval, self.update_cache)
        self.thread.daemon = True
        self.thread.start()

    def cleanup(self):
        self.thread.cancel()

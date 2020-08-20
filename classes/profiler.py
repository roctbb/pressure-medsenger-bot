class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        delta = time.time() - self._startTime

        if delta > 1:
            print("Elapsed time: {:.3f} sec".format(delta))
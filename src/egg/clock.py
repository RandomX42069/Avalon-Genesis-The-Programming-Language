import datetime, os, sys, pathlib, egg.fs, egg.globerr

class clock:
    def __init__(self, stamp=None):
        self.stamp = stamp
        self.logRate = {
            "newborn": 86400,
            "normal": 360000,
            "ancient": 13234342342 
        }
        self._egg_global = egg.globerr.AGC_GLOBAL()
        self._fs = egg.fs.filesystem()

    def integerDate(self):
        return int(datetime.datetime.now().timestamp())

    def _isFar(self, t, override=None):
        threshold = self.stamp if override is None else override
        return (self.integerDate() - t) > threshold

    def _filetime(self, fn):
        if not self._fs.isExistAndFile(fn):
            self._egg_global.err(f"File doesn't exist: {fn}")
            sys.exit(0)

        return int(os.path.getmtime(fn))

    def _ancient_log(self, fn, suffixes, threshold=None):

        if not self._fs.isExistAndFile(fn):
            self._egg_global.err(f"File doesn't exist: {fn}")
            sys.exit(0)

        p = pathlib.Path(fn)

        if p.suffix not in suffixes:
            return False

        file_ts = self._filetime(str(p))
        return self._isFar(file_ts, override=threshold)

    def clean_directory(self, directory, suffixes, rate="normal"):
        if rate not in self.logRate:
            self._egg_global.err(f"Invalid rate '{rate}', must be one of: {list(self.logRate.keys())}")
            sys.exit(1)

        age_limit = self.logRate[rate]

        if not self._fs.isExistAndDir(directory):
            self._egg_global.err(f"Directory doesn't exist: {directory}")
            sys.exit(0)

        dirpath = pathlib.Path(directory)

        deleted = 0
        scanned = 0

        for file in dirpath.iterdir():
            if not file.is_file():
                continue

            scanned += 1
            abs_path = str(file)

            if self._ancient_log(abs_path, suffixes, threshold=age_limit):
                try:
                    os.remove(abs_path)
                    deleted += 1
                    self._egg_global.ok(f"Deleted old log: {abs_path}")
                except Exception as e:
                    self._egg_global.err(f"Error deleting {abs_path}: {e}")

        return {"scanned": scanned, "deleted": deleted}

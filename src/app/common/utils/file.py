import hashlib
import posixpath
import time


def upload_to(instance, filename):
    dirname = hashlib.sha1(f"{time.time()}/{filename}".encode()).hexdigest()[:8]
    return posixpath.join(dirname, filename)

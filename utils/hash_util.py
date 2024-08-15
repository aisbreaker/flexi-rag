import hashlib

# BUF_SIZE is totally arbitrary, change for your app!
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

#md5 = hashlib.md5()
#sha1 = hashlib.sha1()
sha256 = hashlib.sha256()

def sha256sum(file_path) -> str:
    """Compute the SHA-256 hash of a
       file at the given path."""

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            #md5.update(data)
            #sha1.update(data)
            sha256.update(data)
    #hexdigest = md5.hexdigest()
    #hexdigest = sha1.hexdigest()
    hexdigest = sha256.hexdigest()

    #print(f"md5sum({file_path}): {hexdigest}")
    #print(f"sha1sum({file_path}): {hexdigest}")
    print(f"sha256sum({file_path}): {hexdigest}")
    return hexdigest

def sha256sum_str(data: str) -> str:
    """Compute the SHA-256 hash of a
       string."""
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()

# for manual testing:
#filename = "/tmp/wget/dance123.org/index.html"
#sha256sum(filename)

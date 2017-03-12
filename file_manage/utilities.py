import time
import hashlib
import uuid


def id_generator(student_id):
    raw_id = '%s:%s' % (student_id, time.time())
    return hashlib.md5(raw_id.encode('utf-8')).hexdigest()[10:20]


def uuid_generator():
    return str(uuid.uuid4())


# generator binary stream
def file_generator(file_path, chunk_size=1024):
    with open(file_path, 'rb') as file:
        while True:
            c = file.read(chunk_size)
            if c:
                yield c
            else:
                break

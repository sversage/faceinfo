import base64


def read_file_in_base64(filepath):
    '''
    Opens and reads the given file, then encode the file contents as a
    base64 string and returns that base64-encoded string.
    '''
    with open(filepath) as f:
        return base64.b64encode(f.read())

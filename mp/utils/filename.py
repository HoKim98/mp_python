def assert_filename(filename: str, extension: str):
    if filename is None:
        return filename
    if filename.endswith(extension):
        return filename
    return '%s%s' % (filename, extension)

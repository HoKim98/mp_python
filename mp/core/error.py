class BaseError(Exception):
    def __init__(self, error_code: int, message: str):
        self.message = 'Error(%s) : %s' % (hex(error_code), message)
        super().__init__(self.message)
        self.error_code = error_code
        self.message_why = message


class ConstError(BaseError):
    def __init__(self):
        super().__init__(0x10, 'Target is constant.')


class SyntaxError(BaseError):
    def __init__(self, wrong_token: str):
        super().__init__(0x11, 'Wrong token : \'%s\'.' % wrong_token)


class IOError(BaseError):
    def __init__(self, wrong_path: str):
        super().__init__(0x20, 'Wrong access : \'%s\'.' % wrong_path)


class RequiredError(BaseError):
    def __init__(self, wrong_path: str):
        super().__init__(0x30, 'Require ahead : \'%s\'.' % wrong_path)


class TooMuchOrLessArguments(BaseError):
    def __init__(self, wrong_path: str, expected: int, given: int, greater_or_less: int = 0):
        much_or_less = 'much' if expected < given else 'less'
        if greater_or_less > 0:
            greater_or_less = ' or greater'
        elif greater_or_less < 0:
            greater_or_less = ' or less'
        else:
            greater_or_less = ''
        super().__init__(0x40, 'Too %s arguments : \'%s\'. Expected %d%s, but given %d.' %
                         (much_or_less, wrong_path, expected, greater_or_less, given))


class TypeError(BaseError):
    def __init__(self, message: str):
        super().__init__(0x41, 'Wrong type : %s' % message)


class NotDataError(BaseError):
    def __init__(self, wrong_token: str):
        super().__init__(0x42, '\'%s\' is not Data.' % wrong_token)


class WWWNotFound(BaseError):
    def __init__(self, wrong_path: str):
        super().__init__(0x50, '[www] \'%s\' is not found.' % wrong_path)


class WWWNotInCandidate(BaseError):
    def __init__(self, wrong_path: str, base_dir: str, candidates):
        msg = '[www] \'%s\' is not in candidate.' % wrong_path
        msg += '\nAvailable in %s: ' % base_dir
        for name in candidates:
            msg += '\n\t%s.%s' % (base_dir, name)
        super().__init__(0x51, msg)


class NotInCandidate(BaseError):
    def __init__(self, wrong_path: str, base_dir: str, candidates):
        msg = '[www] \'%s\' is not in candidate.' % wrong_path
        msg += '\nAvailable in %s: ' % base_dir
        for name in candidates:
            msg += '\n\t%s' % name
        super().__init__(0x51, msg)

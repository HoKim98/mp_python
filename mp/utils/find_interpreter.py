from mp.core.error import NotInCandidate

INTERPRETER = 'Interpreter'


def find_interpreter(interpreter_name: str, error_exit: bool = True):
    interpreter_name = '%s%s' % (interpreter_name, INTERPRETER)
    mp = __import__('mp')
    # if not have interpreter
    if not hasattr(mp, interpreter_name):
        candidates = [name for name in mp.__dict__.keys() if name.endswith(INTERPRETER)]
        if error_exit:
            print(NotInCandidate(interpreter_name, 'mp', candidates))
            exit()
        raise NotInCandidate(interpreter_name, 'mp', candidates)
    # has interpreter
    return getattr(mp, interpreter_name)

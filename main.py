from mp import PythonInterpreter


if __name__ == '__main__':
    cmd = PythonInterpreter(dir_process='src')
    cmd.execute_script('test')
    cmd.begin_interactive()

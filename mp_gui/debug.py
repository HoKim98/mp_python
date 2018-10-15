from mp_gui import MpGui


if __name__ == '__main__':
    import os
    dir_parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    with open('%s/envs.txt' % dir_parent, 'r') as f:
        os.environ["PATH"] += os.pathsep + f.readline().rstrip()
    gui = MpGui()
    gui.loop()

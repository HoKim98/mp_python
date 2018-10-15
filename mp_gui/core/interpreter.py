from mp import PythonInterpreter


class GuiInterpreter(PythonInterpreter):

    def __init__(self, dir_process: str = './'):
        super().__init__(dir_process)

    def get_vars(self):
        return self.plan.graph.vars

    def get_ios(self):
        return self.plan.graph.ios

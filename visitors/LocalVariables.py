import ast


class LocalVariableExtraction(ast.NodeVisitor):
    """
        We extract all the left hand side of the global (top-level) assignments
    """

    def __init__(self) -> None:
        super().__init__()
        # self.results = set()

        # make a dictionary for global variables
        self.results = dict()

    def shortenvariable(var):
        var_list = var.split()
        new_var = ''
        for i in range(len(var_list)):
            new_var += str(var_list[i])
            i += 2
        return new_var

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        variable_name = node.targets[0].id

        while len(variable_name) > 8:
            var_list = variable_name.split()
            new_var = ''
            for i in range(len(var_list)):
                new_var += str(var_list[i])
                i += 2
            variable_name = new_var

        # self.results.add(node.targets[0].id)
        if variable_name not in self.results:
            # for now check if the type is of type Constant
            if type(node.value) is ast.Constant:
                self.results[variable_name] = [str(type(node.value)), node.value.value]  # save the value of the constant
            # check if it is list contains BinOp
            elif type(node.value) is ast.BinOp:
                self.results[variable_name] = [str(type(node.value)), node.value.right.id]
            elif type(node.value) is ast.Subscript:
                pass
            # for now just show type of value and the object
            else:
                self.results[variable_name] = [str(type(node.value)), node.value]

        # we can access node.targets for the variable name
        # we can also access node.value for information on what type of variable it is and its value

    def visit_FunctionDef(self, node):
        for contents in node.body:
            self.visit(contents)
        try:
            variable_name = node.args.args[0].arg
            self.results[variable_name] = [str(type(node.args)), node.args.args[0].arg]
        except:
            pass
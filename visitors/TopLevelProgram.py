import ast

LabeledInstruction = tuple[str, str]

class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""
    
    def __init__(self, entry_point, thesymboltable) -> None:
        super().__init__()
        self.__instructions = list()
        self.__record_instruction('NOP1', label=entry_point)
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0
        #
        self.__word_alr_defined = dict()
        self.symboltable = thesymboltable

    def finalize(self):
        self.__instructions.append((None, '.END'))
        return self.__instructions

    ####
    ## Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        # remembering the name of the target
        self.__current_variable = node.targets[0].id


        var_alr_defined = False

        if self.__current_variable[0] != '_':
            # visiting the left part, now knowing where to store the result
            functions = ['int', 'input', 'print']
            if type(node.value) == ast.Call and node.value.func.id not in functions:
                self.__record_instruction(f'SUBSP {2*len(node.targets)},i')
                self.visit(node.value)
                self.__record_instruction(f'LDWA 0,s')
                self.__record_instruction(f'ADDSP {2*len(node.targets)},i')
            else:
                if type(node.value) is ast.Constant:
                # keep track of a word variable, it doesnt need to be initialized with load store the first time
                # if it appears again that means we are assigning something new to it so it we need to loadstore
                    if self.__current_variable not in self.__word_alr_defined:
                        self.__word_alr_defined[self.__current_variable] = 1
                        var_alr_defined = True
                    else:
                        self.visit(node.value)
                else:
                    self.visit(node.value)
            if self.__should_save:
                if (self.__current_variable[0] == "_" and self.__current_variable.isupper()):
                    pass
                else:
                    # checks if the word variable has alr been defined, if not then we need to load store in it
                    if not(var_alr_defined):
                        if (len(self.__current_variable) > 8):
                            self.__current_variable = self.symboltable.translate(self.__current_variable)
                        self.__record_instruction(f'STWA {self.__current_variable},d')
            else:
                self.__should_save = True
            self.__current_variable = None

    def visit_Constant(self, node):
        self.__record_instruction(f'LDWA {node.value},i')
    
    def visit_Name(self, node):
        self.__record_instruction(f'LDWA {node.id},d')

    def visit_BinOp(self, node):
        #F5 stuff don't touch for now
        if isinstance(node.op, ast.Mult):
            return
        self.__access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int': 
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.__record_instruction(f'DECI {self.__current_variable},d')
                self.__should_save = False # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO {node.args[0].id},d')
            case _:
                self.__record_instruction(f'CALL {node.func.id}')
    ####
    ## Handling While loops (only variable OP variable)
    ####

    def visit_While(self, node):
        loop_id = self.__identify()
        inverted = {
            ast.Lt:  'BRGE', # '<'  in the code means we branch if '>=' 
            ast.LtE: 'BRGT', # '<=' in the code means we branch if '>' 
            ast.Gt:  'BRLE', # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT', # '>=' in the code means we branch if '<'
            ast.NotEq: 'BREQ', # '!=' in the code means we branch if '='
            ast.Eq: 'BRNEQ', # '==' in the code means we branch if '!='
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label = f'test_{loop_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{inverted[type(node.test.ops[0])]} end_l_{loop_id}')
        # Visiting the body of the loop
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'BR test_{loop_id}')
        # Sentinel marker for the end of the loop
        self.__record_instruction(f'NOP1', label = f'end_l_{loop_id}')

    ####
    ## Not handling function calls 
    ####

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not top level"""
        pass
    ####
    ## Handling if statements
    ####

    def visit_If(self, node):
        condition_id = self.__identify()
        op = {
            ast.Lt:  'BRLT',
            ast.LtE: 'BRLE',
            ast.Gt:  'BRGT',
            ast.GtE: 'BRGE',
            ast.NotEq: 'BRNEQ',
            ast.Eq: 'BREQ',
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label = f'if_{condition_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{op[type(node.test.ops[0])]} con_{condition_id}')
        # Visiting or else of the loop
        for contents in node.orelse:
            self.visit(contents)
        self.__record_instruction(f'BR end_{condition_id}')
        # Visiting the body of the loop
        self.__record_instruction(f'NOP1', label=f'con_{condition_id}')
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'NOP1', label = f'end_{condition_id}')
    ####
    ## Helper functions to 
    ####

    def __record_instruction(self, instruction, label = None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label = None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f'{instruction} {node.value},i', label)
        else:
            self.__record_instruction(f'{instruction} {node.id},d', label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # 符号表，存储变量名及其类型
        self.errors = []  # 存储类型错误
        self.value_stack = []  # 用于存储语法分析中的值

    def analyze_semantics(self, node, production_index):
        """
        根据产生式和当前节点分析语义。
        该方法会根据语法规则的语义定义进行类型检查和计算值。
        """
        if production_index == 0:  # S' -> S
            node.type = node.children[0].type  # S'.type := S.type

        elif production_index == 1:  # S -> D' C
            if node.children[0].type != 'type_error' and node.children[1].type != 'type_error':
                node.type = 'program'  # S.type := program
            else:
                node.type = 'type_error'

        elif production_index == 2:  # S -> C
            node.type = node.children[0].type  # S.type := C.type

        elif production_index == 3:  # D'1 -> D D'2
            if node.children[0].type == 'declaration' and node.children[1].type == 'declarations':
                node.type = 'declarations'  # D'1.type := declarations
            else:
                node.type = 'type_error'

        elif production_index == 4:  # D' -> D
            if node.children[0].type == 'declaration':
                node.type = 'declarations'  # D'.type := declarations
            else:
                node.type = 'type_error'

        elif production_index == 5:  # D -> let T id be E
            if node.children[3].type != 'type_error':  # 检查 E 的类型
                self.add_type(node.children[2].lexeme, node.children[0].type)  # 添加到符号表
                node.type = 'declaration'  # D.type := declaration
            else:
                node.type = 'type_error'

        elif production_index == 6:  # T -> int
            node.type = 'integer'  # T.type := integer

        elif production_index == 7:  # T -> set
            node.type = 'set'  # T.type := set

        elif production_index == 8:  # E -> E'
            node.type = node.children[0].type  # E.type := E'.type

        elif production_index == 9:  # E1 -> E2 U E'
            if node.children[0].type == 'set' and node.children[2].type == 'set':
                node.type = 'set'  # E1.type := set
            else:
                node.type = 'type_error'

        elif production_index == 10:  # E1 -> E2 + E'
            if node.children[0].type == 'integer' and node.children[2].type == 'integer':
                node.type = 'integer'  # E1.type := integer
            else:
                node.type = 'type_error'

        elif production_index == 11:  # E1 -> E2 - E'
            if node.children[0].type == 'integer' and node.children[2].type == 'integer':
                node.type = 'integer'  # E1.type := integer
            else:
                node.type = 'type_error'

        elif production_index == 12:  # E' -> E''
            node.type = node.children[0].type  # E'.type := E''.type

        elif production_index == 13:  # E'1 -> E'2 I E''
            if node.children[1].type == 'set' and node.children[2].type == 'set':
                node.type = 'set'  # E'1.type := set
            else:
                node.type = 'type_error'

        elif production_index == 14:  # E'1 -> E'2 * E''
            if node.children[1].type == 'integer' and node.children[2].type == 'integer':
                node.type = 'integer'  # E'1.type := integer
            else:
                node.type = 'type_error'

        elif production_index == 15:  # E'' -> num
            node.type = 'integer'  # E''.type := integer

        elif production_index == 16:  # E'' -> id
            var_name = node.children[0].lexeme
            node.type = self.lookup_type(var_name)  # E''.type := lookup_type(id.entry)

        elif production_index == 17:  # E'' -> ( E )
            node.type = node.children[1].type  # E''.type := E.type

        elif production_index == 18:  # E'' -> { Z P }
            if node.children[1].type == 'predicate':
                node.type = 'set'  # E''.type := set
            else:
                node.type = 'type_error'

        elif production_index == 19:  # Z -> id :
            self.add_type(node.children[0].lexeme, 'integer')  # add_type(id.entry, integer)
            node.type = 'void'  # Z.type := void

        elif production_index == 20:  # P1 -> P2 | P'
            if node.children[0].type == 'predicate' and node.children[2].type == 'predicate':
                node.type = 'predicate'  # P1.type := predicate
            else:
                node.type = 'type_error'

        elif production_index == 21:  # P -> P'
            node.type = node.children[0].type  # P.type := P'.type

        elif production_index == 22:  # P'1 -> P'2 & P''
            if node.children[1].type == 'predicate' and node.children[2].type == 'predicate':
                node.type = 'predicate'  # P'1.type := predicate
            else:
                node.type = 'type_error'

        elif production_index == 23:  # P' -> P''
            node.type = node.children[0].type  # P'.type := P''.type

        elif production_index == 24:  # P'' -> R
            if node.children[0].type == 'relation':
                node.type = 'predicate'  # P''.type := predicate
            else:
                node.type = 'type_error'

        elif production_index == 25:  # P'' -> ( P )
            node.type = node.children[1].type  # P''.type := P.type

        elif production_index == 26:  # P'' -> ! R
            if node.children[1].type == 'relation':
                node.type = 'predicate'  # P''.type := predicate
            else:
                node.type = 'type_error'

        elif production_index == 27:  # R -> E1 < E2
            if node.children[0].type == 'integer' and node.children[1].type == 'integer':
                node.type = 'relation'  # R.type := relation
            else:
                node.type = 'type_error'

        elif production_index == 28:  # R -> E1 > E2
            if node.children[0].type == 'integer' and node.children[1].type == 'integer':
                node.type = 'relation'  # R.type := relation
            else:
                node.type = 'type_error'

        elif production_index == 29:  # R -> E1 = E2
            if node.children[0].type == 'integer' and node.children[1].type == 'integer':
                node.type = 'relation'  # R.type := relation
            else:
                node.type = 'type_error'

        elif production_index == 30:  # R -> E1 @ E2
            if node.children[0].type == 'integer' and node.children[1].type == 'set':
                node.type = 'relation'  # R.type := relation
            else:
                node.type = 'type_error'

        elif production_index == 31:  # C -> show A
            node.type = node.children[1].type  # C.type := A.type

        elif production_index == 32:  # A -> E
            if node.children[0].type != 'type_error':
                node.type = 'calculation'  # A.type := calculation
            else:
                node.type = 'type_error'

        elif production_index == 33:  # A -> P
            if node.children[0].type != 'type_error':
                node.type = 'calculation'  # A.type := calculation
            else:
                node.type = 'type_error'

    def add_type(self, var_name, var_type):
        """
        将变量添加到符号表中。
        """
        self.symbol_table[var_name] = var_type

    def lookup_type(self, var_name):
        """
        查找符号表中的变量类型。
        """
        return self.symbol_table.get(var_name, 'type_error')

    def get_errors(self):
        """
        返回所有收集到的语义错误。
        """
        return self.errors

    def print_symbol_table(self):
        """
        打印符号表，帮助调试。
        """
        for var_name, var_type in self.symbol_table.items():
            print(f"{var_name}: {var_type}")

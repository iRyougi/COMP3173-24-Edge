# semantic.py


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}

    def analyze(self):
        self.visit(self.ast)

    def visit(self, node):
        method_name = "visit_" + node.type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Program(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_VariableDeclaration(self, node):
        var_name = node.value["name"]
        var_type = node.value["type"]
        if var_name in self.symbol_table:
            raise Exception(f"Variable {var_name} already declared")
        self.symbol_table[var_name] = {"type": var_type}

    def visit_ShowStatement(self, node):
        expr = node.children[0]
        expr_type = self.visit(expr)
        # 可以在这里检查表达式的类型

    def visit_Identifier(self, node):
        var_name = node.value
        if var_name not in self.symbol_table:
            raise Exception(f"Undefined variable {var_name}")
        return self.symbol_table[var_name]["type"]

    def visit_Number(self, node):
        return "int"

# parser.py

class ASTNode:
    def __init__(self, node_type, children=None, value=None):
        self.type = node_type        # 节点类型
        self.children = children if children is not None else []
        self.value = value           # 节点值（如标识符名称、数字等）

    def to_dict(self):
        result = {"type": self.type}
        if self.value is not None:
            result["value"] = self.value
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        statements = []
        while self.current_token().type != 'EOF':
            stmt = self.statement()
            statements.append(stmt)
        return ASTNode('Program', statements)

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        else:
            # 添加一个 EOF 标记
            return Token('EOF', '', self.tokens[-1].line, self.tokens[-1].column)

    def eat(self, token_type):
        token = self.current_token()
        if token.type == token_type:
            self.pos += 1
            return token
        else:
            raise Exception(f"Expected token {token_type}, got {token.type}")

    def statement(self):
        token = self.current_token()
        if token.type == 'LET':
            return self.variable_declaration()
        elif token.type == 'SHOW':
            return self.show_statement()
        else:
            raise Exception(f"Unexpected token {token.type}")

    def variable_declaration(self):
        self.eat('LET')
        identifier = self.eat('IDENTIFIER')
        self.eat('BE')
        var_type_token = self.current_token()
        if var_type_token.type == 'INT':
            var_type = 'int'
            self.eat('INT')
        elif var_type_token.type == 'SET':
            var_type = 'set'
            self.eat('SET')
        else:
            raise Exception(f"Invalid type {var_type_token.type}")
        self.eat('SEMICOLON')
        return ASTNode('VariableDeclaration', value={'name': identifier.lexeme, 'type': var_type})

    def show_statement(self):
        self.eat('SHOW')
        expr = self.expression()
        self.eat('SEMICOLON')
        return ASTNode('ShowStatement', [expr])

    def expression(self):
        # 实现表达式解析（这里简单起见，直接返回标识符或数字）
        token = self.current_token()
        if token.type == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            return ASTNode('Identifier', value=token.lexeme)
        elif token.type == 'NUMBER':
            self.eat('NUMBER')
            return ASTNode('Number', value=token.lexeme)
        else:
            raise Exception(f"Invalid expression starting with {token.type}")

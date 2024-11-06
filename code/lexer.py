# lexer.py

class Token:
    def __init__(self, token_type, lexeme, line, column):
        self.type = token_type       # 标记类型
        self.lexeme = lexeme         # 词素
        self.line = line             # 行号
        self.column = column         # 列号

    def to_dict(self):
        return {
            "token": self.type,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column
        }

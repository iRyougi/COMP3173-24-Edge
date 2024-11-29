import json

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.symbol_table = {}  # 添加符号表
        self.current_position = 0

    def tokenize(self):
        keywords = {"show"}
        operators = {"+", "-", "*", "@", "<", ">", "&", "|", "!"}
        special_symbols = {".", "(", ")", "{", "}", ":"}
        whitespace = {" ", "\n", "\t"}

        while self.current_position < len(self.source_code):
            char = self.source_code[self.current_position]

            if char in whitespace:
                self.current_position += 1
                continue

            if char.isalpha():
                start_pos = self.current_position
                while self.current_position < len(self.source_code) and self.source_code[self.current_position].isalnum():
                    self.current_position += 1
                lexeme = self.source_code[start_pos:self.current_position]
                if lexeme in keywords:
                    self.tokens.append({"token": lexeme, "lexeme": lexeme})
                else:
                    raise ValueError(f"Unexpected identifier '{lexeme}'")

            elif char.isdigit():
                start_pos = self.current_position
                while self.current_position < len(self.source_code) and self.source_code[self.current_position].isdigit():
                    self.current_position += 1
                lexeme = self.source_code[start_pos:self.current_position]
                self.tokens.append({"token": "num", "lexeme": lexeme})
                self.symbol_table[lexeme] = "num"

            elif char in operators:
                self.tokens.append({"token": char, "lexeme": char})
                self.current_position += 1

            elif char in special_symbols:
                self.tokens.append({"token": char, "lexeme": char})
                self.current_position += 1

            else:
                raise ValueError(f"Lexical Error: Unexpected character '{char}' at position {self.current_position}")

    def save_tokens(self, output_file):
        with open(output_file, "w") as f:
            json.dump(self.tokens, f, indent=2)

    def save_symbol_table(self, output_file):
        with open(output_file, "w") as f:
            json.dump(self.symbol_table, f, indent=2)

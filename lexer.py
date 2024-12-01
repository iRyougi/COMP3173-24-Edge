import re
import json
import sys

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.current_position = 0
        self.symbol_table = {}

    def tokenize(self):
        token_specification = [
            # Keywords, matched only if not followed by a lowercase letter, digit, or underscore
            ("KEYWORD", r'\b(let|be|show|int|set)(?![a-z_0-9])'),  
            ("NUMBER", r'\d+'),  # Numbers
            ("ID", r'[a-z_][a-z_]*'),  # Identifiers with lowercase letters only
            ("PUNCTUATION", r'[{}().,:]'),
            ("ARITH_OP", r'[+\-*]'),
            ("REL_OP", r'[<>@=]'),
            ("LOGIC_OP", r'[&|!]'),
            ("SET_OP", r'[UI]'),  # Assuming 'U' and 'I' are valid set operators
            ("SKIP", r'[ \t\n]+'),  # Skip spaces, tabs, and newlines
            ("MISMATCH", r'.'),  # Catch-all for any other character
        ]
        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        get_token = re.compile(token_regex).match
        line = self.source_code

        # 调试用输入信息
        # print(f"Source code for tokenization:\n{line}\n")

        mo = get_token(line)
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group()

            if kind == "SKIP":
                pass  # Ignore whitespace
            elif kind == "MISMATCH":
                # Handle the lexical error
                print("Lexical Error!")
                with open("lexer_out.json", "w") as json_file:
                    json.dump([], json_file)
                sys.exit(0)
            else:
                if kind == "NUMBER":
                    # value = int(value) #保持字符串格式
                    self.tokens.append({"token": "num", "lexeme": value})
                elif kind == "ID":
                    if value not in self.symbol_table:
                        self.symbol_table[value] = {"type": None, "value": None}
                    self.tokens.append({"token": "id", "lexeme": value})
                elif kind == "KEYWORD":
                    self.tokens.append({"token": value, "lexeme": value})
                else:
                    self.tokens.append({"token": value, "lexeme": value})

            mo = get_token(line, mo.end())

        # Debug output to verify tokenization 调试使用
        # print("Tokens found:", self.tokens)
        return self.tokens


    def next_token(self):
        if self.current_position < len(self.tokens):
            token = self.tokens[self.current_position]
            self.current_position += 1
            return token
        return None

    def get_symbol_table(self):
        # Debug output to verify symbol table content
        # print("Symbol table:", self.symbol_table)
        return self.symbol_table

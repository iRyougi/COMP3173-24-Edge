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
            ("KEYWORD", r'\b(let|be|show|int|set)\b'),
            ("PUNCTUATION", r'[{}().,:]'),
            ("ARITH_OP", r'[+\-*]'),
            ("REL_OP", r'[<>@=]'),
            ("LOGIC_OP", r'[&|!]'),
            ("SET_OP", r'[UI]'),
            ("NUMBER", r'\b\d+\b'),
            ("ID", r'\b[a-z]+\b'),
            ("SKIP", r'[ \t\n]+'),  # Skip spaces, tabs, and newlines
            ("MISMATCH", r'.'),
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
            
            if kind == "MISMATCH":
                # If there is a mismatch, handle the lexical error
                print("Lexical Error!")
                # Create an empty JSON file called lexer_output.json
                with open("lexer_out.json", "w") as json_file:
                    json.dump([], json_file)
                # Exit the program with code 0
                sys.exit(0)

            # Only add to tokens if it's not a SKIP or MISMATCH
            if kind == "NUMBER":
                value = int(value)
                self.tokens.append({"token": "num", "lexeme": value})
            elif kind == "ID":
                if value not in self.symbol_table:
                    self.symbol_table[value] = {"type": None, "value": None}
                self.tokens.append({"token": "id", "lexeme": value})
            elif kind == "KEYWORD":
                # Keywords are directly used as the token value
                self.tokens.append({"token": value, "lexeme": value})
            elif kind == "PUNCTUATION":
                self.tokens.append({"token": value, "lexeme": value})
            elif kind == "REL_OP":
                self.tokens.append({"token": value, "lexeme": value})
            elif kind == "ARITH_OP":
                self.tokens.append({"token": value, "lexeme": value})
            elif kind == "LOGIC_OP":
                self.tokens.append({"token": value, "lexeme": value})
            elif kind == "SET_OP":
                self.tokens.append({"token": value, "lexeme": value})

            # Move to the next match
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

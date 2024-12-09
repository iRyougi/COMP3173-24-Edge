# type_checker.py
import json
from typing import List, Optional, Dict, Any


class ParseTreeNode:
    def __init__(
        self,
        name: Optional[str] = None,
        token: Optional[str] = None,
        lexeme: Optional[str] = None,
    ):
        self.name = name  # 非终结符名称
        self.token = token  # 终结符令牌
        self.lexeme = lexeme  # 终结符词素
        self.children: List["ParseTreeNode"] = []  # 子节点列表
        self.type: Optional[str] = None  # 节点类型

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ParseTreeNode":
        if "token" in data:
            node = ParseTreeNode(token=data["token"], lexeme=data["lexeme"])
            node.type = data.get("type")
        else:
            node = ParseTreeNode(name=data["name"])
            node.type = data.get("type")
            for child in data.get("children", []):
                node.children.append(ParseTreeNode.from_dict(child))
        return node

    def to_dict(self) -> Dict[str, Any]:
        if self.token:
            # 终结符节点
            return {"token": self.token, "lexeme": self.lexeme, "type": self.type}
        else:
            # 非终结符节点
            return {
                "name": self.name,
                "type": self.type,
                "children": [child.to_dict() for child in self.children],
            }


class SymbolTable:
    def __init__(self):
        self.table: Dict[str, Dict[str, Any]] = {}

    def add(self, var_name: str, var_type: str):
        self.table[var_name] = {
            "type": var_type,
            "value": None,  # 初始值为 None，实际实现中可扩展
        }

    def lookup(self, var_name: str) -> Optional[str]:
        if var_name in self.table:
            return self.table[var_name]["type"]
        else:
            return None


KEYWORDS = {"let", "be", "show", "int", "set", "simplify"}
# 定义标点符号集合，根据您的lexer正则表达式
PUNCTUATION = {".", "{", "}", "(", ")", ":", ";"}


class TypeChecker:
    def __init__(self, root: ParseTreeNode):
        self.root = root
        self.symbol_table = SymbolTable()
        self.type_error_found = False

    def type_check(self) -> bool:
        self._check_node(self.root)
        return not self.type_error_found

    def _check_node(self, node: ParseTreeNode):
        if node.token:
            # 处理终结符节点
            if node.token == "num":
                node.type = "integer"
            elif node.token == "id":
                var_type = self.symbol_table.lookup(node.lexeme)
                if var_type:
                    node.type = var_type
                else:
                    node.type = "type_error"
                    self.type_error_found = True
            elif node.token in ["<", ">", "=", "@"]:
                node.type = "relation"
            elif node.token in ["&", "|", "!"]:
                node.type = "predicate"
            elif node.token in ["U", "I", "+", "-", "*"]:
                node.type = "operator"
            elif node.token in KEYWORDS:
                node.type = "void"
            elif node.token in PUNCTUATION:
                node.type = "void"
            else:
                node.type = None  # 其他终结符，如标点符号，不赋类型
        else:
            # 处理非终结符节点，递归检查子节点
            for child in node.children:
                self._check_node(child)

            # 应用类型检查规则
            if node.name == "S":
                # 规则 0, 1, 2
                if len(node.children) == 3:
                    # S -> D' C .
                    D_prime, C, dot = node.children
                    if D_prime.type != "type_error" and C.type != "type_error":
                        node.type = "program"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
                elif len(node.children) == 2:
                    # S -> C .
                    C, dot = node.children
                    node.type = C.type
            elif node.name == "D'":
                if len(node.children) == 2:
                    # D'1 -> D D'2
                    D, D_prime2 = node.children
                    if D.type == "declaration" and D_prime2.type == "declarations":
                        node.type = "declarations"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
                elif len(node.children) == 1:
                    # D' -> D
                    D = node.children[0]
                    if D.type == "declaration":
                        node.type = "declarations"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "D":
                # D -> let T id be E .
                if len(node.children) == 6:
                    let, T, id_node, be, E, dot = node.children
                    if E.type != "type_error":
                        var_type = T.type
                        self.symbol_table.add(id_node.lexeme, var_type)
                        node.type = "declaration"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "T":
                # T -> int | set
                if len(node.children) == 1:
                    token_node = node.children[0]
                    if token_node.token == "int":
                        node.type = "integer"
                    elif token_node.token == "set":
                        node.type = "set"
            elif node.name == "C":
                # C -> show A
                if len(node.children) == 2:
                    show, A = node.children
                    if A.type != "type_error":
                        node.type = A.type
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "A":
                # A -> E | P
                if len(node.children) == 1:
                    A_child = node.children[0]
                    if A_child.type != "type_error":
                        node.type = "calculation"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "E":
                # E -> E'
                if len(node.children) == 1:
                    E_prime = node.children[0]
                    node.type = E_prime.type
            elif node.name == "E1":
                # E1 -> E2 U E' | E2 + E' | E2 - E' | E2 * E'
                if len(node.children) == 3:
                    E2, op, E_prime = node.children
                    if op.token == "U":
                        if E2.type == "set" and E_prime.type == "set":
                            node.type = "set"
                        else:
                            node.type = "type_error"
                            self.type_error_found = True
                    elif op.token in ["+", "-"]:
                        if E2.type == "integer" and E_prime.type == "integer":
                            node.type = "integer"
                        else:
                            node.type = "type_error"
                            self.type_error_found = True
                    elif op.token == "*":
                        if E2.type == "integer" and E_prime.type == "integer":
                            node.type = "integer"
                        else:
                            node.type = "type_error"
                            self.type_error_found = True
            elif node.name == "E'":
                # E' -> E'' | E'2 I E''
                if len(node.children) == 1:
                    E_double_prime = node.children[0]
                    node.type = E_double_prime.type
                elif len(node.children) == 3:
                    E_prime2, I_op, E_double_prime = node.children
                    if E_prime2.type == "set" and E_double_prime.type == "set":
                        node.type = "set"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "E''":
                # E'' -> num | id | ( E ) | { Z P }
                if len(node.children) == 1:
                    child = node.children[0]
                    if child.token:
                        if child.token == "num":
                            node.type = "integer"
                        elif child.token == "id":
                            var_type = self.symbol_table.lookup(child.lexeme)
                            if var_type:
                                node.type = var_type
                            else:
                                node.type = "type_error"
                                self.type_error_found = True
                    else:
                        # { Z P }
                        Z, P = node.children
                        if P.type == "predicate":
                            node.type = "set"
                        else:
                            node.type = "type_error"
                            self.type_error_found = True
                elif len(node.children) == 3:
                    # ( E )
                    _, E, _ = node.children
                    node.type = E.type
                elif len(node.children) == 3 and node.children[0].token == "{":
                    # { Z P }
                    Z, P = node.children[1], node.children[2]
                    if P.type == "predicate":
                        node.type = "set"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "Z":
                # Z -> id :
                if len(node.children) == 2:
                    id_node, colon = node.children
                    # 在类型检查规则中，代表符号的类型是 integer
                    self.symbol_table.add(id_node.lexeme, "integer")
                    node.type = "void"
            elif node.name == "P":
                # P -> P'
                if len(node.children) == 1:
                    P_prime = node.children[0]
                    node.type = P_prime.type
            elif node.name == "P1":
                # P1 -> P2 | P'
                if len(node.children) == 3:
                    P2, or_op, P_prime = node.children
                    if P2.type == "predicate" and P_prime.type == "predicate":
                        node.type = "predicate"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "P'":
                # P' -> P'' | P'2 & P''
                if len(node.children) == 1:
                    P_double_prime = node.children[0]
                    node.type = P_double_prime.type
                elif len(node.children) == 3:
                    P_prime2, and_op, P_double_prime = node.children
                    if (
                        P_prime2.type == "predicate"
                        and P_double_prime.type == "predicate"
                    ):
                        node.type = "predicate"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "P''":
                # P'' -> R | ( P ) | ! R
                if len(node.children) == 1:
                    R = node.children[0]
                    if R.type == "relation":
                        node.type = "predicate"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
                elif len(node.children) == 3:
                    # ( P )
                    _, P, _ = node.children
                    node.type = P.type
                elif len(node.children) == 2:
                    # ! R
                    not_op, R = node.children
                    if R.type == "relation":
                        node.type = "predicate"
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
            elif node.name == "R":
                # R -> E1 < E2 | E1 > E2 | E1 = E2 | E1 @ E2
                if len(node.children) == 3:
                    E1, op, E2 = node.children
                    if op.token in ["<", ">", "="]:
                        if E1.type == "integer" and E2.type == "integer":
                            node.type = "relation"
                        else:
                            node.type = "type_error"
                            self.type_error_found = True
                    elif op.token == "@":
                        if E1.type == "integer" and E2.type == "set":
                            node.type = "relation"
                        else:
                            node.type = "type_error"
                            self.type_error_found = True

    def serialize_tree(node: ParseTreeNode) -> Any:
        return node.to_dict()

    def write_typing_out(
        tree: Optional[ParseTreeNode], filename: str = "typing_out.json"
    ):
        if tree is None:
            # 写入空的 JSON 文件
            with open(filename, "w") as f:
                json.dump([], f)
        else:
            # 写入包含类型信息的解析树
            tree_dict = TypeChecker.serialize_tree(tree)
            with open(filename, "w") as f:
                json.dump(tree_dict, f, indent=4)


def load_parse_tree(filename: str) -> Optional[ParseTreeNode]:
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            # 假设 data 是一个字典格式的解析树
            if isinstance(data, dict):
                return ParseTreeNode.from_dict(data)
            else:
                print(
                    "Error: The parser_out.json does not contain a single dictionary as the parse tree root."
                )
                return None
    except Exception as e:
        print(f"Error reading parse tree: {e}")
        return None


def type_check_with_error_handling(
    root: ParseTreeNode, filename: str = "typing_out.json"
) -> bool:
    type_checker = TypeChecker(root)
    success = type_checker.type_check()
    if success:
        print("Semantic Analysis Complete!")
        TypeChecker.write_typing_out(root, filename)
    else:
        print("Type Error!")
        TypeChecker.write_typing_out(None, filename)
    return success


def main_type_checker():
    # 这部分通常不会被调用，因为主函数在 main.py 中
    pass

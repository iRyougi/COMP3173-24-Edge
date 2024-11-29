import sys
import json
from lexer import Lexer
from parser import SLRParser,Token
from semantic import SemanticAnalyzer

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        return

    # 获取输入文件名
    input_file = sys.argv[1]
    try:
        # 读取源代码文件
        with open(input_file, "r") as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return

    # Step 1: 词法分析
    print("Performing Lexical Analysis...")
    lexer = Lexer(source_code)
    try:
        lexer.tokenize()  # 生成 Token
        lexer.save_tokens("output/lexer_out.json")  # 保存 Token 到 output/lexer_out.json
        lexer.save_symbol_table("output/symbol_table.json")  # 保存符号表
    except ValueError as e:
        print(f"Lexical Error: {e}")  # 捕获词法错误
        return
    print("Lexical Analysis Completed!")

    # Step 2: 语法分析
    print("Performing Syntax Analysis...")
    try:
        # 从 lexer_out.json 加载 Tokens
        with open("output/lexer_out.json", "r") as file:
            tokens = json.load(file)
            raw_tokens=tokens
            # 打印查看输入的 tokens
            for token in raw_tokens:
                print(token)
        # 将 raw_tokens 转换为 Token 对象
        tokens = [Token(token=t['token'], lexeme=t['lexeme']) for t in raw_tokens]

        # 读取解析表
        slr_table_file = "slr_table.csv"  # 文件路径

        # 使用字典创建 SLRParser 实例
        parser = SLRParser(slr_table_file)  # 传递字典

        # 使用加载的 SLR 解析表进行语法分析
        parser.parse(tokens)
        parser.save_syntax_tree("output/parser_out.json")  # 保存语法树到 output/parser_out.json

    except ValueError as e:
        print(f"Syntax Error: {e}")  # 捕获语法错误
        return

    print("Syntax Analysis Completed!")
    # Step 3: 语义分析
    print("Performing Semantic Analysis...")
    try:
        # 从 parser_out.json 和 symbol_table.json 加载数据
        with open("output/parser_out.json", "r") as file:
            syntax_tree = json.load(file)
        with open("output/symbol_table.json", "r") as file:
            symbol_table = json.load(file)

        # 进行语义分析
        analyzer = SemanticAnalyzer(syntax_tree, symbol_table)
        analyzer.analyze()
        analyzer.save_typing_output("output/typing_out.json")  # 保存语义分析结果到 output/typing_out.json

        # 如果你有评估计算步骤，可以在这里添加：
        analyzer.save_evaluation_output("output/evaluation_out.json")  # 保存评估结果到 output/evaluation_out.json

    except ValueError as e:
        print(f"Semantic Error: {e}")  # 捕获语义错误
        return
    print("Semantic Analysis Completed!")

if __name__ == "__main__":
    main()
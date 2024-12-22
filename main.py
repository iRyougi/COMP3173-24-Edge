import argparse
import json
from lexer import Lexer
from parser import (
    SLRParser,
    load_parsing_table,
)  # Assuming parser.py and this file are in the same directory
from type_checker import (
    TypeChecker,
)  # 导入类型检查器功能


def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(
        description="Run lexer and parser on a source code file."
    )
    parser.add_argument("input_file", help="The input file containing source code.")
    args = parser.parse_args()

    # Step 1: 词法分析
    # 读取指定的输入文件
    try:
        with open(args.input_file, "r") as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{args.input_file}' was not found.")
        return

    # 创建 Lexer 实例并进行词法分析
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # 将 token 信息保存为 JSON 格式到 lexer_out.json 文件
    with open("lexer_out.json", "w") as json_file:
        json.dump(tokens, json_file, indent=2)
    print("Lexical Analysis Complete!")  # 调试用代码，显示文件输出

    # Step 2: 语法分析
    # 读取解析表 (固定路径为 'SLR Parsing Table.csv')
    action_table, goto_table = load_parsing_table("SLR Parsing Table.csv")

    # 创建 SLRParser 实例并进行语法分析
    parser = SLRParser(tokens, action_table, goto_table)
    parser.parse()

    # Step 3: 语义分析（类型检查）
    # 假设文件路径如下，你可以根据实际情况修改
    parser_out_path = "parser_out.json"
    typing_out_path = "typing_out.json"

    # 创建 TypeChecker 实例
    type_checker = TypeChecker(parser_out_path, typing_out_path)

    try:
        # 加载 AST
        type_checker.load_ast()
        if type_checker.type_error_flag:
            print("Type Error!")
        else:
            # 运行类型检查
            type_checker.type_check()
            if type_checker.type_error_flag:
                print("Type Error!")
            else:
                print("Semantic Analysis Complete!")
    except Exception as e:
        # 捕获任何未预见的异常
        # debug_log(f"Unexpected error: {e}")
        type_checker.type_error_flag = True
        print("Type Error!")
    finally:
        # 根据 type_error_flag 写出 typing_out.json
        type_checker.write_typing_json()
        # debug_log("Type checking phase finished.")


if __name__ == "__main__":
    main()

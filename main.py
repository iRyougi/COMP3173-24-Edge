import argparse
import json
from lexer import Lexer
from parser import SLRParser, load_parsing_table  # Assuming parser.py and this file are in the same directory

def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="Run lexer and parser on a source code file.")
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
    print("Lexical Analysis Complete!") #调试用代码，显示文件输出

    # Step 2: 语法分析
    # 读取解析表 (固定路径为 'SLR Parsing Table.csv')
    action_table, goto_table = load_parsing_table("SLR Parsing Table.csv")

    # 创建 SLRParser 实例并进行语法分析
    parser = SLRParser(tokens, action_table, goto_table)
    parser.parse()

    # Step 3: Working

if __name__ == "__main__":
    main()

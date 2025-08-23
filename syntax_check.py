#!/usr/bin/env python3
import ast
import sys

def check_syntax(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Try to parse the AST
        ast.parse(content)
        print(f"✅ {filename} has valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax Error in {filename}:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return False

if __name__ == "__main__":
    check_syntax("automated_appfolio_builder.py")

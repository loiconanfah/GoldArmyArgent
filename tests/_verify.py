import ast
try:
    src = open('agents/mentor.py', encoding='utf-8').read()
    ast.parse(src)
    print('OK - syntax valid')
    if "{behavior: 'smooth'}" in src and "{{behavior" not in src:
        print('WARNING: unescaped brace still found in f-string context')
    else:
        print('OK - no f-string brace issue')
except SyntaxError as e:
    print(f'SYNTAX ERROR: {e}')

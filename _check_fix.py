content = open('agents/mentor.py', encoding='utf-8').read()
old = "{behavior: 'smooth'}"
new = "{{behavior: 'smooth'}}"
if new in content:
    print('OK - fix already in place')
elif old in content:
    print('BUG PRESENT - applying fix now...')
    open('agents/mentor.py', 'w', encoding='utf-8').write(content.replace(old, new, 1))
    print('FIXED.')
else:
    print('pattern not found, searching...')
    for i, line in enumerate(content.splitlines()):
        if 'behavior' in line.lower():
            print(f'  line {i+1}: {repr(line[:120])}')

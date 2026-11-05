from pathlib import Path
import re

source = Path(__file__).with_name("legacy_expanded.c").read_text()

array = source.split("struct s*a[1024]={", 1)[1].split("};", 1)[0]

elements = array.split(",")

characters = []

for i, el in enumerate(elements[:52]):
    length = len(re.findall(r"\bz\s*\(", el))

    operation = i % 7
    if operation == 0:
        code = length ^ 99
    elif operation == 1:
        code = length ^ 48
    elif operation == 2:
        code = length // 16
    elif operation == 3:
        code = length // 4
    elif operation == 4:
        code = length // 55
    elif operation == 5:
        code = length - 97
    else:
        code = length - 44

    character = chr(code)
    characters.append(character)
    print(i, length, code, repr(character))

print("".join(characters))

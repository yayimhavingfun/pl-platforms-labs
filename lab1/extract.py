from pathlib import Path
import re

source = Path(__file__).with_name("legacy_manual.c").read_text()

match = re.search(
    r"struct\s+s\s*\*\s*a\s*\[1024\]\s*=\s*\{(.*?)\};",
    source,
    re.DOTALL,
)

elements = match.group(1).split(",")

numbers = []
for element in elements:
    if element.strip():
        count = len(re.findall(r"\bz\s*\(", element))
        numbers.append(count)

print("static const int expected[1024] = {")
for start in range(0, len(numbers), 7):
    row = numbers[start:start + 7]
    print("    " + ", ".join(map(str, row)) + ",")
print("};")
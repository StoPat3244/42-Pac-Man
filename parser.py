import json

def remove_comments(text):
    lines = []

    for line in text.splitlines():
        in_string = False
        escaped = False
        output = []

        for char in line:
            if char == '"' and not escaped:
                in_string = not in_string

            if char == '#' and not in_string:
                break

            output.append(char)

            escaped = char == '\\' and not escaped

        lines.append(''.join(output))

    return '\n'.join(lines)


with open("config.json") as f:
    text = f.read()

data = json.loads(remove_comments(text))

print(data)

##################################################################################### another example

import json

with open("config.json") as f:
    lines = [line for line in f if not line.lstrip().startswith("#")]

data = json.loads("".join(lines))

print(data["width"])  # 4

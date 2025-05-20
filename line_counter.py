import os

SRC_PATH = "src"
lines = 0
for dirpath, dirnames, filenames in os.walk(SRC_PATH):
    for filename in filenames:
        if not filename.endswith(".py"):
            continue
        filepath = os.path.join(dirpath, filename)
        print(filepath)
        with open(filepath, "r") as file:
            lines_count = 0
            for line in file.readline():
                lines_count += 1
            lines += lines_count
print(lines)

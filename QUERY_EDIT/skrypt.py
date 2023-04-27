import re
from os import listdir, path

pattern = r"(?P<name>[\w#]+) [(](?P<primary_key>PK, )?(?P<type>[\w(,)]+?), (?P<nullable>.+?)[)]"
line_pattern = re.compile(pattern)
dir_path = path.dirname(path.realpath(__file__))

files_to_process = [file for file in listdir(dir_path) if file.endswith(".txt") and not(file.startswith("POST_"))]

for file in files_to_process:
    with open(f"POST_{file}", "w", encoding="utf-8") as target:
        with open(file, "r", encoding="utf-8") as source:
            lines = source.readlines()
            for line in lines:
                finding = re.search(line_pattern, line)
                try:
                    target.write(f'[{finding.group("name")}] {finding.group("type")} {finding.group("nullable").upper()},\n')
                except (AttributeError):
                    # NoneType has no attribute 'group' - if no match
                    pass

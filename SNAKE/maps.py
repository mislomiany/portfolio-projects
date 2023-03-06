import my_globals
import re

file_path = __file__ + "\\..\\maps\\"
map_name = "map"

pattern = re.compile(r"\b([0x]+)\b")

def load_map(name: str):
    map_file = open(file_path + map_name + ".txt", "r", encoding="utf-8")
    contents = map_file.read()
    map_lines = re.findall(pattern, contents)
    map_rows = len(map_lines)
    map_cols = len(map_lines[0])
    for line in map_lines[1:]:
        assert len(line) == map_cols, "Map should be a rectangle"

    print("#" * 40)
    print("Map loaded successfully!")
    print("Columns:", map_cols)
    print("Rows:", map_rows)
    print("Size set to",my_globals.SIZE)
    print("It will run in", my_globals.SIZE * map_cols,"x",my_globals.SIZE * map_rows)
    print("#" * 40)

    coordinates = []
    for r in range(map_rows):
            for c in range(map_cols):
                if map_lines[r][c] == "x":
                    coordinates.append((c * my_globals.SIZE, r * my_globals.SIZE))

    return ((my_globals.SIZE * map_cols, my_globals.SIZE * map_rows), coordinates)


if __name__ == "__main__":
    print("Map generation testing")
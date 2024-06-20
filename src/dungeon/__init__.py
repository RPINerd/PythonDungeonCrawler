import importlib
import os

files = os.listdir(os.path.join("src", "dungeon"))
for file in files:
    if file[-3:] == ".py" and file[:2] != "__":
        module_name = file[:-3]
        module = importlib.import_module(f"src.dungeon.{module_name}")
        globals().update(vars(module))

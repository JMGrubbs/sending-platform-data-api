from pathlib import Path
import toml

try:
    config = toml.load(Path(__file__).parent / "config.toml")
except FileNotFoundError:
    raise FileNotFoundError("config.toml not found. File expected in the same directory as settings.py")

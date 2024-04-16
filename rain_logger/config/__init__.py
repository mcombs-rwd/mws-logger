# __init__.py
import pathlib
import tomllib

path = pathlib.Path(__file__).parent / "rain_logger.toml"
with path.open(mode="rb") as fp:
    rain_logger = tomllib.load(fp)

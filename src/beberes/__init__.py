"""beberes: Tidy up messy Indonesian spreadsheets."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("beberes")
except PackageNotFoundError:  # jalan dari source tanpa install
    __version__ = "0.0.0"

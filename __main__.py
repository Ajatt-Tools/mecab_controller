# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import sys

from .mecab_controller import MecabController


def main() -> None:
    """Print an Anki-style reading for the expression supplied on the command line."""
    mecab = MecabController(verbose=False)
    print(mecab.reading(" ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()

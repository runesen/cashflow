"""Holds class with different paths."""
from dataclasses import dataclass
from pathlib import Path
import budget

@dataclass
class Directories:
    """Class with all paths used in the repository."""

    repo = Path(budget.__file__).parent.parent
    module = Path(budget.__file__).parent
    plots = repo / "plots"
"""Holds class with different paths."""
from dataclasses import dataclass
from pathlib import Path
import flow

@dataclass
class Directories:
    """Class with all paths used in the repository."""

    repo = Path(flow.__file__).parent.parent
    module = Path(flow.__file__).parent
    plots = repo / "plots"
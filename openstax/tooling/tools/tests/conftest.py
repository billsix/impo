"""Make the converter modules importable from the tests without a package install.

The converter is an in-repo tool (not a distributed package), so its modules live
under tools/cnxml2tex and tools/pandoc rather than on sys.path. Add those dirs so
`import convert` / `import preprocess` / `import fetch_exercises` resolve. Importing
convert.py is side-effect-free here: its module-level globals glob collections/*.xml
(returning [] when run outside a bundle) and touch no network.
"""

from __future__ import annotations

import os
import sys

_HERE: str = os.path.dirname(os.path.abspath(__file__))
_TOOLS: str = os.path.dirname(_HERE)
_d: str
for _d in (os.path.join(_TOOLS, "cnxml2tex"), os.path.join(_TOOLS, "pandoc")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

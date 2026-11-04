#!/usr/bin/env python3
"""Set which version of the quiz template this book loads (book.json).

    python3 tools/set_template_tag.py 3        # newest 3.x.x
    python3 tools/set_template_tag.py 3.1.0    # exactly 3.1.0

index.html reads "templateVersion" from book.json and loads its code from
that version of eckko/recall-quiz-site-template on jsDelivr. A major version
such as 3 follows the newest 3.x.x release; an exact version such as 3.1.0
never changes. Never use a branch name. Commit the changed book.json
afterwards.
"""

import json
import re
import sys
from pathlib import Path

BOOK_FILE = Path(__file__).resolve().parent.parent / "book.json"
VERSION_PATTERN = re.compile(r"^\d+(\.\d+){0,2}$")


def read_settings():
    """The settings in book.json, or an empty dict when it is missing."""
    if not BOOK_FILE.exists():
        return {}
    return json.loads(BOOK_FILE.read_text(encoding="utf-8"))


def main():
    """Write the version given on the command line into book.json."""
    if len(sys.argv) != 2 or not VERSION_PATTERN.match(sys.argv[1]):
        sys.exit("Usage: python3 tools/set_template_tag.py 3 (a major "
                 "version) or 3.1.0 (an exact version), not a branch")
    settings = read_settings()
    settings["templateVersion"] = sys.argv[1]
    BOOK_FILE.write_text(json.dumps(settings, indent=2) + "\n",
                         encoding="utf-8")
    print(f"book.json now loads the template at version {sys.argv[1]}")


if __name__ == "__main__":
    main()

"""
Checks the types chancy exposes to applications, now that it ships
``py.typed``.

``tests/typing/public_api.py`` uses the public API the way downstream code
does. Running mypy over it catches signatures that would reject valid calls,
accept invalid ones, or silently degrade to ``Any``.
"""

from pathlib import Path

import pytest

mypy_api = pytest.importorskip("mypy.api")

PUBLIC_API = Path(__file__).parent / "typing" / "public_api.py"


def test_public_api_types():
    stdout, stderr, status = mypy_api.run(
        [
            str(PUBLIC_API),
            "--warn-unused-ignores",
            # Only report errors in the file above, as a downstream project's
            # mypy would, not in chancy's own implementation.
            "--follow-imports=silent",
            "--no-incremental",
        ]
    )
    assert status == 0, stdout + stderr

"""Compatibility import for the shared README-context publisher.

Current documentation uses ``engineering.readme_context``. Historical numerical
reproduction continues to use the exact sources in its pinned checkout.
"""
import sys
from engineering import readme_context as _shared

if __name__ == '__main__':
    raise SystemExit(_shared.main())
sys.modules[__name__] = _shared

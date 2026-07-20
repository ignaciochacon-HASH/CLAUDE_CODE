#!/usr/bin/env python3
"""Convert a file or URL to Markdown using MarkItDown and print it to stdout."""

import sys


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path-or-url>", file=sys.stderr)
        return 2

    source = sys.argv[1]

    try:
        from markitdown import MarkItDown
    except ImportError:
        print(
            "markitdown is not installed. Run: pip install 'markitdown[all]'",
            file=sys.stderr,
        )
        return 1

    try:
        result = MarkItDown().convert(source)
    except Exception as exc:  # noqa: BLE001 - surface any conversion failure to the caller
        print(f"failed to convert '{source}': {exc}", file=sys.stderr)
        return 1

    print(result.text_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

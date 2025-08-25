#!/usr/bin/env python3
"""
Legacy wrapper for namespace-aware ingestion.
Prefer: kk ingest <dir> [--env ...] [--dry-run]
"""

import sys
from kkcli.__main__ import main as kk_main


def main():
    # Map to: kk ingest <dir> [--dry-run]
    argv = ["ingest"]
    args = sys.argv[1:]
    argv.extend(args)
    return kk_main(argv)


if __name__ == "__main__":
    sys.exit(main())

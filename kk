#!/usr/bin/env python3
import sys

try:
    from kkcli.__main__ import main
except Exception as e:
    sys.stderr.write("Failed to import kk CLI. Did you install dependencies?\n")
    raise

if __name__ == "__main__":
    sys.exit(main())

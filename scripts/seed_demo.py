#!/usr/bin/env python3
"""Pre-seed the deployed instance with demo crawl data."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import load_seeds, run_crawl


def main() -> None:
    seeds_file = Path(__file__).parent.parent / "demo_seeds.txt"
    seeds = load_seeds(str(seeds_file))
    print(f"Seeding demo with {len(seeds)} URLs...")
    saved = asyncio.run(run_crawl(seeds))
    print(f"Done — {saved} articles saved.")


if __name__ == "__main__":
    main()

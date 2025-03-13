#!/usr/bin/env python
"""
Run bot

This script runs bot in a long-running process.

"""
import asyncio
from edu_meet_bot.main import start_bot


def main() -> None:
    """
    Main entry point for running bot.

    Runs bot in a long-running process.
    """
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()

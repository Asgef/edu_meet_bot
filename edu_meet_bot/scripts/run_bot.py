#!/usr/bin/env python
import asyncio
from edu_meet_bot.main import start_bot


def main() -> None:
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()

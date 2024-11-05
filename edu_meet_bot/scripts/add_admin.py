#!/usr/bin/env python
import asyncio
from argparse import ArgumentParser

from edu_meet_bot.admin.errors import UserAlreadyAdmin
from edu_meet_bot.admin.service import make_user_admin
from edu_meet_bot.db import async_session

parser = ArgumentParser("Utility for adding admin for shop telegram bot")
parser.add_argument("id", type=int)


async def add_admin(admin_id: int):
    async with async_session() as session:
        try:
            await make_user_admin(admin_id)
        except UserAlreadyAdmin:
            print("This user is already admin")
        print("Succesfully added user to admins")


def main():
    admin_id = parser.parse_args().id
    asyncio.run(add_admin(admin_id))


if __name__ == "__main__":
    main()

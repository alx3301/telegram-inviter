from random import uniform
from asyncio import run, sleep
from os import system, name, path, makedirs, listdir, remove
from pyrogram import Client
from pyrogram.errors import (
    UserAlreadyParticipant,
    UserPrivacyRestricted,
    UserNotMutualContact,
    UserIsBlocked,
    PeerFlood,
    FloodWait)

class TelegramInviter:
    SESSIONS_PATH = "sessions"

    def __init__(self):
        if not path.exists(self.SESSIONS_PATH):
            makedirs(self.SESSIONS_PATH)

        self.client = None
        self.source_id = None
        self.members_ids = []
        self.last_index = 0
        self.destination_id = None
        self.sessions = listdir(self.SESSIONS_PATH)

        self.commands = {
            "/exit": self.shutdown,
            "/start": self.start_inviting,
            "/clear": self.clear_screen,
            "/set_source_id": self.set_source_id,
            "/set_destination_id": self.set_destination_id,
            "/add_session": self.add_session,
            "/show_dialogs": self.show_dialogs,
            "/show_sessions": self.show_sessions,
            "/delete_session": self.delete_session,
        }

    @staticmethod
    async def clear_screen():
        system("cls" if name == "nt" else "clear")

    async def shutdown(self):
        await self.clear_screen(); exit(0)

    async def set_source_id(self, input_):
        try:
            self.source_id = int(input_)
            print(f"Source ID has been successfully set to: {self.source_id}")
        except ValueError:
            print("Error: Invalid source ID. Please make sure it is a number.")

    async def set_destination_id(self, input_):
        try:
            self.destination_id = int(input_)
            print(f"Destination ID has been successfully set to: {self.destination_id}")
        except ValueError:
            print("Error: Invalid destination ID. Please make sure it is a number.")

    async def delete_session(self, session_name, silent=False):
        try:
            remove(f"{self.SESSIONS_PATH}/{session_name}.session")
            self.sessions = listdir(self.SESSIONS_PATH)
        except FileNotFoundError:
            print(f"Error: Session with name {session_name} not found.")
        else:
            if not silent:
                print(f"Session {session_name} has been successfully deleted.")

    async def add_session(self):
        try:
            self.client = Client(
                lang_code="ru",
                sleep_threshold=0,
                device_model="SM-S928B",
                workdir=self.SESSIONS_PATH,
                api_id=input("Enter api_id: "),
                api_hash=input("Enter api_hash: "),
                name=input("Enter session name: "),
            )
        except ValueError:
            print("Error: Invalid values provided. Please try again.")
            return
        try:
            async with self.client:
                await self.client.get_me()
                self.sessions = listdir(self.SESSIONS_PATH)
                print("Session added and authorized successfully.")
        except Exception as e:
            print(f"Error: Authorization failed. Details: {e}")
            await self.delete_session(self.client.name, silent=True)

    async def show_sessions(self):
        if self.sessions:
            print("Available sessions:")
            for session in self.sessions:
                print(f"- {session.split(".")[0]}")
        else:
            print("No sessions found.")

    async def show_dialogs(self, session_name):
        self.client = Client(session_name, workdir=self.SESSIONS_PATH)
        async with self.client:
            async for dialog in self.client.get_dialogs():
                if dialog.chat.title:
                    print(f"Title: {dialog.chat.title}, ID: {dialog.chat.id}")

    async def start_inviting(self):
        if self.sessions and self.source_id and self.destination_id:
            while True:
                for session in self.sessions:
                    self.client = Client(session.split(".")[0], workdir=self.SESSIONS_PATH)
                    async with self.client:
                        if not self.members_ids:
                            async for member in self.client.get_chat_members(self.source_id):
                                if not member.user.is_bot and not member.user.is_deleted:
                                    self.members_ids.append(member.user.id)
                        added_count = 0
                        while added_count < 3 and self.last_index < len(self.members_ids):
                            member_id = self.members_ids[self.last_index]
                            try:
                                await self.client.add_chat_members(self.destination_id, member_id)
                                print(f"Member {member_id} added to {self.destination_id}.")
                                await sleep(uniform(3, 5))
                                added_count += 1
                            except (UserAlreadyParticipant, UserPrivacyRestricted, UserNotMutualContact, UserIsBlocked):
                                pass
                            except (FloodWait, PeerFlood):
                                print("Flood limit reached. Switching session...")
                                await sleep(uniform(3,5))
                                break
                            finally:
                                self.last_index += 1

                if self.last_index >= len(self.members_ids):
                    print("All members added, starting over...")
                    self.last_index = 0

    async def parse_command(self, input_: str):
        parts = input_.strip().split()
        command = parts[0]

        if command in self.commands:
            if command in ["/set_source_id", "/set_destination_id", "/delete_session", "/show_dialogs"]:
                if len(parts) == 2:
                    await self.commands[command](parts[1])
                else:
                    print(f"Error: The {command} command requires exactly one argument!")
            elif self.commands[command] and len(parts) == 1:
                await self.commands[command]()
            elif len(parts) > 1:
                print(f"Error: The {command} command does not accept any arguments!")
            else:
                print(f"Error: The {command} command is not yet implemented.")
        else:
            print("Error: Unknown command. Please check your input and try again.")

    async def main(self):
        await self.clear_screen()
        while True:
            try:
                await self.parse_command(input("Command => "))
            except Exception as e:
                print(f"Unexpected error: {e}")

if __name__ == "__main__":
    telegram_inviter = TelegramInviter()
    try:
        run(telegram_inviter.main())
    except KeyboardInterrupt:
        run(telegram_inviter.shutdown())
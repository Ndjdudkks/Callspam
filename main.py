import asyncio, os

from pyrogram import Client, filters, types, compose
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, VideoPiped
from config import CHAT_LINK, API_ID, API_HASH, SESSION_STRING
from ses import sessions

app = Client(
    "basic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

apps: list["Client"] = []
calls: list["PyTgCalls"] = []

for a in sessions:
    apps.append(
        Client(
            a["Phone number"],
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=a["Token"],
            no_updates=True
        )
    )

@app.on_message(filters.regex("^join ") & filters.me & filters.reply)
async def joinChat(c: Client, m: types.Message):
    chat = m.text.split()[1].replace("@", "")
    chat_id = (await apps[-1].join_chat(chat)).id
    await m.edit("Wait ...")
    if m.reply_to_message.video:
        Type = VideoPiped
    elif m.reply_to_message.audio or m.reply_to_message.voice:
        Type = AudioPiped
    else:
        return await m.edit("rep to audio voice video")
    await m.edit("Downloading ....")
    path = await m.reply_to_message.download()
    await m.edit("Joining ..")
    for a in apps:
        try:
            await a.join_chat(chat)
        except:
            pass
    count = 0
    for call in calls:
        try:
            await call.join_group_call(
                chat_id=chat_id,
                stream=Type(path=path)
            )
            count += 1
        except:
            pass
    return await apps[0].send_message(m.chat.id, f"Successfully Joined to {chat_id}", reply_to_message_id=m.id)




@app.on_message(filters.command("start"))
def start_command(client, message):
    message.edit("Hello world!")



@app.on_message(filters.regex("^leave ") & filters.me)
async def leaveChat(c: Client, m: types.Message):
    chat = m.text.split()[1].replace("@", "")
    chat_id = (await apps[-1].join_chat(chat)).id
    for a in apps:
        try:
            await a.leave_chat(chat_id=chat_id)
        except:
            pass
    return await m.edit("Done")

async def main():
    await app.start()
    await compose(apps)
    count = 0
    for a in apps:
        call = PyTgCalls(a)
        try:
            await call.start()
            calls.append(call)
            await a.join_chat(CHAT_LINK)
            count += 1
        except:
            pass
    print(f"Started {count} session")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

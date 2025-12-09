import discord
from discord.ext import tasks
import requests

pastebin_raw = "https://pastebin.com/raw/PCSy25Fe"

client = discord.Client(intents=discord.Intents.all())


def check_status():
    try:
        data = requests.get(pastebin_raw).text.strip()
        # expected format: "false:username" or "true:anything"
        status, user = data.split(":", 1)
        return status.lower() == "false", user
    except:
        return False, "error"


@tasks.loop(hours=12)
async def notifier(channel_id):
    channel = client.get_channel(channel_id)
    if not channel:
        return

    banned, username = check_status()

    if banned:
        msg = f"🚨 **Account banned**\nNew user: **{username}**"
    else:
        msg = "✅ **Account fine**"

    embed = discord.Embed(description=msg, color=0x00FF00)
    await channel.send("@everyone", embed=embed)


def reload_logic():
    print("[Bot] Logic reloaded.")


def run_bot(token, channel_id, github_raw):
    @client.event
    async def on_ready():
        print("[Bot] Logged in as", client.user)
        notifier.start(channel_id)

    @client.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.content == ",notify":
            banned, username = check_status()
            if banned:
                msg = f"🚨 **Account banned**\nUser: **{username}**"
            else:
                msg = "✅ **Account fine**"
            await message.channel.send(msg)

        if message.content == ",update":
            await message.channel.send("Updating from GitHub…")
            # main.py will handle the update on next cycle

    client.run(token)

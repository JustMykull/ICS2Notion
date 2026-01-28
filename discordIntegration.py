import discord 
import asyncio
import sharedVars
from datetime import datetime
import pytz

TOKEN = sharedVars.getConfig("DISCORDBOT_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

timeNow = datetime.now()
Timezone = "US/Eastern"

logFile = "discordLogs.log"

reminderChannelID = 1412581741973082143
assignmentChannelID = 1412589036178112724
statusChannelId = 1411001176316575756


@client.event
async def on_ready():
    
    reminderChannel = client.get_channel(reminderChannelID)
    assignmentChannel = client.get_channel(assignmentChannelID)

    print(f"Logged in as {client.user}")
    await assignmentChannel.send(f"We up at: {await getCurrentTime(Timezone)}")

    try: 
        with open(logFile, "r") as f:
            logs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Log not found.")
        logs = []

    if assignmentChannel:
        for log in logs:
            await assignmentChannel.send(log)
    else:
        print("Channel not found.")

    with open(logFile, "w") as f:
        pass 

    await assignmentChannel.send(f"We down at: {await getCurrentTime(Timezone)}")
    await client.close()

async def getCurrentTime(Timezone: str):
    currentTime = timeNow.strftime("%Y-%m-%d %H:%M:%S")
    return currentTime

def runBot():
    client.run(TOKEN)

if __name__ == "__main__":
    runBot()
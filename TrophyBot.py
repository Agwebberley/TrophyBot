import discord
import time
import asyncio
import json

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
style.use("fivethirtyeight")

client = discord.Client()
token = open("token.txt", "r").read()
uw = {}



def community_report(guild):
    online = 0
    idle = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        if str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline

agwebberley = 0


async def user_metrics_background_task():
    await client.wait_until_ready()
    global Python_Bot_Guild
    Python_Bot_Guild = client.get_guild(684816171316412458)
    while not client.is_closed():
        try:
            # await on_ready()
            online, idle, offline = community_report(Python_Bot_Guild)
            with open("usermetrics.csv","a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")

            plt.clf()
            df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
            df['date'] = pd.to_datetime(df['time'], unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", 1,  inplace=True)
            df.set_index("date", inplace=True)
            df['online'].plot()
            plt.legend()
            plt.savefig("online.png")
            await asyncio.sleep(60)


        except Exception as e:
            print(str(e))
            await asyncio.sleep(10)

async def winner_minute():
    global uw
    lasttime = json.loads(open('lasttime.json').read())
    if int(time.time()) >= lasttime + 60:
        print(uw, "it works")
        with open("lasttime.json", "w") as fp:
            json.dump(lasttime, fp)
    await asyncio.sleep(10)


@client.event  # event decorator/wrapper
async def on_ready():
    global uw
    global Python_Bot_Guild
    print(f"We have logged in as {client.user}")
    print(str(int(time.time())))
    uw = json.loads(open('Wins.json').read())



@client.event
async def on_message(message):
    global Python_Bot_Guild
    global uw
    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    if "trophy-room" == f"{message.channel}":
        if message.author.name in uw:
            uw[message.author.name] = uw[message.author.name] + 1
        else:
            uw[message.author.name] = 1

    try:
        if "!tb # of wins" == message.content.lower():
            if message.channel == 'trophy-room' and uw[message.author.name] > 0:
                uw[message.author.name] - 1
            await message.channel.send(f"```{uw[message.author.name]}```")
    except KeyError:
        print("test")
        uw[message.author.name] = 1
        

    if "!tb" == message.content.lower():
        message1 = 'Hi!\n all commands start with !tb\n'
        message2 = '!tb member count will give you the meber count of the current server \n'
        message3 = '!tb community repport will tell you whos online, busy/dnd, and offline then display a graph\n'
        message4 = '!tb # of wins will tell you how many wins you have'
        await message.channel.send(f'```{message1}{message2}{message3}{message4}```')
    if "!tb member count" == message.content.lower():
        await message.channel.send(f"```py\n{Python_Bot_Guild.member_count}```")

    elif str(message.author) == 'agwebberley#9066' and "!tb logout" == message.content.lower():
        await client.close()
    elif "!tb save" == message.content.lower():
        print("saved")
        with open('Wins.json', 'w') as fp:
            json.dump(uw, fp)

    elif "!tb community report" == message.content.lower():
        online, idle, offline = community_report(Python_Bot_Guild)
        await message.channel.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")

        file = discord.File("online.png", filename="online.png")
        await message.channel.send("online.png", file=file)

client.loop.create_task(winner_minute())
client.loop.create_task(user_metrics_background_task())
client.run(token)
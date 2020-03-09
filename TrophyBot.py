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
            online, idle, offline = community_report(Python_Bot_Guild)
            with open("usermetrics.csv","a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")

            plt.clf()
            df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
            df['date'] = pd.to_datetime(df['time'],unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", 1,  inplace=True)
            df.set_index("date", inplace=True)
            df['online'].plot()
            plt.legend()
            plt.savefig("online.png")

            await asyncio.sleep(60)

        except Exception as e:
            print(str(e))
            await asyncio.sleep(60)


@client.event  # event decorator/wrapper
async def on_ready():
    global Python_Bot_Guild
    print(f"We have logged in as {client.user}")
    json_data = json.loads(open('dict.json').read())
    print(json_data)
    print(type(json_data))


@client.event
async def on_message(message):
    global Python_Bot_Guild
    global uw



    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    if message.channel == "trophy-room":
        print("it works")
        if message.author.name in uw:
            uw[message.author.name] = uw[message.author.name] + 1
        else:
            uw[message.author.name] = 1

    try:
        if "!py # of wins" == message.content.lower():
            await message.channel.send(f"```{uw[message.author.name]}```")
    except KeyError:
        print("test")
        uw[message.author.name] = 1

    if "!py messages" == message.content.lower():
        agwebberley -= 1
        await message.channel.send(f"```{agwebberley}```")



    if "!py" == message.content.lower():
        await message.channel.send('Hi!')
        await message.channel.send('all commands start with !py')
        await message.channel.send('!py member count give you the member count of your server')
        await message.channel.send('!py community report tells you who is online, busy dnd idle, offline')

    if "!py member count" == message.content.lower():
        await message.channel.send(f"```py\n{Python_Bot_Guild.member_count}```")

    elif str(message.author) == 'agwebberley#9066' and "!py logout" == message.content.lower():
        await client.close()
    elif "!py save" == message.content.lower():
        with open('dict.json', 'w') as fp:
            json.dump(uw, fp)


    elif '!py stat' == message.content.lower():
        mesg = await message.channel.send('Calculating...')
        counter = 0
        repeat = 0
        for x in range(0, 1): # Repeats 4 times
            async for msg in message.channel.history(limit=500):
                if msg.author == message.author:
                    counter += 1
                    repeat += 1
        await message.channel.send("{} has {} out of the first {} messages in {}".format(message.author, str(counter), 500*repeat, message.channel))

    elif "!py community report" == message.content.lower():
        online, idle, offline = community_report(Python_Bot_Guild)
        await message.channel.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")

        file = discord.File("online.png", filename="online.png")
        await message.channel.send("online.png", file=file)

client.loop.create_task(user_metrics_background_task())
client.run(token)
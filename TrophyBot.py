import asyncio
import discord
import json
import time
from discord.utils import get
from discord.ext import commands
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib import style
style.use("fivethirtyeight")

client = discord.Client()
token = open("token.txt", "r").read()

uw = json.loads(open('Wins.json').read())



def community_report(guild):
    online  = 0
    idle    = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        if str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline


def find_winners():
    uw = json.loads(open('Wins.json').read())
    tempuw = uw
    winner_list = [] 


    for i in range(3):
        winner_list.append(max(tempuw, key=tempuw.get))
        #tempuw.remove(max(tempuw, key=tempuw.get)) 
        top = max(tempuw, key=tempuw.get)
        winner_list[i] = winner_list[i] + "   " + str(tempuw.get(winner_list[i]))
        del tempuw[top]

    return winner_list



async def create_image(winners):
    img = Image.open("placement.jpg")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("BUNGEEINLINE-REGULAR.ttf", 16)

    draw.text((30, 43), winners[0],(255,255,255),font=font)
    draw.text((30, 85), winners[1],(255,255,255),font=font)
    draw.text((30, 130), winners[2],(255,255,255),font=font)
    
    img.save('placement_temp.jpg')

    send_message = True
    with open('send_message.json', 'w') as fp:
        json.dump(send_message, fp)



@client.event
async def send_winners():
    img = Image.open("placement_temp.jpg")

    send_winners = json.loads(open('send_message.json').read())

    if send_winners == True:
        channel = client.get_channel("686026687145705505") #648365930639785985   
        
        await message.channel.send(channel, "<@&684816171316412458> And the Winners of this week are:", Image.open("placement_temp.jpg"))
        send_winners = False
        with open("winner_send.json", "w") as fp:
            json.dump(send_winners, fp)
    await asyncio.sleep(10)


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
    await client.wait_until_ready()

    uw = json.loads(open('Wins.json').read())
    tempuw = uw

    while not client.is_closed():
        lasttime = json.loads(open('lasttime.json').read())

        if int(time.time()) >= lasttime + 10:


            winners = find_winners()
            await create_image(winners)

            lasttime = int(time.time())
            with open("lasttime.json", "w") as fp:
                json.dump(lasttime, fp)
        await asyncio.sleep(10)


@client.event  # event decorator/wrapper
async def on_ready():

    global Python_Bot_Guild
    print(f"We have logged in as {client.user}")
    uw = json.loads(open('Wins.json').read())
    channel = 686026687145705505




@client.event
async def on_message(message):
    global Python_Bot_Guild

    uw = json.loads(open('Wins.json').read())

    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")



    if message.content == "!tb send":

        await message.delete()

        send_winners = json.loads(open('send_message.json').read())

        channel = client.get_channel("686026687145705505")
        channel2 = channel
        file = discord.File("placement_temp.jpg", filename="placement_temp.jpg")


        if send_winners == True:
            await message.channel.send("<@&684816171316412458> And the Winners of this week are:")
            await message.channel.send("placement_temp.jpg", file=file)
            send_winners = False
            with open("winner_send.json", "w") as fp:
                json.dump(send_winners, fp)
            await asyncio.sleep(10)
            await message.channel.send("!tb send")
        else:
            await asyncio.sleep(10)
            await message.channel.send("!tb send")





    if "trophy-room" == f"{message.channel}":
        if message.author.name in uw:
            uw[message.author.name] = uw[message.author.name] + 1
        else:
            uw[message.author.name] = 1
            
        with open('Wins.json', 'w') as fp:
            json.dump(uw, fp)

 
    if "!tb wins" == message.content.lower():
        if message.channel == 'trophy-room' and uw[message.author.name] > 0:
            uw[message.author.name] - 1
        await message.channel.send(f"```{uw[message.author.name]}```")
        with open('Wins.json', 'w') as fp:
            json.dump(uw, fp)

            

    if "!tb" == message.content.lower():
        message1 = 'Hi!\nall commands start with !tb\n'
        message2 = '!tb member count will give you the meber count of the current server\n'
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

    #self.loop.create_task(self.winner_minute())
client.loop.create_task(winner_minute())
#client.loop.create_task(send_winners())
client.loop.create_task(user_metrics_background_task())
client.run(token)
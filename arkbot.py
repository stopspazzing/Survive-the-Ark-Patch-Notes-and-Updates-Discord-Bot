import asyncio
from bs4 import BeautifulSoup
import html5lib
import os
from peony import PeonyClient
import hashlib
import discord
import xml.etree.ElementTree as ET
from aiohttp import web, ClientSession

# Either specify a set of keys here or use os.getenv('CONSUMER_KEY') style
# assignment:

CONSUMER_KEY = ''
# CONSUMER_KEY = os.getenv("CONSUMER_KEY", None)
CONSUMER_SECRET = ''
# CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", None)
ACCESS_TOKEN = ''
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)
ACCESS_TOKEN_SECRET = ''
# ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", None)

# Users to watch for should be a list. This will be joined by Twitter and the
# data returned will be for any tweet mentioning:
# @twitter *OR* @twitterapi *OR* @support.
USERS = ['@survivetheark']

# Languages to filter tweets by is a list. This will be joined by Twitter
# to return data mentioning tweets only in the english language.
LANGUAGES = ['en']

# Since we're going to be using a streaming endpoint, there is no need to worry
# about rate limits.
pclient = PeonyClient(CONSUMER_KEY,
                      CONSUMER_SECRET,
                      ACCESS_TOKEN,
                      ACCESS_TOKEN_SECRET)

client = discord.Client()
loop = asyncio.get_event_loop()
app = web.Application()
link = 'https://survivetheark.com/index.php?/forums/topic/388254-pc-patch-notes-client-v31067-server-v31076/'
debug = False


@client.event
async def on_ready():
    print(f'Logged on as {client.user}')
    print('Tracking of Twitter, Youtube, and RSS Feeds Started')


@client.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == client.user:
        return
    if debug:
        if message.content == 'ping':
            await message.channel.send('pong' )


@client.event
async def twittercallback(data):
    channel = client.get_channel(YOUR-DISCORD-CHANNEL-ID)
    await channel.send(data)
    return True


@client.event
async def rsscallback(data):
    # RSS and Patch Notes
    channel = client.get_channel(YOUR-DISCORD-CHANNEL-ID)
    await channel.send(data)
    return True


@client.event
async def youtubecallback(data):
    channel = client.get_channel(YOUR-DISCORD-CHANNEL-ID)
    await channel.send(data)
    return True


# Timer call back for getting webpage


async def timercallback():
    md5hash = None
    bot_message = ''
    try:
        f = open("version_hash.txt", "r")
        if f.mode == 'r':
            md5hash = f.read()
        f.close()
    except:
        pass
    async with ClientSession() as session:
        async with session.get(link) as resp:
            bs = await resp.read()
            soup = BeautifulSoup(bs.decode('utf-8'), 'html5lib')
            comments = soup.find('div', attrs={'data-role': 'commentContent'})
            versions = comments.find_all('p')
            cleaned_versions = versions[1].text.replace('\n', ' ').strip()
            md5string = cleaned_versions.replace(' ', '').strip().lower()
            md5 = hashlib.md5(md5string.encode())
            if debug:
                print(md5.hexdigest()) ## Debug
                print(md5hash) ## Debug
            if str(md5hash) == str(md5.hexdigest()):
                if debug: print("No Changes Found") ## Debug
                await asyncio.sleep(3600)
                return await timercallback()
            else:
                try:
                    os.remove("version_hash.txt")
                except:
                    pass
                f = open("version_hash.txt", "w")
                f.write(md5.hexdigest())
                f.close()
                if debug: print("Changes Found! Sending to chat") ## Debug
                changelist = comments.find_all('ul')
                changes = changelist[0].find_all('li')
                if debug: print(cleaned_versions) ## Debug
                bot_message += f'>>> __**{cleaned_versions}**__' + '\n'
                for i in changes:
                    ii = i.text.replace('\n', ' ').strip()
                    if debug: print(ii) ## Debug
                    bot_message += f'* {ii}' + '\n'
                await rsscallback(bot_message)
                await asyncio.sleep(3600)
                return await timercallback()


# Timer call back for checking tweets


async def timercallback2():
    md5hash = None
    bot_message = ''
    try:
        f = open("version_hash2.txt", "r")
        if f.mode == 'r':
            md5hash = f.read()
        f.close()
    except:
        pass
    tweets = await pclient.api.statuses.user_timeline.get(count=50, user_id=2965146125)
    if debug:
        print(tweets[0].created_at)
        print(tweets[0].text)
    md5string = tweets[0].created_at.replace(' ', '').strip().lower()
    md5 = hashlib.md5(md5string.encode())
    if debug:
        print(md5.hexdigest())
        print(md5hash)
    if str(md5hash) == str(md5.hexdigest()):
        if debug: print("No New Tweets Found") ## Debug
        await asyncio.sleep(3600)
        return await timercallback2()
    else:
        try:
            os.remove("version_hash2.txt")
        except:
            pass
        f = open("version_hash2.txt", "w")
        f.write(md5.hexdigest())
        f.close()
        if debug: print("New Tweet Found! Sending to chat") ## Debug
        bot_message += f'>>> {tweets[0].created_at}' + '\n' + f'{tweets[0].text}'
        await twittercallback(bot_message)
        await asyncio.sleep(3600)
        return await timercallback2()


async def youtube(request):
    # https://www.youtube.com/feeds/videos.xml?channel_id=UCEYfsfyne69mFfNTcZeZ6gw
    data = await request.text()
    if request.body_exists:
        root = ET.fromstring(data)
        entry = root[4]
        if debug:
            print(entry[3].text) ## Debug
            print(entry[4].get('href')) ## Debug
        await youtubecallback(f'>>> {entry[3].text}' + '\n' + f'Link here: {entry[4].get("href")}')
    return web.Response(text="OK")


async def rss(request):
    # https://survivetheark.com/index.php?/rss/3-ark-news.xml/&member_id=431553&key=0e0dc4ef92a0551741b4318b1660bc04
    data = await request.text()
    root = ET.fromstring(data)
    entry = root[4]
    if debug:
        print(entry[3].text) ## Debug
        print(entry[5].get('href')) ## Debug
    await rsscallback(f'>>> {entry[3].text}' + '\n' + f'Link here: {entry[5].get("href")}')
    return web.Response(text="OK")


app.add_routes([web.post('/youtube/0213865', youtube),
                web.post('/rss/4302104', rss)
                ])

client.loop.create_task(web._run_app(app, host='0.0.0.0', port=6583))
client.loop.create_task(timercallback())
client.loop.create_task(timercallback2())
client.run('DISCORD-API-KEY')

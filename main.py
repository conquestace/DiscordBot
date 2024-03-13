import discord
import os
from dotenv import load_dotenv
import requests
#import asyncio
import random
#import novelai_api
#import sd_api


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

def reso():
        pairs = [(384, 640), (640, 384), (512, 512), (512, 768), (768, 512), (640, 640), (512, 1024), (1024, 512), (1024,1024), (832, 1216), (1216,832), (768, 384), (1024, 384), (1216, 384)]
        width, height = random.choice(pairs)
        return width, height

# Function to communicate with the image generation program
def novelapi(prompt, width, height):
    url = 'http://localhost:5000/generate_image'  # Update the URL if needed
    data = {'prompt': prompt, 'width': width, 'height': height}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.content  # Return the image data
    else:
        return None
    
def StableApi(prompt, width, height):
    url = 'http://localhost:5002/generate_image'  # Update the URL if needed
    data = {'prompt': prompt, 'width': width, 'height': height}
    
    try:
        response = requests.post(url, json=data)  
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return response.content  # Return the image data
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

# Offline to Online
@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        # Print server id and name.
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

# EVENT LISTENER
@bot.event
async def on_message(message):
    # reads message.
    if message.content.lower() in ["gm cir", "gm sir", "gm cirno", "good morning", "gm cirs", "gm sirs"]:
        # sends msg back
        await message.channel.send("Good morning!")

    elif message.content.lower() in ["cute cirno!", "cute cirno", "cute"]:
        await message.channel.send("Thanks!")

    elif message.content.lower() == "bake a cirno":
        await message.channel.send("Sure, gimme a sec...")
        files = os.listdir('./pre_generated')
        # Choose a random file
        random_file = random.choice(files)
        # Send the randomly chosen file
        await message.channel.send(file=discord.File(f'./pre_generated/{random_file}'))

    elif message.content.lower() == "bake a cirno slowly":
        await message.channel.send("Sure, gimme a min...")
        path='./output.png'
        # Send the generated image back to the Discord channel
        prompt = "cirno, touhou, blue eyes, blue hair, pinafore dress, ice wings, hair bow, blue bow,"
        width, height = reso()  # Example width and height
        image_data = StableApi(prompt, width, height)
        if image_data:
            # Send the generated image back to the Discord channel
            await message.channel.send(file=discord.File(path, "output.png"))

    elif message.content.lower() == "bake a cirno pls":
        await message.channel.send("Sure, gimme a sec...")
        # Example prompt to be sent to the image generation program
        prompt = "cirno, touhou, blue eyes, blue hair, pinafore dress, ice wings, hair bow, blue bow,"
        width, height = reso()  # Example width and height
        # Communicate with the image generation program
        image_data = novelapi(prompt, width, height)
        path='./results/image.png'
        if image_data:
            # Send the generated image back to the Discord channel
            await message.channel.send(file=discord.File(path, "image.png"))

        else:
            await message.channel.send("Failed to generate image. Please try again later.")

#run
bot.run(DISCORD_TOKEN)


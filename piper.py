import os
import random
import re
import string
import subprocess
import discord
from discord import Client, File, Message

# Define the bot token and configuration variables
BOT_TOKEN = "BOT_TOKEN"  # Replace with your bot token
temp_audio_folder = "/piper/output/"  # Set the temporary audio folder
piper_binary_path = "/usr/bin/piper"  # Set the Piper binary location
model_folder = "/piper/models/"  # Set the .onnx model folder

# Model names mapping
model_names = {
    "es_MX-claude-14947-epoch-high": "Español México | Claude",
    # Add more mappings as needed:"es_MX-modelname-epoch-high": "Discord model name",
}

# Initialize the Discord client with the intents modified
intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

# Config variables
# Set mode: 1 for responding only to private messages, 2 for responding only to server messages, 3 for responding to both
mode = 3
# Specify the server name or ID where the bot should respond (leave as None to respond to all servers)
server_name_or_id = none
# Specify the channel where the bot should respond (leave as None to respond in all channels)
channel_name_or_id = none

def filter_text(text):
    # Filter unwanted characters and limit text length
    filtered_text = re.sub(r'[^\w\s,.:\u00C0-\u00FF]', '', text)  # Removed newline filter
    return filtered_text[:4000]  # Increased limit to 4000 characters

def convert_text_to_speech(text, model):
    filtered_text = filter_text(text)
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)

    if os.path.isfile(piper_binary_path):
        model_path = os.path.join(model_folder, model)
        if os.path.isfile(model_path):
            # Construct the command to execute Piper
            command = f'echo "{filtered_text}" | "{piper_binary_path}" -m {model_path} -f {output_file}'
            # Log the command being executed
            print(f"Executing: {command}")  # You can use logging.debug() here if you prefer
            try:
                subprocess.run(command, shell=True, check=True)
                return output_file
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                return None
        else:
            print(f"Model '{model}' not found at the specified location.")
            return None
    else:
        print(f"Piper binary not found at the specified location.")
        return None

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

@client.event
async def on_message(message: Message):
    print(f"Received message: {message.content}")  # Debug print for received messages
    
    # Check if the message is from a bot or not
    if message.author.bot:
        return  # Ignore messages from other bots
    
    # Check mode and message context
    if mode == 1 and message.guild:  # If mode is set to respond only to private messages but message is from a server
        return
    elif mode == 2 and not message.guild:  # If mode is set to respond only to server messages but message is not from a server
        return
    elif mode == 3 and server_name_or_id and message.guild and message.guild.id != server_name_or_id:  # If mode is set to respond to both but message is from a different server
        return
    elif mode == 3 and channel_name_or_id and message.channel.id != channel_name_or_id:  # If mode is set to respond to both but message is not from the specified channel
        return
    
    if message.content.startswith("/piper help") or message.content.startswith("/piper manual") or message.content.startswith("/piper ayuda"):
        # Explanation of how to use Piper and examples
        help_message = ("Piper is a text-to-speech bot. Use `/piper (model number) (text to convert)` to convert text to speech.\n"
                        "Example: `/piper 1 Hello, world!`\n"
                        "Use `/piper list` to see available models.")
        await message.channel.send(help_message)

    elif message.content.startswith("/piper list") or message.content.startswith("/piper ls") or message.content.startswith("/piper models") or message.content.startswith("/piper model list") or message.content.startswith("/piper lista") or message.content.startswith("/piper modelos") or message.content.startswith("/piper lista modelos"):
        # List available models
        model_options = [file[:-5] for file in os.listdir(model_folder) if file.endswith('.onnx')]  # Remove .onnx extension
        numbered_models = [f"{i+1} - {model_names.get(model, model)}" for i, model in enumerate(model_options)]  # Add numbers and check for custom names
        await message.channel.send("Available models:\n" + "\n".join(numbered_models))

    elif message.content.startswith("/piper"):
        command_parts = message.content.split()
        if len(command_parts) < 3:
            await message.channel.send("Invalid command format. Use `/piper (model number) (text to convert)`.")
            return

        model_num = command_parts[1]
        text = " ".join(command_parts[2:])  # Joining all parts after model number as text
        model_options = [file for file in os.listdir(model_folder) if file.endswith('.onnx')]

        if not model_num.isdigit() or not 1 <= int(model_num) <= len(model_options):
            await message.channel.send("Invalid model number.")
            return

        model_name = model_options[int(model_num) - 1]
        output_file = convert_text_to_speech(text, model_name)
        if output_file:
            await message.channel.send(file=File(output_file))
            os.remove(output_file)  # Delete the file after sending
        else:
            await message.channel.send("Conversion failed.")


client.run(BOT_TOKEN)

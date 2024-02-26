import discord
import os
import shardai
import requests
import json
from shardai import exceptions
from shardai import ShardClient
from discord.ext import commands
from discord import app_commands
from commands.chat import setup as chat_setup
from commands.custom_imagine import setup as imagine_setup
from collections import deque
from dotenv import load_dotenv

load_dotenv()

# Setup the Discord client
intents = discord.Intents.all()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents , heartbeat_timeout=60)

message_history = {}

MAX_MESSAGE_HISTORY = 15

client = ShardClient("shard-jsW4ZXRuuKRyfu27opINzywriKiQLq")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

active_channels = set()

current_model = 'llama_2_7b'

current_text_model = 'llama_2_7b'

current_image_model = 'absolute_reality_v16'

current_personality = 'You are a helpful assistant'
# Registering the slash commands using the new method

chat_setup(bot)

imagine_setup(bot)

@bot.tree.command(name='help', description='Display the list of available commands and their descriptions')
async def help(interaction: discord.Interaction):
    # This is a simple example of creating an embed to list the commands.
    embed = discord.Embed(title="Available Commands", description="Here are the commands you can use:", color=0x00ff00)
    
    for command in bot.tree.get_commands():
        # You might want to add checking and formatting as desired.
        embed.add_field(name=command.name, value=command.description, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='persona', description= 'Change the bot persona!')
async def persona(interaction: discord.Interaction, instructions: str):
    global current_personality
    current_personality = instructions
    embed = discord.Embed(description='Successfully changed the bot persona!', color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='change-model', description='Change the chat model')
@app_commands.describe(model_name='The name of the model you want to use')
@app_commands.choices(model_name=[
     app_commands.Choice(name='🍀 gpt_35_turbo', value='gpt_35_turbo'),
     app_commands.Choice(name='🍀 gpt_35_turbo_16k', value='gpt_35_turbo_16k'),
     app_commands.Choice(name='🍀 gpt_4_turbo', value='gpt_4_turbo'),
     app_commands.Choice(name='🔍 gemini', value='gemini'),
     app_commands.Choice(name='🦎 pygmalion', value='pygmalion'),
     app_commands.Choice(name='🐬 dolphin', value='dolphin'),
     app_commands.Choice(name='🌌 mixtral_instruct', value='mixtral_instruct'),
     app_commands.Choice(name='🌌 mixtral_7b_instruct', value='mixtral_7b_instruct'),
     app_commands.Choice(name='🌌 mixtral', value='mixtral'),
     app_commands.Choice(name='🌵 lzlv_70b', value='lzlv_70b'),
     app_commands.Choice(name='🌙 airoboros_70b', value='airoboros_70b'),
     app_commands.Choice(name='🌙 airoboros_70b_gpt4', value='airoboros_70b_gpt4'),
     app_commands.Choice(name='🦙 llama_2_7b', value='llama_2_7b'),
     app_commands.Choice(name='🦙 llama_2_13b', value='llama_2_13b'),
     app_commands.Choice(name='🦙 llama_2_70b', value='llama_2_70b'),
     app_commands.Choice(name='💻 code_llama_34b', value='code_llama_34b'),
     app_commands.Choice(name='💻 code_llama_34b_v2', value='code_llama_34b_v2'),
     app_commands.Choice(name='💻 code_llama_70b_instruct', value='code_llama_70b_instruct'),
     app_commands.Choice(name='yi_6b_200k', value='yi_6b_200k'),
     app_commands.Choice(name='yi_34b_chat', value='yi_34b_chat'),
     app_commands.Choice(name='yi_34b_200k', value='yi_34b_200k'),
     app_commands.Choice(name='pythia_2_8b', value='pythia_2_8b'),
     app_commands.Choice(name='pythia_12b', value='pythia_12b'),
     app_commands.Choice(name='mythomax_l2_13b', value='mythomax_l2_13b'),
     app_commands.Choice(name='gpt_neo_1_3b', value='gpt_neo_1_3b')
])
@app_commands.describe(model_name='The name of the model you want to use')
async def change_model(interaction: discord.Interaction, model_name: str):
    global current_text_model
    current_text_model = model_name
    await interaction.response.send_message(f"Chat model changed to {model_name}")
@bot.tree.command(name='current-model', description='Tells the current model the bot is using')
async def current_text_model_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(f"The current chat model is {current_text_model}")

@bot.tree.command(name='toggle-active', description='Toggle bot active status in the channel')
async def toggle_active(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if channel_id in active_channels:
        active_channels.remove(channel_id)
        await interaction.response.send_message(f"🔴 Bot has been deactivated in this channel.")
    else:
        active_channels.add(channel_id)
        await interaction.response.send_message(f"🟢 Bot has been activated in this channel.")

@bot.tree.command(name='clear-history', description='Clears your message history with the bot!')
async def clear_history(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in message_history:
        del message_history[user_id]
        await interaction.response.send_message(f"🟢 Successfully cleared {interaction.user.mention} message history!", ephemeral=True)
    else:
        await interaction.response.send_message(f"🔴 {interaction.user.mention} has no message history stored!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message) or 'llemy' in message.content.lower() or message.channel.id in active_channels:
        reaction_emoji = '🦙'  # Replace with the actual ID if custom emoji is used
        await message.add_reaction(reaction_emoji)
        async with message.channel.typing():
            try:
            # Use the global model variable here
                   cleaned_message = message.content.lower().replace('llemy', '').strip()
                   user_id = message.author.id
                   if user_id not in message_history:
                        message_history[user_id] = deque(maxlen=MAX_MESSAGE_HISTORY)
                   message_history[user_id].append(cleaned_message)
                   recent_messages = list(message_history.get(user_id, []))
                   payload = [{'role': 'user', 'content': recent_messages[-1]},*({'role': 'user', 'content': msg} for msg in recent_messages[:-1]),{"role": 'system', 'content': current_personality}]
                   data = {'model': current_text_model,
                           'messages': payload,
                           'stream': False                    
                   }
                   headers = {'api-key': 'shard-jsW4ZXRuuKRyfu27opINzywriKiQLq', 'Content-Type': 'application/json'}
                   r = requests.post(url='https://shard-ai.xyz/v1/chat/completions', headers=headers, data=json.dumps(data))
                   text = r.json()['choices'][0]['message']['content']
                   embed = discord.Embed(title=current_text_model.upper(), description=text, color=0x00ff00)
                   await message.reply(embed=embed)
            except shardai.exceptions.APIError as e:
                # Send a message to the channel with the error
                   error_message = f"Oops! An error occurred: {str(e)}"
                   error_code = error_message
                   embed = discord.Embed(title="🔴 ERROR!", description=error_code, color=0x00ff00)
                   await message.reply(embed=embed)
    else:
        return


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="LLM models"), status=discord.Status.idle)
    await bot.tree.sync()

# Enter your Discord bot token here
bot.run(DISCORD_TOKEN)

import discord
import os
from dotenv import load_dotenv
import requests
import json
from discord import app_commands
from discord.ext import commands
from collections import deque

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

global capitalized_model_value
capitalized_model_value = None

intents = discord.Intents.all()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents , heartbeat_timeout=60)

user_message_history = {}

user_last_model = {}

active_channels = set()

guild_models = {}

@bot.tree.command(name='help', description='Display the list of available commands and their descriptions')
async def help(interaction: discord.Interaction):
    # This is a simple example of creating an embed to list the commands.
    embed = discord.Embed(title="Available Commands", description="Here are the commands you can use:", color=0x00ff00)
    
    for command in bot.tree.get_commands():
        # You might want to add checking and formatting as desired.
        embed.add_field(name=command.name, value=command.description, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='change-model', description='Change the AI model')
@app_commands.describe(model='The name of the model you want to use')
@app_commands.choices(model=[
     app_commands.Choice(name='gpt_35_turbo', value='gpt_35_turbo'),
     app_commands.Choice(name='gpt_35_turbo_16k', value='gpt_35_turbo_16k'),
     app_commands.Choice(name='gpt_4_turbo', value='gpt_4_turbo'),
     #app_commands.Choice(name='gemini', value='gemini'),
     #app_commands.Choice(name='pygmalion', value='pygmalion'),
     app_commands.Choice(name='dolphin', value='dolphin'),
     app_commands.Choice(name='mixtral_instruct', value='mixtral_instruct'),
     #app_commands.Choice(name='mixtral_7b_instruct', value='mixtral_7b_instruct'),
     #app_commands.Choice(name='mixtral', value='mixtral'),
     #app_commands.Choice(name='lzlv_70b', value='lzlv_70b'),
     #app_commands.Choice(name='airoboros_70b', value='airoboros_70b'),
     #app_commands.Choice(name='airoboros_70b_gpt4', value='airoboros_70b_gpt4'),
     #app_commands.Choice(name='llama_2_7b', value='llama_2_7b'),
     #app_commands.Choice(name='llama_2_13b', value='llama_2_13b'),
     app_commands.Choice(name='llama_2_70b', value='llama_2_70b')
     #app_commands.Choice(name='code_llama_34b', value='code_llama_34b'),
     #app_commands.Choice(name='code_llama_34b_v2', value='code_llama_34b_v2'),
     #app_commands.Choice(name='code_llama_70b_instruct', value='code_llama_70b_instruct'),
     #app_commands.Choice(name='yi_6b_200k', value='yi_6b_200k'),
     #app_commands.Choice(name='yi_34b_chat', value='yi_34b_chat'),
     #app_commands.Choice(name='yi_34b_200k', value='yi_34b_200k'),
     #app_commands.Choice(name='pythia_2_8b', value='pythia_2_8b'),
     #app_commands.Choice(name='pythia_12b', value='pythia_12b'),
     #app_commands.Choice(name='mythomax_l2_13b', value='mythomax_l2_13b'),
     #app_commands.Choice(name='gpt_neo_1_3b', value='gpt_neo_1_3b')
])
@app_commands.describe(model='The name of the model you want to use')
async def change_model(interaction: discord.Interaction, model: str):
    guild_models[interaction.guild_id] = model

    await interaction.response.send_message(f'The model has been changed to {model}', ephemeral=True)


# Add the new command with decorators
@bot.tree.command(name='toggle-active', description='Toggle bot active status in the channel')
async def toggle_active(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if channel_id in active_channels:
        active_channels.remove(channel_id)
        await interaction.response.send_message(f"🔴 Bot has been deactivated in this channel.")
    else:
        active_channels.add(channel_id)
        await interaction.response.send_message(f"🟢 Bot has been activated in this channel.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_id = message.author.id
    if user_id not in user_message_history:
        user_message_history[user_id] = deque(maxlen=15)
    user_message_history[user_id].append(message.content)
    if message.channel.id in active_channels:
        # Bot responds to all messages in active channels without needing mention
        async with message.channel.typing():
            current_model = guild_models.get(message.guild.id, 'gpt_4_turbo')
            capitalized_model = current_model.upper()
            capitalized_model_value = capitalized_model
            data = {
                'model': current_model,
                'messages': [{'role': 'user', 'content': msg} for msg in user_message_history[user_id]] + [{'role': 'assistant', 'content': message.content}],
                'stream': False
            }
            headers = {'api-key': 'shard-jsW4ZXRuuKRyfu27opINzywriKiQLq', 'Content-Type': 'application/json'}
            response = requests.post(url='https://shard-ai.xyz/v1/chat/completions', headers=headers, data=json.dumps(data))
            text = response.json()['choices'][0]['message']['content']
            embed = discord.Embed(title=capitalized_model, description=text, color=0x00ff00)
            await message.channel.send(embed=embed)
    if bot.user.mentioned_in(message):
      async with message.channel.typing():
        current_model = guild_models.get(message.guild.id, 'gpt_4_turbo')
        capitalized_model = current_model.upper()
        capitalized_model_value = capitalized_model
        data = {
            'model': current_model,
            'messages': [{'role': 'user', 'content': msg} for msg in user_message_history[user_id]] + [{'role': 'assistant', 'content': message.content}],
            'stream': False
        }
        headers = {'api-key': 'shard-jsW4ZXRuuKRyfu27opINzywriKiQLq', 'Content-Type': 'application/json'}
        response = requests.post(url='https://shard-ai.xyz/v1/chat/completions', headers=headers, data=json.dumps(data))
        text = response.json()['choices'][0]['message']['content']
        embed = discord.Embed(title=capitalized_model, description=text, color=0x00ff00)
        await message.channel.send(embed = embed)
    await bot.process_commands(message)

@bot.tree.command(name='reset', description='Reset your chat history with the bot')
async def reset(interaction: discord.Interaction):
    # Reset the user's message history
    user_id = interaction.user.id
    user_message_history[user_id] = deque(maxlen=15)
    embed = discord.Embed(
        description='✅ Your chat history has been reset.',
        color=0x00ff00  # or any other color of your choice
    )

    # Send a confirmation message to the user
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='models', description='List available AI models')
async def models(interaction: discord.Interaction):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url='https://shard-ai.xyz/v1/chat/models', headers=headers)
    data = response.json()
    
    models_list = []
    if 'models' in data:
        models = data['models']
        for model in models:
            models_list.append(model)
    
    models_output = '\n'.join(models_list)
    footer_note = "A lot of models listed here don't really work, please use `/change-model` to view the available models."
    description_text = f"{footer_note}\n\n{models_output}"
    embed = discord.Embed(
        title="List of availaible AI models",
        description=description_text,
        color=0x00ff00  # or any other color of your choice
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="imagine", description="(DO NOT USE THIS)Generate an image from a text prompt")
async def imagine(interaction: discord.Interaction):
        headers = {
            'api-key': 'shard-jsW4ZXRuuKRyfu27opINzywriKiQLq'
        }
        data = {
            'prompt': 'dog',
            'model': 'DELIBERATE_V2',
            'sampler': 'Euler',
            'upscale': 'yes',
            'steps': 25
        }
        response = requests.get(url='https://shard-ai.xyz/v1/sd1x/completions', headers=headers, json=data)
        image_url = response.json()['image']  # Assuming the API returns the image URL in a field named `url`
        print(image_url)
        embed = discord.Embed(title="Imagined:", description=image_url, color=0x00ff00)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name='current-model', description='Tells the current model the bot is using')
async def current_model(interaction: discord.Interaction):
    embed = discord.Embed(title="Current bot model", description= f'The bot is currently using {capitalized_model_value} model', color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="LLM models"), status=discord.Status.idle)
    await bot.tree.sync()

@bot.command()
async def chat(ctx, *, message: str):
    await ctx.message.delete()
    await on_message(ctx.message)
bot.run(DISCORD_TOKEN)

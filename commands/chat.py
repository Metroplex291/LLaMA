import discord
import os
import shardai
from shardai import exceptions
from shardai import ShardClient
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents , heartbeat_timeout=60)

client = ShardClient("shard-jsW4ZXRuuKRyfu27opINzywriKiQLq")

current_model = 'llama_2_7b'


def setup(bot):
    @bot.tree.command(name='chat', description='Chat with your preferred model!')
    @app_commands.describe(model_name='The name of the model you want to use')
    @app_commands.choices(model_name=[
          app_commands.Choice(name='gpt_35_turbo', value='gpt_35_turbo'),
          app_commands.Choice(name='gpt_35_turbo_16k', value='gpt_35_turbo_16k'),
          app_commands.Choice(name='gpt_4_turbo', value='gpt_4_turbo'),
          app_commands.Choice(name='gemini', value='gemini'),
          app_commands.Choice(name='pygmalion', value='pygmalion'),
          app_commands.Choice(name='dolphin', value='dolphin'),
          app_commands.Choice(name='mixtral_instruct', value='mixtral_instruct'),
          app_commands.Choice(name='mixtral_7b_instruct', value='mixtral_7b_instruct'),
          app_commands.Choice(name='mixtral', value='mixtral'),
          app_commands.Choice(name='lzlv_70b', value='lzlv_70b'),
          app_commands.Choice(name='airoboros_70b', value='airoboros_70b'),
          app_commands.Choice(name='airoboros_70b_gpt4', value='airoboros_70b_gpt4'),
          app_commands.Choice(name='llama_2_7b', value='llama_2_7b'),
          app_commands.Choice(name='llama_2_13b', value='llama_2_13b'),
          app_commands.Choice(name='llama_2_70b', value='llama_2_70b'),
          app_commands.Choice(name='code_llama_34b', value='code_llama_34b'),
          app_commands.Choice(name='code_llama_34b_v2', value='code_llama_34b_v2'),
          app_commands.Choice(name='code_llama_70b_instruct', value='code_llama_70b_instruct'),
          app_commands.Choice(name='yi_6b_200k', value='yi_6b_200k'),
          app_commands.Choice(name='yi_34b_chat', value='yi_34b_chat'),
          app_commands.Choice(name='yi_34b_200k', value='yi_34b_200k'),
          app_commands.Choice(name='pythia_2_8b', value='pythia_2_8b'),
          app_commands.Choice(name='pythia_12b', value='pythia_12b'),
          app_commands.Choice(name='mythomax_l2_13b', value='mythomax_l2_13b'),
          app_commands.Choice(name='gpt_neo_1_3b', value='gpt_neo_1_3b')
    ]) 
    @app_commands.describe(model_name='The name of the model you want to use')
    @app_commands.describe(query='Ask the bot!')
    async def chat(interaction: discord.Interaction, model_name: str, query: str):
                  global current_model
                  current_model = model_name

                  await interaction.response.defer(thinking=True)
                  
                  try:
                        response = client.chat.completions(query, current_model)
                        text = response.choices[0].message.content
                        embed = discord.Embed(title=current_model.upper(), description=text, color=0x00ff00)
                        await interaction.followup.send(embed=embed)
                  except Exception as e:  # Catch potential errors
                        await interaction.followup.send(f"An error occurred: {e}")
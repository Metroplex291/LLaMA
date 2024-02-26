import discord
import os
import shardai
import requests
from shardai import exceptions
from shardai import ShardClient
from discord.ext import commands
from discord import app_commands
from collections import deque

intents = discord.Intents.all()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents , heartbeat_timeout=60)

current_image_model = 'absolute_reality_v16'
sampler = 'Euler'
ratios = 'portrait'
styles = 'base'

def setup(bot):
    @bot.tree.command(name='imagine', description='Generate images from text!')
    @app_commands.choices(image_model=[
        app_commands.Choice(name='absolute_reality_v16', value='absolute_reality_v16'),
        app_commands.Choice(name='timeless_1', value='timeless_1'),
        app_commands.Choice(name='realistic_vision_v1', value='realistic_vision_v1'),
        app_commands.Choice(name='realistic_vision_v2', value='realistic_vision_v2'),
        app_commands.Choice(name='realistic_vision_v4', value='realistic_vision_v4'),
        app_commands.Choice(name='realistic_vision_v5', value='realistic_vision_v5'),
        app_commands.Choice(name='redshift_diffusion_v10', value='redshift_diffusion_v10'),
        app_commands.Choice(name='openjourney_v4', value='openjourney_v4'),
        app_commands.Choice(name='dreamlike_anime_1', value='dreamlike_anime_1'),
        app_commands.Choice(name='dreamlike_diffusion_1', value='dreamlike_diffusion_1'),
        app_commands.Choice(name='dreamlike_photoreal_2', value='dreamlike_photoreal_2'),
        app_commands.Choice(name='dreamshaper_7', value='dreamshaper_7'),
        app_commands.Choice(name='dreamshaper_8', value='dreamshaper_8'),
        app_commands.Choice(name='deliberate_v2', value='deliberate_v2'),
        app_commands.Choice(name='deliberate_v3', value='deliberate_v3'),
        app_commands.Choice(name='edge_of_realism_eorv20', value='edge_of_realism_eorv20'),
        app_commands.Choice(name='absolute_reality_v181', value='absolute_reality_v181'),
        app_commands.Choice(name='neverendingdream_v122', value='neverendingdream_v122'),
        app_commands.Choice(name='analog_diffusion_1', value='analog_diffusion_1'),
        app_commands.Choice(name='anything_v3_0_pruned', value='anything_v3_0_pruned'),
        app_commands.Choice(name='anything_v4_5_pruned', value='anything_v4_5_pruned'),
        app_commands.Choice(name='anything_v5_prtre', value='anything_v5_prtre')
    ])
    @app_commands.choices(ratio_choose=[
        app_commands.Choice(name='square', value='square'),
        app_commands.Choice(name='landscape', value= 'landscape'),
        app_commands.Choice(name='portrait', value= 'portrait')
    ])
    @app_commands.choices(sampler_choose=[
        app_commands.Choice(name='Euler (recommended to use for best clarity with all image_models)', value='Euler'),
        app_commands.Choice(name='Euler_a', value='Euler_a'),
        app_commands.Choice(name='LMS', value='LMS'),
        app_commands.Choice(name='Heun', value='Heun'),
        app_commands.Choice(name='DPM2', value='DPM2'),
        app_commands.Choice(name='DPM2_a', value='DPM2_a'),
        app_commands.Choice(name='DPM2_a_Karras', value='DPM2_a_Karras'),
        app_commands.Choice(name='DPM2_Karras', value='DPM2_Karras'),
        app_commands.Choice(name='DPM_fast', value='DPM_fast'),
        app_commands.Choice(name='DPM_adaptive', value='DPM_adaptive'),
        app_commands.Choice(name='LMS_Karras', value='LMS_Karras'),
        app_commands.Choice(name='DPM_plusplus_2S_a', value='DPM_plusplus_2S_a'),
        app_commands.Choice(name='DPM_plusplus_2S_a_Karras', value='DPM_plusplus_2S_a_Karras'),
        app_commands.Choice(name='DPM_plusplus_2M', value='DPM_plusplus_2M'),  
        app_commands.Choice(name='DPM_plusplus_2M_Karras', value='DPM_plusplus_2M_Karras'),
        app_commands.Choice(name='DPM_plusplus_SDE', value='DPM_plusplus_SDE'),
        app_commands.Choice(name='DPM_plusplus_SDE_Karras', value='DPM_plusplus_SDE_Karras'),
        app_commands.Choice(name='DDIM', value='DDIM'),
        app_commands.Choice(name='PLMS', value='PLMS')

    ])
    @app_commands.choices(styles_choose=[
        app_commands.Choice(name='base', value='base'),
        app_commands.Choice(name='3d_model', value='3d_model'),
        app_commands.Choice(name='analog_film', value='analog_film'),
        app_commands.Choice(name='anime', value='anime'),
        app_commands.Choice(name='cinematic', value='cinematic'),
        app_commands.Choice(name='comic_book', value='comic_book'),
        app_commands.Choice(name='digital_art', value='digital_art'),
        app_commands.Choice(name='enhance', value='enhance'),
        app_commands.Choice(name='fantasy_art', value='fantasy_art'),
        app_commands.Choice(name='isometric_style', value='isometric_style'),
        app_commands.Choice(name='line_art', value='line_art'),
        app_commands.Choice(name='photographic', value='photographic'),
        app_commands.Choice(name='pixel_art', value='pixel_art'),
        app_commands.Choice(name='texture', value='texture'),
        app_commands.Choice(name='food_photography', value='food_photography'),
        app_commands.Choice(name='real_estate', value='real_estate'),
        app_commands.Choice(name='abstract', value='abstract'),
        app_commands.Choice(name='graffiti', value='graffiti'),
        app_commands.Choice(name='hyperrealism', value='hyperrealism'),
        app_commands.Choice(name='pop_art', value='pop_art'),
        app_commands.Choice(name='steampunk', value='steampunk'),
        app_commands.Choice(name='surrealist', value='surrealist'),
        app_commands.Choice(name='typography', value='typography'),
        app_commands.Choice(name='watercolor', value='watercolor')
    ])
    @app_commands.describe(image_model= 'Choose the model for image gen')
    @app_commands.describe(text_prompt= 'Describe the image')
    async def chat(interaction: discord.Interaction, image_model: str, text_prompt: str, ratio_choose: str, sampler_choose: str, styles_choose: str):
        global current_image_model
        global ratios
        global sampler
        global styles
        ratios = ratio_choose
        sampler = sampler_choose
        styles = styles_choose
        current_image_model = image_model

        await interaction.response.defer(thinking=True)

        try:
            headers = {'api-key': 'shard-jsW4ZXRuuKRyfu27opINzywriKiQLq'}
            data = {
                    'prompt': text_prompt,
                    'model': current_image_model,
                    'samplers': sampler,
                    'upscale': 'yes',
                    'ratios': ratios,
                    'styles': styles,
                    'cfg': 9,
                    'steps': 25
            }
            response = requests.get(url='https://shard-ai.xyz/v1/sd1x/completions', headers=headers, json=data)
            img_url = response.json()['image']
            print(img_url)
            #embed = discord.Embed(description='Prompt\n' + text_prompt + '\nModel\n' + current_image_model + '\nSampler\nEuler\n', color=0x00ff00)
            await interaction.followup.send(img_url)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}")

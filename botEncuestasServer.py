import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()  # Enable all intents
load_dotenv()
TOKEN = os.getenv("TOKEN_BOT_DISCORD")
bot = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", description="Pruebas", intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for command in bot.commands:
        print(command)


@bot.command()
async def create_poll(ctx, time: int, question, image_url: str, *options_and_emojis):
    options_and_emojis = list(options_and_emojis)
    if len(options_and_emojis) % 2 != 0:
        await ctx.send('You must supply an even number of arguments, alternating between options and emojis.')
        return

    options = options_and_emojis[::2]
    emojis = options_and_emojis[1::2]

    # Create a dictionary that maps each emoji to its corresponding option
    emoji_to_option = dict(zip(emojis, options))

    if len(options) > 20:
        await ctx.send('You can only supply a maximum of 20 options.')
    else:
        embed = discord.Embed(title=question, description='\n'.join(
            [f'{emoji} {option}' for emoji, option in zip(emojis, options)]), color=discord.Color.blue())
        embed.set_image(url=image_url)  # Add image to the poll
        message = await ctx.send(embed=embed)
        for emoji in emojis:
            await message.add_reaction(emoji)

        # Update poll results every 10 seconds
        for _ in range(time // 10):
            await asyncio.sleep(10)
            # Fetch the latest version of the message
            message = await ctx.channel.fetch_message(message.id)
            embed = create_results_embed(
                message, question, emoji_to_option, image_url)
            await message.edit(embed=embed)

        # Fetch the latest version of the message before closing the poll
        message = await ctx.channel.fetch_message(message.id)
        embed_poll_finish = poll_end(
            message, f"El resultado de la encuesta con la pregunta : {question}", emoji_to_option, image_url)
        await ctx.send(embed=embed_poll_finish)
        await ctx.send('The poll has ended!')


def create_results_embed(message, question, emoji_to_option, image_url):
    reactions = message.reactions
    results = []
    for i, reaction in enumerate(reactions):
        emoji = str(reaction.emoji)
        if emoji in emoji_to_option:
            # subtract 1 to exclude the bot's own reaction
            results.append((emoji_to_option[emoji], reaction.count-1))
    results.sort(key=lambda x: x[1], reverse=True)
    result_string = '\n'.join(
        [f'Opción {result[0]}: {result[1]} votos' for result in results])
    embed = discord.Embed(
        title=question, description=result_string, color=discord.Color.blue())
    embed.set_image(url=image_url)  # Add image to the results
    return embed


def poll_end(message, question, emoji_to_option, image_url):
    reactions = message.reactions
    results = []
    for i, reaction in enumerate(reactions):
        emoji = str(reaction.emoji)
        if emoji in emoji_to_option:
            # subtract 1 to exclude the bot's own reaction
            results.append((emoji_to_option[emoji], reaction.count-1))
    results.sort(key=lambda x: x[1], reverse=True)
    result_string = '\n'.join(
        [f'Resultado definitivo de la Opción {result[0]}: {result[1]} votos' for result in results])
    embed = discord.Embed(
        title=question, description=result_string, color=discord.Color.red())
    embed.set_image(url=image_url)  # Add image to the results
    return embed


bot.run(TOKEN)

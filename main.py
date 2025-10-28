# bot.py
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Put your Discord bot token here
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
print("Token loaded:", bool(TOKEN))  # For testing
# Intents (make sure 'Message Content Intent' is enabled in the Discord Developer Portal)
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)

# Difficulty settings
DIFFICULTIES = {
    "easy":    {"max_number": 10, "max_attempts": 3},
    "medium":  {"max_number": 50, "max_attempts": 5},
    "hard":    {"max_number": 100, "max_attempts": 7},
}

# Per-user game states
active_games = {}

# Help message builder
def build_help_message():
    return (
        "**Number Guessing Bot Commands:**\n"
        "`!start [difficulty]` — Begin a new game. Difficulty: easy, medium, hard\n"
        "`!guess [number]` — Submit your guess during an active game\n"
        "`!end` — End your current game\n"
        "`!help` — Show this help message\n"
        "Example: `!start easy`"
    )

@bot.event
async def on_ready():
    print(f"✅ Number Guessing Bot connected as {bot.user}")

@bot.command(name="help")
async def help_command(ctx):
    await ctx.send(build_help_message())

@bot.command(name="start")
async def start_command(ctx, difficulty: str = "easy"):
    user_id = ctx.author.id
    difficulty = difficulty.lower()

    if user_id in active_games:
        await ctx.send(f"{ctx.author.mention}, you already have an active game! End it with `!end`.")
        return

    if difficulty not in DIFFICULTIES:
        await ctx.send(f"Invalid difficulty. Choose from: easy, medium, hard. Example: `!start medium`")
        return

    config = DIFFICULTIES[difficulty]
    secret_number = random.randint(1, config["max_number"])
    active_games[user_id] = {
        "secret_number": secret_number,
        "difficulty": difficulty,
        "max_number": config["max_number"],
        "attempts_left": config["max_attempts"],
        "score": config["max_attempts"] + 10,
        "attempts": 0,
    }

    await ctx.send(
        f"🎯 {ctx.author.mention} **{difficulty.title()} Mode** started!\n"
        f"Guess a number between 1 and {config['max_number']}.\n"
        f"You have {config['max_attempts']} attempts. Use `!guess [number]` to play."
    )

@bot.command(name="guess")
async def guess_command(ctx, number: int = None):
    user_id = ctx.author.id
    game = active_games.get(user_id)

    if not game:
        await ctx.send(f"{ctx.author.mention}, you don't have an active game. Start one with `!start [difficulty]`.")
        return

    if number is None:
        await ctx.send(f"{ctx.author.mention}, please provide your guess. Example: `!guess 7`.")
        return

    if number < 1 or number > game["max_number"]:
        await ctx.send(f"{ctx.author.mention}, your guess must be between 1 and {game['max_number']}.")
        return

    if game["attempts_left"] <= 0:
        await ctx.send(f"{ctx.author.mention}, you're out of attempts! The number was {game['secret_number']}.\nStart a new game with `!start [difficulty]`.")
        del active_games[user_id]
        return

    game["attempts"] += 1
    game["attempts_left"] -= 1
    game["score"] -= 2

    if number == game["secret_number"]:
        await ctx.send(f"🎉 {ctx.author.mention}, correct! The number was {game['secret_number']}.\nYou guessed it in {game['attempts']} attempts. Final Score: {game['score']}.\nStart a new game anytime with `!start [difficulty]`.")
        del active_games[user_id]
    elif number > game["secret_number"]:
        await ctx.send(f"{ctx.author.mention}, your guess is **too high**. Attempts left: {game['attempts_left']}.")
    else:
        await ctx.send(f"{ctx.author.mention}, your guess is **too low**. Attempts left: {game['attempts_left']}.")

    if game["attempts_left"] == 0 and user_id in active_games:
        await ctx.send(f"💀 {ctx.author.mention}, you're out of attempts! The number was {game['secret_number']}.")
        del active_games[user_id]

@bot.command(name="end")
async def end_command(ctx):
    user_id = ctx.author.id
    if user_id in active_games:
        del active_games[user_id]
        await ctx.send(f"{ctx.author.mention}, your game has ended. Start a new one anytime with `!start [difficulty]`.")
    else:
        await ctx.send(f"{ctx.author.mention}, you don't have an active game.")

# Error handling for bad command usage
@start_command.error
@guess_command.error
async def param_error(ctx, error):
    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid command usage. Type `!help` for usage instructions.")
    else:
        await ctx.send(f"An error occurred: {error}")

if __name__ == "__main__":
    bot.run(TOKEN)

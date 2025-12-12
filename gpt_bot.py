import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Basic sanity check
if not OPENAI_API_KEY:
    print("FATAL ERROR: OPENAI_API_KEY  must be set in the .env file.")
    exit()

if not DISCORD_TOKEN:
    print("FATAL ERROR: DISCORD_TOKEN must be set in the .env file.")
    exit()

# --- Initialize Clients ---
# Initialize the OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize the Discord bot client
# Define intents needed for the bot (reading messages, responding, etc.)
intents = discord.Intents.default()
intents.message_content = True  # Mandatory to read the content of messages
bot = commands.Bot(command_prefix='!', intents=intents)


# --- Discord Bot Events and Commands ---

@bot.event
async def on_ready():
    """Prints status message when the bot successfully connects to Discord."""
    print(f'Bot is ready. Logged in as {bot.user.name} (ID: {bot.user.id})')
    # Set the bot's activity status
    await bot.change_presence(activity=discord.Game(name="Chatting with gpt-5-mini!"))


@bot.command(name='gpt', help='Ask gpt-5-mini a question. Usage: !gpt What is the capital of France?')
async def gpt_command(ctx, *args):
    """
    Handles the '!gpt' command, sends the user's prompt to the OpenAI API,
    and sends the response back to the Discord channel.
    """
    # Combine all arguments into a single user prompt string
    user_prompt = " ".join(args)

    if not user_prompt:
        await ctx.send("Please provide a question after the `!gpt` command. Example: `!gpt Write a haiku about computers.`")
        return

    # Use a dynamic loading message since the API call can take a moment
    await ctx.send(f"🤖 **Processing prompt for {ctx.author.display_name}...** (Model: gpt-5-mini)")

    try:
        # 3. Call the OpenAI API using the user's prompt
        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                # System instructions set the tone/persona
                {"role": "system", "content": "You are a helpful, concise, and friendly Discord bot. Keep your answers brief and relevant."},
                # The actual user query
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract the content
        gpt_response = response.choices[0].message.content

        # 4. Send the API response back to the Discord channel
        # Discord messages have a character limit (2000). We send the response in a code block.
        if len(gpt_response) > 1900:
            # If the response is too long, truncate or split it (simple truncation here)
            gpt_response = gpt_response[:1900] + "...\n[Response too long, truncated.]"

        await ctx.send(f"**{ctx.author.display_name} asked:** {user_prompt}\n\n"
                       f"```markdown\n{gpt_response}\n```")

    except Exception as e:
        print(f"An error occurred during API call: {e}")
        await ctx.send("An error occurred while talking to the OpenAI API. Please try again later.")

# 5. Run the bot using the Discord token
bot.run(DISCORD_TOKEN)
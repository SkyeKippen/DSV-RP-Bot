import discord
import os
from tqdm import tqdm
from discord import Interaction, app_commands
from discord.ext import commands
from typing import Literal  # For fixed choices
import random
import datetime
import json
import aiohttp
import asyncio
from llama_cpp import Llama

# Invite link: https://discord.com/oauth2/authorize?client_id=1353334629246959656&permissions=397284591680&integration_type=0&scope=bot+applications.commands

TOKEN = "MTM1MzMzNDYyOTI0Njk1OTY1Ng.GhZMOH.yAikXCkv3V7u8xbz6IgKYNOLh-qHxKtB9izkL4"

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Slash commands synced!")

@bot.tree.command(name="shutdown", description="Shuts down the bot (admin only)")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == 305861137440833536:  # Replace with your Discord user ID
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        await bot.change_presence(status=discord.Status.offline)  # Set offline before closing
        await bot.close()
    else:
        await interaction.response.send_message("You do not have permission!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()  # Sync slash commands with Discord
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

### DICE STUFF
@bot.tree.command(name="roll_dice", description="Rolls a specified set of dice")
@app_commands.describe(
    sides="How many sides on the dice?",
    quantity="How many dice do you want to roll?"
    )
async def rolldice(
    interaction: discord.Interaction,
    sides: Literal["D2","D4","D6","D8","D10","D12","D20","D100"],
    quantity: int
    ):
    await interaction.response.defer()  # Defer response to allow time
    
    rolled = 0
    results=[]
    while (rolled < quantity):
        ## Dice Rolls
        if sides == "D2":
            dice_roll = random.randint(1,2)
        elif sides == "D4":
            dice_roll = random.randint(1,4)
        elif sides == "D6":
            dice_roll = random.randint(1,6)
        elif sides == "D8":
            dice_roll = random.randint(1,8)
        elif sides == "D10":
            dice_roll = random.randint(1,10)
        elif sides == "D12":
            dice_roll = random.randint(1,12)
        elif sides == "D20":
            dice_roll = random.randint(1,20)
        elif sides == "D100":
            dice_roll = random.randint(1,100)
        else: 
            dice_roll = "ERROR: Invalid Side Count"
            break
        
        results.append(str(dice_roll))
        rolled += 1

    await interaction.followup.send(f"Results of {quantity} x {sides} Rolled: {', '.join(results)}")
    
    return

@bot.tree.command(name="roll-d20", description="Rolls a D20")
async def rolld20(
    interaction: discord.Interaction
    ):
    await interaction.response.defer()  # Defer response to allow time
    dice_roll = random.randint(1,20)
    await interaction.followup.send(dice_roll)
    return

# Absolute path to the directory containing THIS script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

## Statics
DISCORD_MESSAGE_LIMIT = 2000

### LLM STUFF
CHANNEL_NAME = "rp-testing"
MAX_TOKENS = 8000
MAX_MEM_LINES = 20
MAX_MEM_LINE_LENGTH = 500
BATCH_SIZE = 64
LLM_TEMPERATURE = 0.7

webhook_urls = {
    "BERTI": "https://discord.com/api/webhooks/1363814560443797655/8qaVNB0tORdUD9YffkuTc-4fU8xCow3QMS8Ta8I307j6m4vIQUUoOjQ5grxQUx5hVMzP",
    "FORGE": "https://discord.com/api/webhooks/1364826606379597864/kBe23Hh53WHJ53L8Q4QK4opSAZVrejDUQ_rMvQywCGV9ithBSY5KtB5S_3-WGOdnjm6-",
    "UNITE": "https://discord.com/api/webhooks/1364826696166936656/EqU3Nk80KMdrtUhEM0pHknsksYBAboxmto0tRsWnleFXTGMM8MZ8sSLVNi6hI_30ldAJ"
}

webhook_usernames = {
    "BERTI": "BERTI Executive Chancellor Liora Castane",
    "FORGE": "FORGE Archon Zeraphiel Kain",
    "UNITE": "UNITE Secretary-General Elias Marcone"
}

llm = Llama(
    model_path=os.path.join(BASE_DIR, "LLM", "mythomax-l2-13b.Q5_K_M.gguf"),
    n_ctx=MAX_TOKENS,
    n_threads=14,
    n_batch=BATCH_SIZE
)

role_prefix_map = {
    "[SKA] Skye's Ascendency": "[SKA]",
}

def load_rp_name_map(path=os.path.join(BASE_DIR, "name_map.json")):
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_map = json.load(f)
            # Convert keys from strings to integers (user IDs)
            return {int(k): v for k, v in raw_map.items()}
    except Exception as e:
        print(f"[ERROR] Failed to load RP name map: {e}")
        return {}

rp_name_map = load_rp_name_map()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.name == CHANNEL_NAME:
        log_entry_base = {
            "timestamp": str(datetime.datetime.utcnow()),
            "author": message.author.display_name,
            "content": message.content,
            "source": "user"  # Correctly mark this as a player-origin message
        }

        factions = ["BERTI", "FORGE", "UNITE"]

        for faction in factions:
            mem_path = os.path.join(BASE_DIR, f"memory_{faction.lower()}.json")
            with open(mem_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry_base, ensure_ascii=False) + "\n")

        print(f"[LOGGED to all factions] {log_entry_base}")



def load_memory(path=None, max_lines=MAX_MEM_LINES, max_entry_length=MAX_MEM_LINE_LENGTH):
    memory = []
    if path is None:
        path = os.path.join(BASE_DIR, "memory_log.json")  # Default fallback

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-max_lines:]
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    msg = entry["content"][:max_entry_length]
                    author = entry.get("author", "Unknown")
                    memory.append(f"{author} said: {msg}")
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return memory

def get_rp_name(user: discord.User) -> str:
    # Try exact match by ID
    if user.id in rp_name_map:
        return rp_name_map[user.id]

    # Role fallback (if you're using role_prefix_map)
    for role in user.roles:
        if role.name in role_prefix_map:
            return f"{role_prefix_map[role.name]} {user.display_name}"

    # Final fallback
    return user.display_name

def load_faction_personalities(path=os.path.join(BASE_DIR, "faction_personalities.json")):
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return {
                k.upper(): "\n".join(v) if isinstance(v, list) else str(v)
                for k, v in raw.items()
            }
    except Exception as e:
        print(f"[ERROR] Failed to load personalities: {e}")
        return {}


    
faction_personalities = load_faction_personalities()

def load_summary() -> str:
    path = os.path.join(BASE_DIR, "summarized_memory_compact.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            summary = f.read().strip()
            print("[OK] Loaded shared summary.\n")
            return summary
    except FileNotFoundError:
        print("[ERROR] Shared summary file not found.")
        return ""

    
def build_prompt(player_question, player_name, faction):
    faction = faction.upper()

    # Personality
    personality = faction_personalities.get(faction.upper(), "")
    if not personality.strip():
        personality = "You are the authoritative representative of your faction. Speak firmly and with purpose."

    # Summary (long-term memory)
    summary = load_summary()

    # Recent memory (short-term)
    memory = load_memory(f"memory_{faction.lower()}.json")
    history = "\n".join(f"- {event}" for event in memory[-8:])

    # Build the prompt (no Q&A format)
    return (
    f"{personality}\n\n"
    "Current Territorial Control:\n"
    "- BERTI: Tarlian (home), Lyara, Sonchia\n"
    "- UNITE: Sevella (home), Tadara, Anatos\n"
    "- FORGE: Nibrax (home), Kuesh, Plunia\n\n"
    f"Summary of important past events:\n{summary}\n\n"
    f"Recent diplomatic activity and communications:\n{history}\n\n"
    "### Player Message:\n"
    f"{player_name}: \"{player_question}\"\n\n"
    "### Instructions:\n"
    "You are the representative of your faction.\n"
    "Respond in character, with a single message.\n"
    "Do not include or restate the player's message.\n"
    "Do not write narration or story text. Do not describe actions, thoughts, or scene transitions.\n"
    "Never break character.\n\n"
    f"Respond **as the faction representative of {faction}**, not any other entity."
    "### Response:\n"

)

def generate_response(prompt, max_out):
    response = ""
    for part in llm(prompt, max_tokens=max_out, stream=True, temperature=LLM_TEMPERATURE, stop=["###"]):
        token = part["choices"][0]["text"]
        response += token
    return response


def clean_response(text, faction):
    # Get the representative's first name (e.g., "Liora" from "Liora Castane")
    name = webhook_usernames[faction].split()[-1]  # Last word = "Castane", "Kain", "Marcone"
    if text.strip().startswith(f"{name}:"):
        text = text.strip()[len(name)+1:].strip()
    return text


def count_tokens(text: str) -> int:
    tokens = llm.tokenize(text.encode("utf-8"), add_bos=False)
    return len(tokens)

def safe_max_tokens(prompt, buffer=64):
    prompt_tokens = len(llm.tokenize(prompt.encode("utf-8"), add_bos=False))
    return max(llm.context_params.n_ctx - prompt_tokens - buffer, 0)

async def send_via_webhook(webhook_url, content, username="Faction AI", avatar_url=None, log_to=None):
    async with aiohttp.ClientSession() as session:
        payload = {
            "content": content,
            "username": username
        }
        if avatar_url:
            payload["avatar_url"] = avatar_url

        async with session.post(webhook_url, json=payload) as response:
            if response.status != 204:
                print(f"[ERROR] Webhook failed: {response.status}")
            else:
                print(f"[OK] Sent message via webhook: {username}")
                
                if log_to:
                    log_entry = {
                        "timestamp": str(datetime.datetime.utcnow()),
                        "author": username,
                        "content": content
                    }

                    # Allow logging to a list of factions
                    for faction_name in log_to:
                        mem_path = os.path.join(BASE_DIR, f"memory_{faction_name.lower()}.json")
                        try:
                            with open(mem_path, "a", encoding="utf-8") as f:
                                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                            print(f"[OK] Logged to {faction_name}")
                        except Exception as e:
                            print(f"[ERROR] Failed to log to {faction_name}: {e}")


# Split long messages into safe Discord chunks
def split_message(message: str, chunk_size: int, other_limit: int = 2000):
    chunks = []

    if len(message) > chunk_size:
        split_at = max(message.rfind("\n", 0, chunk_size), message.rfind(". ", 0, chunk_size) + 1)
        if split_at <= 0:
            split_at = chunk_size
        chunks.append(message[:split_at].strip())
        message = message[split_at:].strip()
    else:
        return [message]

    while len(message) > other_limit:
        split_at = max(message.rfind("\n", 0, other_limit), message.rfind(". ", 0, other_limit) + 1)
        if split_at <= 0:
            split_at = other_limit
        chunks.append(message[:split_at].strip())
        message = message[split_at:].strip()

    if message:
        chunks.append(message)

    return chunks


@bot.tree.command(name="ask_faction", description="Ask the BERTI AI a question.")
@app_commands.describe(question="What do you want to ask the faction?", faction="Which faciton are you asking?")
async def ask_faction(interaction: discord.Interaction, question: str, faction: Literal["BERTI", "FORGE", "UNITE"]):
    allowed_channels = ["rp-testing"]  # You can also use IDs if you prefer

    if interaction.channel.name not in allowed_channels:
        await interaction.response.send_message(
            "[ERROR] This command can only be used in the RP channels.",
            ephemeral=True
        )
        return

    await interaction.response.defer()  # basic defer, no typing dots

    # Send "Transmission received" message immediately after deferring
    # Send a visible message that will auto-delete
    transmission_msg = await interaction.followup.send("Transmission received. Please Await a reply")
    await asyncio.sleep(30)  # Delay in seconds
    await transmission_msg.delete()


    player_name = get_rp_name(interaction.user)
    prompt = build_prompt(question, player_name, faction)
    token_count = count_tokens(prompt)
    max_out = safe_max_tokens(prompt)

    progress = tqdm(total=max_out)
    response = ""

    print("Final prompt length:", len(prompt))
    print("Final prompt preview:\n", prompt[:500])

    token_count = count_tokens(prompt)
    max_out = safe_max_tokens(prompt)
    print(f"Prompt token count: {token_count}")
    print(f"Max tokens allowed for output: {max_out}")

    print("Personality (raw):", repr(faction_personalities.get(faction)))

    print("Final Prompt Preview:\n", prompt[-1000:])  # Last 1000 chars


    try:
        for part in llm(prompt, max_tokens=max_out, stream=True, temperature=LLM_TEMPERATURE, stop=["###"]):
            token = part["choices"][0]["text"]
            response += token
            progress.update(1)
    except Exception as e:
        print("Prompt that caused error:\n", prompt)
        raise e
    finally:
        progress.close()

    print(f"Raw response (repr): {repr(response)}")

    # Skip sending if the response is empty or whitespace
    if not response.strip():
        print("[ERROR] Model generated an empty response. Nothing will be sent.")
        return

    response = await asyncio.to_thread(generate_response, prompt, max_out)

    response = clean_response(response, faction)

    # Send via webhook after streaming is complete...
    suffix = f""
    first_chunk_limit = DISCORD_MESSAGE_LIMIT - len(suffix)
    chunks = split_message(response, first_chunk_limit)

    for i, chunk in enumerate(chunks):
        print(f"Response length: {len(response)} characters")
        print(f"Chunks created: {len(chunks)}")
        print(f"First chunk preview: {repr(chunks[0])[:100]}...")
        print(f"Token count for prompt: {token_count}")
        await send_via_webhook(
            webhook_url=webhook_urls[faction],
            content=f"{chunk}{suffix if i == 0 else ''}",
            username=webhook_usernames[faction],
            #log_to=["BERTI", "FORGE", "UNITE"]
        )


bot.run(TOKEN)
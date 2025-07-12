import discord
from discord.ext import commands
import json
import os

CHARACTER_FILE = "characters.json"

def load_characters():
    if not os.path.exists(CHARACTER_FILE):
        with open(CHARACTER_FILE, "w") as f:
            json.dump({}, f)
    with open(CHARACTER_FILE, "r") as f:
        return json.load(f)

def save_characters(data):
    with open(CHARACTER_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = load_characters()

    def get_user_characters(self, user_id):
        return self.characters.get(str(user_id), [])

    def save_user_characters(self, user_id, char_list):
        self.characters[str(user_id)] = char_list
        save_characters(self.characters)

    @commands.group(name="char", invoke_without_command=True)
    async def char_group(self, ctx):
        await ctx.send("Available subcommands: create, view, list, edit, delete")

    @char_group.command()
    async def create(self, ctx):
        await ctx.send("Let's create your character. You can type `cancel` at any time to stop.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            fields = {
                "name": "What is your character's **name**?",
                "age": "How old is your character?",
                "gender": "What is your character's **gender**?",
                "species": "What **species/race** is your character?",
                "affiliation": "What **affiliation or group** are they part of?",
                "role": "What is their **role or occupation**?",
                "personality": "Describe their **personality** in a few words.",
                "backstory": "Give a brief **backstory** (or type `skip` to leave blank).",
                "abilities": "What are their **abilities or powers**?",
                "avatar": "Optional: paste an **image URL** for your character's avatar (or type `skip`)."
            }

            char_data = {}
            for key, prompt in fields.items():
                await ctx.send(prompt)
                msg = await self.bot.wait_for("message", check=check, timeout=300)
                content = msg.content.strip()
                if content.lower() == "cancel":
                    await ctx.send("Character creation cancelled.")
                    return
                if key in ["backstory", "avatar"] and content.lower() == "skip":
                    char_data[key] = ""
                else:
                    char_data[key] = content

            user_id = str(ctx.author.id)
            if user_id not in self.characters:
                self.characters[user_id] = []
            self.characters[user_id].append(char_data)
            save_characters(self.characters)

            await ctx.send(f"Character **{char_data['name']}** created successfully!")

        except Exception as e:
            await ctx.send("Character creation timed out or failed. Please try again.")

    @char_group.command()
    async def list(self, ctx):
        user_chars = self.get_user_characters(ctx.author.id)
        if not user_chars:
            await ctx.send("You have no characters.")
            return

        embed = discord.Embed(title="Your Characters", color=discord.Color.purple())
        for char in user_chars:
            embed.add_field(name=char["name"], value=f"{char['species']} - {char['role']}", inline=False)
        await ctx.send(embed=embed)

    @char_group.command()
    async def view(self, ctx, *, name: str):
        user_chars = self.get_user_characters(ctx.author.id)
        for char in user_chars:
            if char["name"].lower() == name.lower():
                embed = discord.Embed(title=char["name"], color=discord.Color.blue())
                embed.add_field(name="Age", value=char["age"], inline=True)
                embed.add_field(name="Gender", value=char["gender"], inline=True)
                embed.add_field(name="Species", value=char["species"], inline=True)
                embed.add_field(name="Affiliation", value=char["affiliation"], inline=True)
                embed.add_field(name="Role", value=char["role"], inline=True)
                embed.add_field(name="Personality", value=char["personality"], inline=False)
                if char["backstory"]:
                    embed.add_field(name="Backstory", value=char["backstory"], inline=False)
                if char["abilities"]:
                    embed.add_field(name="Abilities", value=char["abilities"], inline=False)
                if char["avatar"]:
                    embed.set_thumbnail(url=char["avatar"])
                await ctx.send(embed=embed)
                return
        await ctx.send("Character not found.")

    @char_group.command()
    async def delete(self, ctx, *, name: str):
        user_id = str(ctx.author.id)
        user_chars = self.get_user_characters(user_id)
        for i, char in enumerate(user_chars):
            if char["name"].lower() == name.lower():
                del user_chars[i]
                self.save_user_characters(user_id, user_chars)
                await ctx.send(f"Character **{name}** deleted.")
                return
        await ctx.send("Character not found.")

async def setup(bot):
    await bot.add_cog(Characters(bot))
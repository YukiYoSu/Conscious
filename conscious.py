import discord
from discord.ext import commands
import json
import os
import asyncio

CHAR_FILE = "characters.json"
LORE_FILE = "lore.json"

def load_json(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(default_data, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

class Conscious(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = load_json(CHAR_FILE, {"characters": {}})
        self.lore = load_json(LORE_FILE, {"lore_entries": {}})

    # ------------- Lore Commands -------------

    @commands.group(invoke_without_command=True)
    async def lore(self, ctx):
        await ctx.send("Lore commands: add, view <title>, list, edit <title>, delete <title>")

    @lore.command()
    async def add(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Enter the **title** of the new lore entry:")

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=120)
            title = msg.content.strip()
            if title.lower() in self.lore["lore_entries"]:
                await ctx.send("A lore entry with that title already exists!")
                return

            await ctx.send("Enter the **content** of the lore entry:")
            msg = await self.bot.wait_for('message', check=check, timeout=600)
            content = msg.content.strip()

            self.lore["lore_entries"][title.lower()] = {
                "title": title,
                "author": str(ctx.author),
                "content": content,
                "date_added": ctx.message.created_at.isoformat()
            }
            save_json(LORE_FILE, self.lore)
            await ctx.send(f"Lore entry **{title}** added successfully!")

        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")

    @lore.command()
    async def view(self, ctx, *, title: str):
        entry = self.lore["lore_entries"].get(title.lower())
        if not entry:
            await ctx.send("Lore entry not found.")
            return

        embed = discord.Embed(title=entry["title"], description=entry["content"], color=discord.Color.green())
        embed.set_footer(text=f"Written by {entry['author']} on {entry['date_added'][:10]}")
        await ctx.send(embed=embed)

    @lore.command()
    async def list(self, ctx):
        entries = self.lore["lore_entries"]
        if not entries:
            await ctx.send("No lore entries found.")
            return

        titles = sorted(entry["title"] for entry in entries.values())
        await ctx.send("Lore Entries:\n" + "\n".join(titles))

    @lore.command()
    async def edit(self, ctx, *, title: str):
        entry = self.lore["lore_entries"].get(title.lower())
        if not entry:
            await ctx.send("Lore entry not found.")
            return

        if str(ctx.author) != entry["author"] and not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to edit this lore entry.")
            return

        await ctx.send(f"Editing lore entry **{entry['title']}**. Send the new content:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=600)
            new_content = msg.content.strip()
            self.lore["lore_entries"][title.lower()]["content"] = new_content
            save_json(LORE_FILE, self.lore)
            await ctx.send(f"Lore entry **{entry['title']}** updated!")

        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")

    @lore.command()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, *, title: str):
        if title.lower() not in self.lore["lore_entries"]:
            await ctx.send("Lore entry not found.")
            return

        del self.lore["lore_entries"][title.lower()]
        save_json(LORE_FILE, self.lore)
        await ctx.send(f"Lore entry **{title}** deleted.")

async def setup(bot):
    await bot.add_cog(Conscious(bot))

import discord
from discord.ext import commands
from discord.commands import slash_command, SlashCommandGroup
import sqlite3

class AutoPublisher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('db/autopublisher.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY)")
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.TextChannel) and message.channel.is_news():
            self.cursor.execute("SELECT id FROM channels WHERE id = ?", (message.channel.id,))
            result = self.cursor.fetchone()
            if result:
                await message.publish()

    autopublisher_commands = SlashCommandGroup("autopublisher", "Befehle zur Verwaltung von Einladungen")

    @autopublisher_commands.command(description='Aktiviert den AutoPublisher für einen Channel.')
    async def on(self, ctx: discord.ApplicationContext, channel: discord.Option(discord.TextChannel, "Wähle einen Kanal", required=False)):
        if channel is None:
            if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.is_news():
                self.cursor.execute("INSERT OR IGNORE INTO channels (id) VALUES (?)", (ctx.channel.id,))
                self.conn.commit()
                await ctx.respond(f"AutoPublisher wurde für diesen Ankündigungs-Kanal aktiviert.", ephemeral=True)
            else:
                await ctx.respond("Dieser Kanal ist kein Ankündigungs-Kanal.", ephemeral=True)
        else:
            if channel.is_news():
                self.cursor.execute("INSERT OR IGNORE INTO channels (id) VALUES (?)", (channel.id,))
                self.conn.commit()
                await ctx.respond(f"AutoPublisher wurde für {channel.mention} aktiviert.")
            else:
                await ctx.respond("Der gewählte Kanal ist kein Ankündigungs-Kanal.", ephemeral=True)

    @autopublisher_commands.command(description='Deaktiviert den AutoPublisher für einen Channel.')
    async def off(self, ctx, channel: discord.Option(discord.TextChannel, "Wähle einen Kanal", required=False)):
        if channel is None:
            self.cursor.execute("DELETE FROM channels WHERE id = ?", (ctx.channel.id,))
            self.conn.commit()
            await ctx.respond(f"AutoPublisher wurde für diesen Kanal deaktiviert.", ephemeral=True)
        else:
            self.cursor.execute("DELETE FROM channels WHERE id = ?", (channel.id,))
            self.conn.commit()
            await ctx.respond(f"AutoPublisher wurde für {channel.mention} deaktiviert.")

def setup(bot):
    bot.add_cog(AutoPublisher(bot))

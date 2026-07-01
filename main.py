import discord
from discord.ext import commands
from utils import log, get_config
import dashboard

config = get_config()


class SelfMusicBot(commands.Bot):
    def __init__(self):
        prefix = str(config.get("prefix") or "$")
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            self_bot=True,
            help_command=None,
        )
        self.start_time = None
        self.songs_played = 0

    async def setup_hook(self):
        log("Loading cogs...")
        await self.load_extension('cogs.music')
        log("✅ Cogs loaded.")

        dashboard.init_app(self)
        port = int(config.get("dashboard_port") or 5000)
        host = str(config.get("dashboard_host") or "0.0.0.0")
        self.loop.create_task(dashboard.app.run_task(host=host, port=port))
        log(f"✅ Dashboard running at http://127.0.0.1:{port}")

    async def on_ready(self):
        import time
        self.start_time = time.time()
        log(f"✅ Logged in as {self.user} (ID: {self.user.id})")

        status_type_str = str(config.get("bot_status_type", "listening")).lower()
        activity_name = str(config.get("bot_activity_name", "🎵 Music | MADE BY SUBHAN"))

        if status_type_str == "playing":
            activity = discord.Game(name=activity_name)
        elif status_type_str == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
        elif status_type_str == "competing":
            activity = discord.Activity(type=discord.ActivityType.competing, name=activity_name)
        else:
            activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)

        await self.change_presence(status=discord.Status.online, activity=activity)
        log(f"✅ Bot status set: {status_type_str.capitalize()} to '{activity_name}'")
        log("Bot is ready!")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Bad argument: {error}")
            return
        log(f"Command error in '{ctx.command}': {error}")
        try:
            await ctx.send(f"❌ An error occurred: `{error}`")
        except Exception:
            pass

    async def on_command(self, ctx):
        log(f"CMD: '{ctx.message.content}' by {ctx.author} in {ctx.guild}/{ctx.channel}")

    async def on_message(self, message):
        await self.process_commands(message)


bot = SelfMusicBot()

if __name__ == "__main__":
    token = str(config.get("token") or "").strip()
    if not token or token in {"YOUR_TOKEN_HERE", "token"}:
        log("❌ Invalid token. Please set a valid token in .env or Railway variables.")
    else:
        log("🚀 Starting Self Music Bot...")
        try:
            bot.run(token)
        except discord.LoginFailure:
            log("❌ Login failed. Invalid token.")
        except Exception as e:
            log(f"❌ Fatal error: {e}")

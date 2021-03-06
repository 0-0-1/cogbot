from discord.ext import commands
from discord.ext.commands import Context

from cogbot.cog_bot import CogBot


def is_manager_check(ctx: Context):
    bot = ctx.bot  # type: CogBot
    return ctx.message.author.id in bot.state.managers


def is_manager():
    return commands.check(lambda ctx: is_manager_check(ctx))


def is_moderator_check(ctx: Context):
    if is_manager_check(ctx):
        return True

    # TODO check if user has appropriate server permissions
    return False


def is_moderator():
    return commands.check(lambda ctx: is_moderator_check(ctx))

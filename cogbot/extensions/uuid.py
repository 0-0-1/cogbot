import logging
import re

from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.errors import *

from cogbot.cog_bot import CogBot

log = logging.getLogger(__name__)


class UUID:
    UUID_PATTERN = re.compile('([0-9A-F]{1,8})-([0-9A-F]{1,4})-([0-9A-F]{1,4})-([0-9A-F]{1,4})-([0-9A-F]{1,12})|([0-9a-f]{1,8})-([0-9a-f]{1,4})-([0-9a-f]{1,4})-([0-9a-f]{1,4})-([0-9a-f]{1,12})')

    INT_PATTERN = re.compile(r'[+\-]?[0-9]+')

    def __init__(self, bot):
        self.bot : Bot = bot
    
    def combine_num_64(self, *num_64) -> int:
        nums = []
        for num in num_64:
            if num > 9223372036854775807 or num < -9223372036854775808:
                raise CommandError(f'one of the provided numbers is not in a valid range: {num}')
            if num < 0:
                num = 18446744073709551616 + num
            nums.append(num)
        
        return ((nums[0] << 64) | nums[1])

    def split_num_128(self, num_128 : int):
        least_significant_bits : int = num_128 & 18446744073709551615
        most_significant_bits : int = num_128 >> 64

        if least_significant_bits > 9223372036854775807:
            least_significant_bits -= 18446744073709551616
        
        if most_significant_bits > 9223372036854775807:
            most_significant_bits -= 18446744073709551616

        return (most_significant_bits, least_significant_bits)

    def string_from_num_128(self, num_128: int) -> str:
        components = []

        components.append(hex(num_128 >> 96)[2:])
        components.append(hex((num_128 >> 80) & 65535)[2:])
        components.append(hex((num_128 >> 64) & 65535)[2:])
        components.append(hex((num_128 >> 48) & 65535)[2:])
        components.append(hex(num_128 & 281474976710655)[2:])

        component_lengths = (8, 4, 4, 4, 12)
        
        for i in range(0, 5):
            component = components[i]
            component_length = len(component)
            proper_component_length = component_lengths[i]

            if component_length < proper_component_length:
                components[i] = ('0'*(proper_component_length-component_length)) + component

        return '-'.join(components)

    def num_128_from_string(self, uuid_string) -> int:
        match = self.UUID_PATTERN.match(uuid_string)

        if match is None:
            raise CommandError(f'the provided UUID is not in a valid format: {uuid_string}')

        start = 0
        if match[1] is None:
            start = 5

        return ((((int(match[start+5], 16) | (int(match[start+4], 16) << 48)) | (int(match[start+3], 16) << 64)) | (int(match[start+2], 16) << 80)) | (int(match[start+1], 16) << 96))

    async def uuid_from_num_64_cmd(self, ctx: Context, most_significant_bits: int, least_significant_bits: int):
        await self.bot.say(f'Generated UUID: `{self.string_from_num_128(self.combine_num_64(most_significant_bits, least_significant_bits))}`')
    
    async def num_64_from_uuid_cmd(self, ctx: Context, uuid_string):
        num_64 = self.split_num_128(self.num_128_from_string(uuid_string))
        await self.bot.say(f'UUIDMost: `{num_64[0]}`\nUUIDLeast: `{num_64[1]}`')
    
    @commands.group(pass_context=True, name='uuid')
    async def cmd_uuid(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            raise CommandError('UUID command invoked with no arguments')
    
    @cmd_uuid.command(pass_context=True, name='join')
    async def cmd_uuid_join(self, ctx: Context, UUIDMost, UUIDLeast):
        if self.INT_PATTERN.match(UUIDMost) is None or self.INT_PATTERN.match(UUIDLeast) is None:
            raise CommandError(f'UUID components must be integers, but at least one is not: ({UUIDMost}, {UUIDLeast})')
        
        await self.uuid_from_num_64_cmd(ctx, int(UUIDMost), int(UUIDLeast))
    
    @cmd_uuid.command(pass_context=True, name='split')
    async def cmd_uuid_split(self, ctx: Context, *, UUID):
        await self.num_64_from_uuid_cmd(ctx, UUID)


def setup(bot):
    bot.add_cog(UUID(bot))
import logging

from NetUtils import ClientStatus, color
from worlds.AutoSNIClient import SNIClient

snes_logger = logging.getLogger("SNES")

# FXPAK Pro protocol memory mapping used by SNI
"""
[HiROM, no 0x200 @ 0xFFC0]
 Title       : EARTH BOUND          
 Map Mode    : 0x31
 ROM Type    : 0x02
 ROM Size    : 0x0C
 SRAM Size   : 0x03
 Checksum    : 0x4048
 Inverse     : 0xBFB7
65984
"""

ROM_START = 0x000000
WRAM_START = 0xF50000
WRAM_SIZE = 0x20000
SRAM_START = 0xE00000

EARTHBOUND_ROMNAME_START = 0x00FFC0
EARTHBOUND_ROMHASH_START = 0x7FC0
ROMNAME_SIZE = 0x15
ROMHASH_SIZE = 0x15

EARTHBOUND_RECV_PROGRESS_ADDR = WRAM_START + 0x632
EARTHBOUND_FILE_NAME_ADDR = WRAM_START + 0x5D9
DEATH_LINK_ACTIVE_ADDR = EARTHBOUND_ROMNAME_START + 0x15     # EARTHBOUND_TODO: Find a permanent home for this


class EarthBoundSNIClient(SNIClient):
    game = "EarthBound"
    patch_suffix = ".apdkc3"

    async def deathlink_kill_player(self, ctx):
        pass
        # EARTHBOUND_TODO: Handle Receiving Deathlink


    async def validate_rom(self, ctx):
        from SNIClient import snes_read

        rom_name = await snes_read(ctx, EARTHBOUND_ROMHASH_START, ROMHASH_SIZE)

        # EARTHBOUND_TODO: Update validation for EarthBound ROM
        if rom_name is None or rom_name == bytes([0] * ROMHASH_SIZE) or rom_name[:2] != b"D3":
            return False

        ctx.game = self.game
        ctx.items_handling = 0b111  # remote items

        ctx.rom = rom_name

        #death_link = await snes_read(ctx, DEATH_LINK_ACTIVE_ADDR, 1)
        ## EARTHBROUND_TODO: Handle Deathlink
        #if death_link:
        #    ctx.allow_collect = bool(death_link[0] & 0b100)
        #    await ctx.update_death_link(bool(death_link[0] & 0b1))
        return True
    
    
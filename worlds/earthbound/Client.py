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
    patch_suffix = ".apeb"

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
        ## EARTHBOUND_TODO: Handle Deathlink
        #if death_link:
        #    ctx.allow_collect = bool(death_link[0] & 0b100)
        #    await ctx.update_death_link(bool(death_link[0] & 0b1))
        return True
    
    async def game_watcher(self, ctx):
        from SNIClient import snes_buffered_write, snes_flush_writes, snes_read
        # EARTHBOUND_TODO: Handle Deathlink
        save_file_name = await snes_read(ctx, EARTHBOUND_FILE_NAME_ADDR, 0x5)
        if save_file_name is None or save_file_name[0] == 0x00 or save_file_name == bytes([0x55] * 0x05):
            # We haven't loaded a save file
            return
    
        new_checks = []
        # EARTHBOUND_TODO: Add location data and verify location data for this function
        from .Rom import location_rom_data, item_rom_data, boss_location_ids, level_unlock_map
        location_ram_data = await snes_read(ctx, WRAM_START + 0x5FE, 0x81)
        for loc_id, loc_data in location_rom_data.items():
            if loc_id not in ctx.locations_checked:
                data = location_ram_data[loc_data[0] - 0x5FE]
                masked_data = data & (1 << loc_data[1])
                bit_set = (masked_data != 0)
                invert_bit = ((len(loc_data) >= 3) and loc_data[2])
                if bit_set != invert_bit:
                    # EARTHBOUND_TODO: Handle non-included checks
                    new_checks.append(loc_id)

        verify_save_file_name = await snes_read(ctx, EARTHBOUND_FILE_NAME_ADDR, 0x5)
        if verify_save_file_name is None or verify_save_file_name[0] == 0x00 or verify_save_file_name == bytes([0x55] * 0x05) or verify_save_file_name != save_file_name:
            # We have somehow exited the save file (or worse)
            ctx.rom = None
            return

        rom = await snes_read(ctx, EARTHBOUND_ROMHASH_START, ROMHASH_SIZE)
        if rom != ctx.rom:
            ctx.rom = None
            # We have somehow loaded a different ROM
            return
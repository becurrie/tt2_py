"""
maps.py

Map any values into a single location useful for determining locations on screen
and mapping the proper values and coordinates to their respective keys.
"""
from settings import IMAGE_DIR

# Some emulators apply some padding or wrapping around their window. This can be accounted for by mapping
# the padding and dealing with it during screenshots.
EMULATOR_PADDING_MAP = {
    "nox": {
        "x": 5,
        "y": 38,
    },
}

EMULATOR_LOCS = {
    "nox": {
        "opened_apps": (500, 815),
        "close_game": (405, 242),
        # The launch game location for all emulators / sizes should be based off of the app being placed
        # in the top most left corner of the home screen within the emulator.
        "launch_game": (53, 232),
    },
}

# All points in game that are relevant to the given resolution can be stored here.
# Not all locations need to be stored here, only locations that otherwise would be
# more of an issue trying to click on after looking for a different image.
GAME_LOCS = {
    "BOTTOM_BAR": {
        "master": (39, 815),
        "heroes": (120, 815),
        "equipment": (200, 815),
        "pets": (281, 815),
        "artifacts": (362, 815),
        "shop": (442, 815),
    },
    "DAILY_REWARD": {
        "open_rewards": (34, 210),
        "close_rewards": (430, 260),
        "collect_rewards": (240, 560),
    },
    "SKILL_BAR": {
        "heavenly_strike": (43, 744),
        "deadly_strike": (123, 744),
        "hand_of_midas": (200, 744),
        "fire_sword": (283, 744),
        "war_cry": (363, 744),
        "shadow_clone": (444, 744),
    },
    "GAME_SCREEN": {
        "fight_boss": (425, 65),
        "game_middle": (250, 320),
        "player": (235, 421),
        "pet_gold": (287, 411),
        "pet_attack": (235, 377),
        "clan_ship": (60, 188),
        # Start any scroll functions from this point.
        "scroll_start": (328, 530),
        "scroll_top_end": (328, 765),
        "scroll_bottom_end": (328, 80),
        "scroll_quick_stop": (328, 780),
        # The fairies map is looped through and each point is pressed
        # sequentially, this will ensure that fairies are pressed if present.
        "fairies_map": (
            (75, 125), (100, 125), (140, 125), (200, 125), (260, 125), (320, 125), (380, 125), (440, 125),
            (75, 160), (100, 160), (140, 160), (200, 160), (260, 160), (320, 160), (380, 160), (440, 160),
            (75, 230), (100, 230), (140, 230), (200, 230), (260, 230), (320, 230), (380, 230), (440, 230),
            (75, 300), (100, 300), (140, 300), (200, 300), (260, 300), (320, 300), (380, 300), (440, 300),
            (75, 370), (100, 370), (140, 370), (200, 370), (260, 370), (320, 370), (380, 370), (440, 370),
            (75, 440), (100, 440), (140, 440), (200, 440), (260, 440), (320, 440), (380, 440), (440, 440),
            # Click on pet for gold bonus.
            (285, 400),
            # Click on spot where skill points appear.
            (110, 445),
            # Click on spot where equipment appears.
            (355, 445),
        ),
        "clan_crate": (70, 165),
    },
    "PANELS": {
        "expand_collapse_top": (386, 43),
        "expand_collapse_bottom": (386, 478),
        "close_top": (449, 43),
        "close_bottom": (449, 479),
    },
    "TOURNAMENT": {
        "tournament": (30, 105),
        "tournament_prestige": (330, 570),
        "collect_prize": (245, 765),
        "join": (245, 730),
    },
    "EGGS": {
        "hatch_egg": (35, 315),
    },
    "CLAN_BATTLE": {
        "clan": (82, 59),
        "clan_quest": (105, 755),
        "clan_fight": (310, 765),
        "diamond_okay": (330, 475),
        "clan_leave_screen": (460, 410),
        "clan_quest_exit": (415, 75),
    },
    "AD": {
        "collect_ad": (365, 650),
        "no_thanks": (135, 650),
    },
    "ARTIFACTS": {
        "bottom_region": (2, 727, 475, 797),
    },
}

# Points used when clicking on locations present on the master panel.
MASTER_LOCS = {
    "master_level": (415, 170),
    "prestige": (405, 770),
    "prestige_confirm": (245, 660),
    "prestige_final": (330, 570),
    "screen_top": (240, 40),
    "skills": {
        "heavenly_strike": (415, 270),
        "deadly_strike": (415, 350),
        "hand_of_midas": (415, 430),
        "fire_sword": (415, 508),
        "war_cry": (415, 580),
        "shadow_clone": (415, 650),
    },
    "skill_level_max": {
        "heavenly_strike": (268, 280),
        "deadly_strike": (268, 357),
        "hand_of_midas": (268, 433),
        "fire_sword": (268, 508),
        "war_cry": (268, 584),
        "shadow_clone": (268, 659),
    },
}

# Points used when clicking on locations present in the heroes panel.
HEROES_LOCS = {
    "drag_heroes": {
        "start": (328, 85),
        # End is quite finicky, be sure to experiment with the y
        # value if using different resolutions.
        "end": (328, 920),
    },
    "level_heroes": (
        (405, 770),
        (405, 690),
        (405, 615),
        (405, 540),
        (405, 465),
        (405, 390),
        (405, 310),
        (405, 240),
        (405, 160),
        (405, 85),
    ),
    "stats_collapsed": (135, 540),
    "stats_expanded": (135, 105),
}

ARTIFACTS_LOCS = {
    # The amount of pixels to push the mouse over when purchasing any artifact. Since the imagesearch
    # will return the top left of the image, we can add these vales to that to click on the purchase button.
    "artifact_push": {
        "x": 401,
        "y": 40,
    },
    "buy_multiplier": (410, 105),
    "buy_max": (50, 105),
}

# Store any colors used (RGB) by the bot to determine so things in game.
GAME_COLORS = {
    "WHITE": (255, 255, 255)
}

# All images should have their names mapped to the file path within the module.
IMAGES = {
    "ADS": {
        "collect_ad": IMAGE_DIR + "/ads/collect.png",
        "no_thanks": IMAGE_DIR + "/ads/no_thanks.png",
    },
    "ARTIFACTS": {
        "artifacts_discovered": IMAGE_DIR + "/artifacts/artifacts_discovered.png",
        "book_of_shadows": IMAGE_DIR + "/artifacts/book_of_shadows.png",
        "spend_max": IMAGE_DIR + "/artifacts/spend_max.png",
    },
    "CLAN_BATTLE": {
        "diamond": IMAGE_DIR + "/clan_battle/diamond.png",
        "goal_complete": IMAGE_DIR + "/clan_battle/goal_complete.png",
        "deal_110_next_attack": IMAGE_DIR + "/clan_battle/deal_110_next_attack.png",
        "fight": IMAGE_DIR + "/clan_battle/fight.png",
    },
    "DAILY_REWARD": {
        "collect_reward": IMAGE_DIR + "/daily_reward/collect.png",
    },
    "EQUIPMENT": {
        "crafting": IMAGE_DIR + "/equipment/crafting.png",
    },
    "GENERIC": {
        "artifacts_active": IMAGE_DIR + "/generic/artifacts_active.png",
        "buy_max": IMAGE_DIR + "/generic/buy_max.png",
        "buy_one": IMAGE_DIR + "/generic/buy_one.png",
        "buy_one_hundred": IMAGE_DIR + "/generic/buy_one_hundred.png",
        "buy_ten": IMAGE_DIR + "/generic/buy_ten.png",
        "collapse_panel": IMAGE_DIR + "/generic/collapse_panel.png",
        "equipment_active": IMAGE_DIR + "/generic/equipment_active.png",
        "exit_panel": IMAGE_DIR + "/generic/exit_panel.png",
        "expand_panel": IMAGE_DIR + "/generic/expand_panel.png",
        "heroes_active": IMAGE_DIR + "/generic/heroes_active.png",
        "large_exit_panel": IMAGE_DIR + "/generic/large_exit_panel.png",
        "master_active": IMAGE_DIR + "/generic/master_active.png",
        "max": IMAGE_DIR + "/generic/max.png",
        "pets_active": IMAGE_DIR + "/generic/pets_active.png",
        "shop_active": IMAGE_DIR + "/generic/shop_active.png",
    },
    "HEROES": {
        "max_level": IMAGE_DIR + "/heroes/max_level.png",
        "maya_muerta": IMAGE_DIR + "/heroes/maya_muerta.png",
        "stats": IMAGE_DIR + "/heroes/stats.png",
        "story": IMAGE_DIR + "/heroes/story.png",
        "upgrades": IMAGE_DIR + "/heroes/upgrades.png",
    },
    "MASTER": {
        "account": IMAGE_DIR + "/master/account.png",
        "achievements": IMAGE_DIR + "/master/achievements.png",
        "cancel_active_skill": IMAGE_DIR + "/master/cancel_active_skill.png",
        "confirm_prestige": IMAGE_DIR + "/master/confirm_prestige.png",
        "deadly_strike": IMAGE_DIR + "/master/deadly_strike.png",
        "fire_sword": IMAGE_DIR + "/master/fire_sword.png",
        "hand_of_midas": IMAGE_DIR + "/master/hand_of_midas.png",
        "heavenly_strike": IMAGE_DIR + "/master/heavenly_strike.png",
        "inbox": IMAGE_DIR + "/master/inbox.png",
        "master": IMAGE_DIR + "/master/master.png",
        "prestige": IMAGE_DIR + "/master/prestige.png",
        "shadow_clone": IMAGE_DIR + "/master/shadow_clone.png",
        "skill_level_zero": IMAGE_DIR + "/master/skill_level_zero.png",
        "skill_max_level": IMAGE_DIR + "/master/skill_max_level.png",
        "skill_tree": IMAGE_DIR + "/master/skill_tree.png",
        "unlock_at": IMAGE_DIR + "/master/unlock_at.png",
        "war_cry": IMAGE_DIR + "/master/war_cry.png",
    },
    "NO_PANELS": {
        "clan_battle_ready": IMAGE_DIR + "/no_panels/clan_battle_ready.png",
        "clan_no_battle": IMAGE_DIR + "/no_panels/clan_no_battle.png",
        "daily_reward": IMAGE_DIR + "/no_panels/daily_reward.png",
        "fight_boss": IMAGE_DIR + "/no_panels/fight_boss.png",
        "hatch_egg": IMAGE_DIR + "/no_panels/hatch_egg.png",
        "leave_boss": IMAGE_DIR + "/no_panels/leave_boss.png",
        "settings": IMAGE_DIR + "/no_panels/clan_battle_ready.png",
        "tournament": IMAGE_DIR + "/no_panels/tournament.png",
    },
    "PETS": {
        "next_egg": IMAGE_DIR + "/pets/next_egg.png",
    },
    "SHOP": {
        "shop_keeper": IMAGE_DIR + "/shop/shop_keeper.png",
    },
    "TOURNAMENT": {
        "join": IMAGE_DIR + "/tournament/join.png",
        "collect_prize": IMAGE_DIR + "/tournament/collect_prize.png",
    },
    "CLAN_CRATE": {
        "okay": IMAGE_DIR + "/clan_crate/okay.png",
    },
}

# All coordinates mapped to their respective resolutions for grabbing
# each stat image that will be parsed by pytesseract.
STATS_COORDS = {
    "highest_stage_reached": (55, 474, 430, 495),
    "total_pet_level": (55, 495, 430, 515),
    "gold_earned": (55, 516, 430, 536),
    "taps": (55, 537, 430, 561),
    "titans_killed": (55, 559, 430, 579),
    "bosses_killed": (55, 580, 430, 600),
    "critical_hits": (55, 602, 430, 621),
    "chestersons_killed": (55, 623, 430, 643),
    "prestiges": (55, 645, 430, 666),
    "play_time": (55, 687, 430, 708),
    "relics_earned": (55, 709, 430, 729),
    "fairies_tapped": (55, 731, 430, 751),
    "daily_achievements": (55, 750, 430, 773),
}

STAGE_COORDS = {
    "region": (214, 71, 268, 84),
}

CLAN_COORDS = {
    "play_again": (70, 768, 172, 787),
}

# The regions for each skill present on the master screen if the panel
# is expanded and scrolled all the way to the top.
MASTER_COORDS = {
    "skills": {
        "heavenly_strike": (0, 233, 480, 303),
        "deadly_strike": (0, 309, 480, 380),
        "hand_of_midas": (0, 385, 480, 455),
        "fire_sword": (0, 460, 480, 531),
        "war_cry": (0, 536, 480, 607),
        "shadow_clone": (0, 612, 480, 682),
    },
}

# Set of skills in game.
SKILLS = (
    "heavenly_strike",
    "deadly_strike",
    "hand_of_midas",
    "fire_sword",
    "war_cry",
    "shadow_clone",
)

# Dictionary containing all of the artifacts in game mapped to their respective tier list.
ARTIFACT_TIER_MAP = {
    "S": {
        "book_of_shadows": IMAGE_DIR + "/artifacts/book_of_shadows.png",
        "stone_of_the_valrunes": IMAGE_DIR + "/artifacts/stone_of_the_valrunes.png",
        "flute_of_the_soloist": IMAGE_DIR + "/artifacts/flute_of_the_soloist.png",
        "heart_of_storms": IMAGE_DIR + "/artifacts/heart_of_storms.png",
        "ring_of_calisto": IMAGE_DIR + "/artifacts/ring_of_calisto.png",
        "invaders_gjalarhorn": IMAGE_DIR + "/artifacts/invaders_gjalarhorn.png",
        "boots_of_hermes": IMAGE_DIR + "/artifacts/boots_of_hermes.png",
    },
    "A": {
        "book_of_prophecy": IMAGE_DIR + "/artifacts/book_of_prophecy.png",
        "khrysos_bowl": IMAGE_DIR + "/artifacts/khrysos_bowl.png",
        "the_bronzed_compass": IMAGE_DIR + "/artifacts/the_bronzed_compass.png",
        "heavenly_sword": IMAGE_DIR + "/artifacts/heavenly_sword.png",
        "divine_retribution": IMAGE_DIR + "/artifacts/divine_retribution.png",
        "drunken_hammer": IMAGE_DIR + "/artifacts/drunken_hammer.png",
        "samosek_sword": IMAGE_DIR + "/artifacts/samosek_sword.png",
        "the_retaliator": IMAGE_DIR + "/artifacts/the_retaliator.png",
        "stryfe's_peace": IMAGE_DIR + "/artifacts/stryfes_peace.png",
        "hero's_blade": IMAGE_DIR + "/artifacts/heros_blade.png",
        "the_sword_of_storms": IMAGE_DIR + "/artifacts/the_sword_of_storms.png",
        "furies_bow": IMAGE_DIR + "/artifacts/furies_bow.png",
        "charm_of_the_ancient": IMAGE_DIR + "/artifacts/charm_of_the_ancient.png",
        "tiny_titan_tree": IMAGE_DIR + "/artifacts/tiny_titan_tree.png",
        "helm_of_hermes": IMAGE_DIR + "/artifacts/helm_of_hermes.png",
        "o'ryans_charm": IMAGE_DIR + "/artifacts/oryans_charm.png",
        "apollo_orb": IMAGE_DIR + "/artifacts/apollo_orb.png",
        "earrings_of_portara": IMAGE_DIR + "/artifacts/earrings_of_portara.png",
        "helheim_skull": IMAGE_DIR + "/artifacts/helheim_skull.png",
        "oath's_burden": IMAGE_DIR + "/artifacts/oaths_burden.png",
        "crown_of_the_constellation": IMAGE_DIR + "/artifacts/crown_of_the_constellation.png",
        "titania's_sceptre": IMAGE_DIR + "/artifacts/titanias_sceptre.png",
        "fagin's_grip": IMAGE_DIR + "/artifacts/fagins_grip.png",
        "blade_of_damocles": IMAGE_DIR + "/artifacts/blade_of_damocles.png",
        "helmet_of_madness": IMAGE_DIR + "/artifacts/helmet_of_madness.png",
        "titanium_plating": IMAGE_DIR + "/artifacts/titanium_plating.png",
        "moonlight_bracelet": IMAGE_DIR + "/artifacts/moonlight_bracelet.png",
        "amethyst_staff": IMAGE_DIR + "/artifacts/amethyst_staff.png",
        "spearit's_vigil": IMAGE_DIR + "/artifacts/spearits_vigil.png",
        "sword_of_the_royals": IMAGE_DIR + "/artifacts/sword_of_the_royals.png",
        "the_cobalt_plate": IMAGE_DIR + "/artifacts/the_cobalt_plate.png",
        "sigils_of_judgement": IMAGE_DIR + "/artifacts/sigils_of_judgement.png",
        "foilage_of_the_keeper": IMAGE_DIR + "/artifacts/foilage_of_the_keeper.png",
        "royal_toxin": IMAGE_DIR + "/artifacts/royal_toxin.png",
        "laborer's_pendant": IMAGE_DIR + "/artifacts/laborers_pendant.png",
        "bringer_of_ragnarok": IMAGE_DIR + "/artifacts/bringer_of_ragnarok.png",
        "parchment_of_foresight": IMAGE_DIR + "/artifacts/parchment_of_foresight.png",
        "unbound_gauntlet": IMAGE_DIR + "/artifacts/unbound_gauntlet.png",
        "lucky_foot_of_al-mi-raj": IMAGE_DIR + "/artifacts/lucky_foot_of_al-mi-raj.png",
        "morgelai_sword": IMAGE_DIR + "/artifacts/morgelai_sword.png",
        "the_magnifier": IMAGE_DIR + "/artifacts/the_magnifier.png",
        "the_treasure_of_fergus": IMAGE_DIR + "/artifacts/the_treasure_of_fergus.png",
        "the_white_dwarf": IMAGE_DIR + "/artifacts/the_white_dwarf.png",
    },
    "B": {
        "chest_of_contentment": IMAGE_DIR + "/artifacts/chest_of_contentment.png",
        "heroic_shield": IMAGE_DIR + "/artifacts/heroic_shield.png",
        "zakynthos_coin": IMAGE_DIR + "/artifacts/zakynthos_coin.png",
        "great_fay_medallion": IMAGE_DIR + "/artifacts/great_fay_medallion.png",
        "neko_sculpture": IMAGE_DIR + "/artifacts/neko_sculpture.png",
        "coins_of_ebizu": IMAGE_DIR + "/artifacts/coins_of_ebizu.png",
        "fruit_of_eden": IMAGE_DIR + "/artifacts/fruit_of_eden.png",
        "influential_elixir": IMAGE_DIR + "/artifacts/influential_elixir.png",
        "avian_feather": IMAGE_DIR + "/artifacts/avian_feather.png",
        "titan's_mask": IMAGE_DIR + "/artifacts/titans_mask.png",
        "elixir_of_eden": IMAGE_DIR + "/artifacts/elixir_of_eden.png",
        "hourglass_of_the_impatient": IMAGE_DIR + "/artifacts/hourglass_of_the_impatient.png",
        "phantom_timepiece": IMAGE_DIR + "/artifacts/phantom_timepiece.png",
        "infinity_pendulum": IMAGE_DIR + "/artifacts/infinity_pendulum.png",
        "glove_of_kuma": IMAGE_DIR + "/artifacts/glove_of_kuma.png",
        "titan_spear": IMAGE_DIR + "/artifacts/titan_spear.png",
        "oak_staff": IMAGE_DIR + "/artifacts/oak_staff.png",
        "the_arcana_cloak": IMAGE_DIR + "/artifacts/the_arcana_cloak.png",
        "hunter's_ointment": IMAGE_DIR + "/artifacts/hunters_ointment.png",
        "axe_of_muerte": IMAGE_DIR + "/artifacts/axe_of_muerte.png",
        "the_master's_sword": IMAGE_DIR + "/artifacts/the_masters_sword.png",
        "mystical_beans_of_senzu": IMAGE_DIR + "/artifacts/mystical_beans_of_senzu.png",
    },
    "C": {
        "corrupted_rune_heart": IMAGE_DIR + "/artifacts/corrupted_rune_heart.png",
        "durendal_sword": IMAGE_DIR + "/artifacts/durendal_sword.png",
        "forbidden_scroll": IMAGE_DIR + "/artifacts/forbidden_scroll.png",
        "ring_of_fealty": IMAGE_DIR + "/artifacts/ring_of_fealty.png",
        "glacial_axe": IMAGE_DIR + "/artifacts/glacial_axe.png",
        "aegis": IMAGE_DIR + "/artifacts/aegis.png",
        "swamp_gauntlet": IMAGE_DIR + "/artifacts/swamp_gauntlet.png",
        "ambrosia_elixir": IMAGE_DIR + "/artifacts/ambrosia_elixir.png",
        "mystic_staff": IMAGE_DIR + "/artifacts/mystic_staff.png",
        "egg_of_fortune": IMAGE_DIR + "/artifacts/egg_of_fortune.png",
        "divine_chalice": IMAGE_DIR + "/artifacts/divine_chalice.png",
        "invader's_shield": IMAGE_DIR + "/artifacts/invaders_shield.png",
        "essence_of_kitsune": IMAGE_DIR + "/artifacts/essence_of_kitsune.png",
        "oberon_pendant": IMAGE_DIR + "/artifacts/oberon_pendant.png",
        "lost_king's_mask": IMAGE_DIR + "/artifacts/lost_kings_mask.png",
        "staff_of_radiance": IMAGE_DIR + "/artifacts/staff_of_radiance.png",
        "aram_spear": IMAGE_DIR + "/artifacts/aram_spear.png",
        "ward_of_the_darkness": IMAGE_DIR + "/artifacts/ward_of_the_darkness.png",
    },
}

# Dictionary containing all artifacts in game mapped to their respective image path. No tiers included.
ARTIFACT_MAP = {k1: v1 for k, v in ARTIFACT_TIER_MAP.items() for k1, v1 in v.items()}

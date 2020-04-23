from settings import IMAGE_DIR

# All points in game that are relevant to the expected resolution can be stored here.
GAME_LOCS = {
    "BOTTOM_BAR": {
        "master": (39, 781),
        "heroes": (120, 781),
        "equipment": (200, 781),
        "pets": (281, 781),
        "artifacts": (362, 781),
        "shop": (442, 781),
    },
    "DAILY_REWARD": {
        "open_rewards": (34, 176),
        "close_rewards": (430, 226),
        "collect_rewards": (240, 526),
    },
    "INBOX": {
        "inbox": (31, 361),
        "inbox_news": (142, 106),
        "inbox_clan": (343, 106),
    },
    "CLAN": {
        "clan": (82, 25),
        "clan_info": (194, 728),
        "clan_info_header": (351, 82),
        "clan_info_close": (431, 34),
        "clan_previous_raid": (373, 298),
        "clan_results_copy": (83, 226),
        "clan_raid": (109, 716),
    },
    "SKILL_BAR": {
        "heavenly_strike": (43, 710),
        "deadly_strike": (123, 710),
        "hand_of_midas": (200, 710),
        "fire_sword": (283, 710),
        "war_cry": (363, 710),
        "shadow_clone": (444, 710),
    },
    "GAME_SCREEN": {
        "fight_boss": (425, 31),
        "game_middle": (250, 286),
        "player": (235, 387),
        "pet_gold": (287, 377),
        "pet_attack": (235, 343),
        "clan_ship": (60, 154),
        # Start any scroll functions from this point.
        "scroll_start": (328, 496),
        "scroll_top_end": (328, 731),
        "scroll_bottom_end": (328, 46),
        "scroll_quick_stop": (328, 746),
        # The fairies map is looped through and each point is pressed
        # sequentially, this will ensure that fairies are pressed if present.
        "fairies_map": (
            (75, 91), (100, 91), (140, 91), (200, 91), (260, 91), (320, 91), (380, 91), (440, 91),
            (75, 126), (100, 126), (140, 126), (200, 126), (260, 126), (320, 126), (380, 126), (440, 126),
            (75, 196), (100, 196), (140, 196), (200, 196), (260, 196), (320, 196), (380, 196), (440, 196),
            # Click on pet for gold bonus.
            (285, 366),
            # Click on spot where skill points appear.
            (110, 411),
            # Click on spot where equipment appears.
            (355, 411),
        ),
        "collect_clan_crate": (70, 131),
    },
    "MINIGAMES": {
        "coordinated_offensive": (
            (176, 411),
        ),
        "astral_awakening": (
            # Bottom Layer.
            (110, 390), (55, 390), (23, 390), (360, 390), (400, 390), (440, 390),
            # Middle Layer.
            (35, 290), (75, 290), (400, 290), (440, 290),
            (30, 215), (70, 215), (410, 215), (450, 215),
            (370, 170), (440, 170), (410, 110), (440, 110),
            (470, 110), (460, 90)
        ),
        "heart_of_midas": (
            (299, 388), 
        ),
        "flash_zip": (
            (172, 344), (141, 288), (112, 214), (124, 158), (233, 141), (305, 144), (369, 162), (381, 230), (336, 351),
            (333, 293), (283, 371), (213, 367), (155, 291), (159, 179), (254, 145), (327, 206), (320, 286), (273, 342),
            (216, 313), (224, 219), (172, 344), (141, 288), (112, 214), (124, 158), (233, 141), (305, 144), (369, 162),
            (381, 230), (336, 351), (333, 293), (283, 371), (213, 367), (155, 291), (159, 179), (254, 145), (327, 206),
            (320, 286), (273, 342), (216, 313), (224, 219)
        ),
        "forbidden_contract": (
            (205, 394), (172, 374), (156, 359), (143, 350), (114, 326), (105, 302), (105, 287), (116, 207), (118, 203),
            (125, 198), (144, 194), (166, 187), (199, 162), (234, 161), (275, 165), (308, 169), (321, 184), (198, 394),
            (165, 374), (152, 359), (139, 350), (110, 326), (100, 302), (101, 287), (111, 207), (114, 203), (119, 198),
            (139, 194), (160, 187), (194, 162), (230, 161), (270, 165), (300, 169), (315, 184), (209, 394), (176, 374),
            (162, 359), (150, 350), (119, 326), (111, 302), (108, 287), (120, 207), (125, 203), (127, 198), (149, 194),
            (171, 187), (204, 162), (239, 161), (280, 165), (314, 169), (325, 184),
        ),
        "summon_dagger": (
            (231, 391), (214, 391), (195, 384), (173, 380), (197, 396), (191, 370), (250, 390), (262, 388), (272, 387),
            (284, 383), (298, 380), (276, 395), (286, 379), (231, 391), (214, 391), (195, 384), (173, 380), (197, 396),
            (191, 370), (250, 390), (262, 388), (272, 387), (284, 383), (298, 380), (276, 395), (286, 379), (265, 394),
            (199, 395),
        )
    },
    "PANELS": {
        "expand_collapse_top": (386, 9),
        "expand_collapse_bottom": (386, 444),
        "close_top": (449, 9),
        "close_bottom": (449, 445),
    },
    "TOURNAMENT": {
        "tournament": (30, 78),
        "tournament_prestige": (330, 546),
        "collect_prize": (245, 731),
        "join": (245, 696),
    },
    "EGGS": {
        "hatch_egg": (35, 281),
    },
    "AD": {
        "collect_ad": (365, 616),
        "no_thanks": (135, 616),
    },
    "ARTIFACTS": {
        "discover_point": (407, 604),
        "enchant_point": (410, 608),
        "purchase": (254, 554)
    },
    "PERKS": {
        "perks_okay": (326, 444),
        "perks_cancel": (150, 444),
    },
}

# Points used when clicking on locations present on the master panel.
MASTER_LOCS = {
    "master_level": (415, 136),
    "prestige": (405, 682),
    "prestige_confirm": (245, 675),
    "prestige_final": (330, 536),
    "screen_top": (240, 6),
    "achievements": (207, 503),
    "daily_achievements": (342, 89),
    "milestones": {
        "milestones_header": (245, 85),
        "milestones_collect_point": (382, 259),
    },
    "skills": {
        "heavenly_strike": (415, 348),
        "deadly_strike": (415, 421),
        "hand_of_midas": (415, 498),
        "fire_sword": (415, 574),
        "war_cry": (415, 648),
        "shadow_clone": (415, 723),
    },
    "skill_level_max": {
        "heavenly_strike": (268, 354),
        "deadly_strike": (268, 427),
        "hand_of_midas": (268, 503),
        "fire_sword": (268, 578),
        "war_cry": (268, 657),
        "shadow_clone": (268, 734),
    },
}

# Points used when clicking on locations present in the heroes panel.
HEROES_LOCS = {
    "drag_heroes": {
        "start": (328, 51),
        # End is quite finicky, be sure to experiment with the y
        # value if using different resolutions.
        "end": (328, 610),
    },
    "level_heroes": (
        (405, 736),
        (405, 702),
        (405, 656),
        (405, 623),
        (405, 581),
        (405, 547),
        (405, 506),
        (405, 470),
        (405, 431),
        (405, 394),
        (405, 356),
        (405, 320),
        (405, 276),
        (405, 244),
        (405, 206),
        (405, 167),
        (405, 126),
        (405, 96),
        (405, 51),
    ),
    "stats_collapsed": (135, 506),
    "stats_expanded": (135, 71),
}

EQUIPMENT_LOCS = {
    "equip": (409, 167),
    "tabs": {
        "sword": (41, 86),
        "headgear": (106, 86),
        "cloak": (174, 86),
        "aura": (240, 86),
        "slash": (307, 86),
    },
    "color_checks": {
        "sword": (29, 114),
        "headgear": (94, 114),
        "cloak": (161, 114),
        "aura": (225, 114),
        "slash": (291, 114),
    },
    "drag_equipment": {
        "start": (328, 165),
        "end": (328, 610),
    }
}

ARTIFACTS_LOCS = {
    # The amount of pixels to push the mouse over when purchasing any artifact. Since the imagesearch
    # will return the top left of the image, we can add these vales to that to click on the purchase button.
    "artifact_push": {
        "x": 375,
        "y": 20,
    },
    "buy_multiplier": (410, 71),
    "buy_max": (50, 71),
    "percent_toggle": (303, 70),
}

PERK_LOCS = {
    "perk_push": {
        "x": 396,
        "y": 20,
    },
}

SKILL_CAN_LEVEL_LOCS = {
    "heavenly_strike": (460, 319),
    "deadly_strike": (460, 395),
    "hand_of_midas": (460, 472),
    "fire_sword": (460, 546),
    "war_cry": (460, 623),
    "shadow_clone": (460, 698)
}

# Store any colors used (RGB) by the bot to determine so things in game.
GAME_COLORS = {
    "WHITE": (255, 255, 255),
    "DISCOVER": (60, 184, 174),
    "ENCHANT": (235, 167, 12),
    "COLLECT_GREEN": (101, 155, 28),
    "SKILL_CANT_LEVEL": (73, 72, 73),
    "EQUIPMENT_CHOSEN": (66, 64, 68),
}

# All images should have their names mapped to the file path within the module.
IMAGES = {
    "ACHIEVEMENTS": {
        "achievements_title": IMAGE_DIR + "/achievements/achievements.png",
        "daily_collect": IMAGE_DIR + "/achievements/daily_collect.png",
        "vip_daily_collect": IMAGE_DIR + "/achievements/vip_collect.png",
        "daily_watch": IMAGE_DIR + "/achievements/daily_watch.png",
    },
    "ADS": {
        "collect_ad": IMAGE_DIR + "/ads/collect.png",
        "watch_ad": IMAGE_DIR + "/ads/watch.png",
        "no_thanks": IMAGE_DIR + "/ads/no_thanks.png",
    },
    "ARTIFACTS": {
        "artifacts": IMAGE_DIR + "/artifacts/artifacts.png",
        "artifacts_discovered": IMAGE_DIR + "/artifacts/artifacts_discovered.png",
        "book_of_shadows": IMAGE_DIR + "/artifacts/book_of_shadows.png",
        "spend_max": IMAGE_DIR + "/artifacts/spend_max.png",
        "salvaged": IMAGE_DIR + "/artifacts/salvaged.png",
        "percent_on": IMAGE_DIR + "/artifacts/percent_on.png",
        "discover": IMAGE_DIR + "/artifacts/discover.png",
        "enchant": IMAGE_DIR + "/artifacts/enchant.png",
    },
    "DAILY_REWARD": {
        "daily_rewards_header": IMAGE_DIR + "/daily_reward/daily_rewards_header.png",
        "collect_reward": IMAGE_DIR + "/daily_reward/collect.png",
    },
    "INBOX": {
        "inbox_header": IMAGE_DIR + "/inbox/inbox_header.png",
    },
    "EQUIPMENT": {
        "crafting": IMAGE_DIR + "/equipment/crafting.png",
        "locked": IMAGE_DIR + "/equipment/locked.png",
        "equip": IMAGE_DIR + "/equipment/equip.png",
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
        "masteries": IMAGE_DIR + "/heroes/masteries.png",
        "zero_dps": IMAGE_DIR + "/heroes/zero_dps.png",
        "melee_type": IMAGE_DIR + "/heroes/melee_type.png",
        "spell_type": IMAGE_DIR + "/heroes/spell_type.png",
        "ranged_type": IMAGE_DIR + "/heroes/ranged_type.png",
        "bonus_melee": IMAGE_DIR + "/heroes/bonus_melee.png",
        "bonus_spell": IMAGE_DIR + "/heroes/bonus_spell.png",
        "bonus_ranged": IMAGE_DIR + "/heroes/bonus_ranged.png",
    },
    "MASTER": {
        "raid_cards": IMAGE_DIR + "/master/raid_cards.png",
        "achievements": IMAGE_DIR + "/master/achievements.png",
        "cancel_active_skill": IMAGE_DIR + "/master/cancel_active_skill.png",
        "confirm_prestige": IMAGE_DIR + "/master/confirm_prestige.png",
        "confirm_prestige_final": IMAGE_DIR + "/master/confirm_prestige_final.png",
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
        "intimidating_presence": IMAGE_DIR + "/master/intimidating_presence.png",
        "silent_march": IMAGE_DIR + "/master/silent_march.png",
    },
    "NO_PANELS": {
        "clan_raid_ready": IMAGE_DIR + "/no_panels/clan_raid_ready.png",
        "clan_no_raid": IMAGE_DIR + "/no_panels/clan_no_raid.png",
        "daily_reward": IMAGE_DIR + "/no_panels/daily_reward.png",
        "fight_boss": IMAGE_DIR + "/no_panels/fight_boss.png",
        "hatch_egg": IMAGE_DIR + "/no_panels/hatch_egg.png",
        "leave_boss": IMAGE_DIR + "/no_panels/leave_boss.png",
        "icon_boss": IMAGE_DIR + "/no_panels/icon_boss.png",
        "settings": IMAGE_DIR + "/no_panels/settings.png",
        "tournament": IMAGE_DIR + "/no_panels/tournament.png",
        "pet_damage": IMAGE_DIR + "/no_panels/pet_damage.png",
        "master_damage": IMAGE_DIR + "/no_panels/master_damage.png",

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
    "CLAN": {
        "clan": IMAGE_DIR + "/clan/clan.png",
        "clan_info": IMAGE_DIR + "/clan/clan_info.png",
    },
    "RAID": {
        "raid_fight": IMAGE_DIR + "/raid/raid_fight.png",
    },
    "STATS": {
        "stats_title": IMAGE_DIR + "/stats/stats_title.png",
    },
    "WELCOME": {
        "welcome_header": IMAGE_DIR + "/welcome/welcome_header.png",
        "welcome_collect_no_vip": IMAGE_DIR + "/welcome/welcome_collect_no_vip.png",
        "welcome_collect_vip": IMAGE_DIR + "/welcome/welcome_collect_vip.png",
    },
    "RATE": {
        "rate_icon": IMAGE_DIR + "/rate/rate_icon.png",
    },
    "PERKS": {
        "perks_mega_boost": IMAGE_DIR + "/perks/perks_mega_boost.png",
        "perks_power_of_swiping": IMAGE_DIR + "/perks/perks_power_of_swiping.png",
        "perks_adrenaline_rush": IMAGE_DIR + "/perks/perks_adrenaline_rush.png",
        "perks_make_it_rain": IMAGE_DIR + "/perks/perks_make_it_rain.png",
        "perks_mana_potion": IMAGE_DIR + "/perks/perks_mana_potion.png",
        "perks_doom": IMAGE_DIR + "/perks/perks_doom.png",
        "perks_clan_crate": IMAGE_DIR + "/perks/perks_clan_crate.png",
        "perks_diamond": IMAGE_DIR + "/perks/perks_diamond.png",
        "perks_header": IMAGE_DIR + "/perks/perks_header.png",
        "perk_header": IMAGE_DIR + "/perks/perk_header.png",
        "perks_vip_watch": IMAGE_DIR + "/perks/perks_vip_watch.png",
    }
}

# All coordinates mapped to their respective resolutions for grabbing
# each stat image that will be parsed by pytesseract.
STATS_COORDS = {
    "highest_stage_reached": (55, 440, 430, 461),
    "total_pet_level": (55, 461, 430, 481),
    "gold_earned": (55, 482, 430, 502),
    "taps": (55, 503, 430, 527),
    "titans_killed": (55, 525, 430, 545),
    "bosses_killed": (55, 546, 430, 566),
    "critical_hits": (55, 568, 430, 587),
    "chestersons_killed": (55, 589, 430, 609),
    "prestiges": (55, 611, 430, 632),
    "days_since_install": (55, 636, 430, 652),
    "play_time": (55, 653, 430, 674),
    "relics_earned": (55, 675, 430, 695),
    "fairies_tapped": (55, 697, 430, 717),
    "daily_achievements": (55, 716, 430, 739),
}

STAGE_COORDS = {
    "region": (215, 38, 268, 53),
}

PRESTIGE_COORDS = {
    "base": {
        "time_since": (301, 155, 380, 177),
        "advance_start": (136, 584, 212, 612),
    },
    "event": {
        "time_since": (301, 121, 380, 139),
        "advance_start": (138, 567, 191, 588),
    }
}

PANEL_COORDS = {
    "panel_check": (0, 550, 232, 762)
}

# The regions for each skill present on the master screen if the panel
# is expanded and scrolled all the way to the top.
MASTER_COORDS = {
    "skills": {
        "heavenly_strike": (0, 310, 480, 379),
        "deadly_strike": (0, 385, 480, 455),
        "hand_of_midas": (0, 460, 480, 531),
        "fire_sword": (0, 538, 480, 607),
        "war_cry": (0, 611, 480, 682),
        "shadow_clone": (0, 687, 480, 759),
    },
}

# Regions used to level up skills in game should only take place when our
# skills are not their specified level or maxed.. We use these regions to grab
# the current level through an OCR check.
SKILL_LEVEL_COORDS = {
    "heavenly_strike": (70, 331, 115, 348),
    "deadly_strike": (70, 407, 115, 423),
    "hand_of_midas": (70, 483, 115, 498),
    "fire_sword": (70, 558, 115, 574),
    "war_cry": (70, 634, 115, 650),
    "shadow_clone": (70, 709, 115, 725),
}

CLAN_COORDS = {
    "info_name": (95, 15, 392, 54),
    "info_code": (128, 746, 207, 766),
}

# Clan raid coordinates located in the main clan raid page.
CLAN_RAID_COORDS = {
    "raid_attack_reset": (55, 719, 240, 737),
}

# Artifact coordinates used py any artifact related functionality.
ARTIFACT_COORDS = {
    "parse_region": (0, 57, 72, 763)
}

PERK_COORDS = {
    "purchase": (72, 290, 407, 405),
}

# Hero coordinates used to find the first levelled hero on screen.
HERO_COORDS = {
    "heroes": [
        {
            "dps": (261, 120, 310, 141),
            "type": (300, 119, 322, 140),
        },
        {
            "dps": (260, 194, 308, 217),
            "type": (300, 194, 322, 217),
        },
        {
            "dps": (262, 271, 310, 291),
            "type": (298, 271, 324, 292),
        }
    ]
}

# Equipment coordinates used to find equipment in game and determine if it's
# meant to be equipped or not.
EQUIPMENT_COORDS = {
    "gear": [
        # SLOT 1.
        {
            "base": (0, 134, 472, 200),
            "locked": (40, 173, 73, 198),
            "bonus": (70, 180, 278, 198),
            "equip": (407, 166),
        },
        # SLOT 2.
        {
            "base": (0, 208, 476, 276),
            "locked": (40, 250, 73, 277),
            "bonus": (70, 256, 294, 276),
            "equip": (407, 244),
        },
        # SLOT 3.
        {
            "base": (0, 287, 476, 355),
            "locked": (40, 328, 73, 356),
            "bonus": (70, 335, 294, 353),
            "equip": (407, 322),
        },
        # SLOT 4.
        {
            "base": (0, 365, 476, 431),
            "locked": (40, 405, 73, 432),
            "bonus": (70, 411, 294, 431),
            "equip": (407, 400),
        },
        # SLOT 5.
        {
            "base": (0, 442, 476, 510),
            "locked": (40, 484, 73, 509),
            "bonus": (70, 488, 294, 508),
            "equip": (407, 476)
        },
        # SLOT 6.
        {
            "base": (0, 520, 476, 588),
            "locked": (40, 562, 73, 588),
            "bonus": (70, 567, 294, 587),
            "equip": (407, 554),
        },
        # SLOT 7.
        {
            "base": (0, 597, 476, 665),
            "locked": (40, 640, 73, 665),
            "bonus": (70, 644, 294, 664),
            "equip": (407, 632),
        },
        # SLOT 8.
        {
            "base": (0, 676, 476, 742),
            "locked": (40, 717, 73, 743),
            "bonus": (70, 723, 294, 743),
            "equip": (407, 710),
        },
    ],
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
        "book_of_shadows": (IMAGE_DIR + "/artifacts/book_of_shadows.png", 22),
        "stone_of_the_valrunes": (IMAGE_DIR + "/artifacts/stone_of_the_valrunes.png", 2),
        "flute_of_the_soloist": (IMAGE_DIR + "/artifacts/flute_of_the_soloist.png", 84),
        "heart_of_storms": (IMAGE_DIR + "/artifacts/heart_of_storms.png", 52),
        "ring_of_calisto": (IMAGE_DIR + "/artifacts/ring_of_calisto.png", 40),
        "invaders_gjalarhorn": (IMAGE_DIR + "/artifacts/invaders_gjalarhorn.png", 47),
        "boots_of_hermes": (IMAGE_DIR + "/artifacts/boots_of_hermes.png", 70),
    },
    "A": {
        "charged_card": (IMAGE_DIR + "/artifacts/charged_card.png", 95),
        "book_of_prophecy": (IMAGE_DIR + "/artifacts/book_of_prophecy.png", 20),
        "khrysos_bowl": (IMAGE_DIR + "/artifacts/khrysos_bowl.png", 66),
        "the_bronzed_compass": (IMAGE_DIR + "/artifacts/the_bronzed_compass.png", 82),
        "evergrowing_stack": (IMAGE_DIR + "/artifacts/evergrowing_stack.png", 94),
        "heavenly_sword": (IMAGE_DIR + "/artifacts/heavenly_sword.png", 26),
        "divine_retribution": (IMAGE_DIR + "/artifacts/divine_retribution.png", 31),
        "drunken_hammer": (IMAGE_DIR + "/artifacts/drunken_hammer.png", 29),
        "samosek_sword": (IMAGE_DIR + "/artifacts/samosek_sword.png", 51),
        "the_retaliator": (IMAGE_DIR + "/artifacts/the_retaliator.png", 59),
        "stryfe's_peace": (IMAGE_DIR + "/artifacts/stryfes_peace.png", 83),
        "hero's_blade": (IMAGE_DIR + "/artifacts/heros_blade.png", 35),
        "the_sword_of_storms": (IMAGE_DIR + "/artifacts/the_sword_of_storms.png", 32),
        "furies_bow": (IMAGE_DIR + "/artifacts/furies_bow.png", 33),
        "charm_of_the_ancient": (IMAGE_DIR + "/artifacts/charm_of_the_ancient.png", 34),
        "tiny_titan_tree": (IMAGE_DIR + "/artifacts/tiny_titan_tree.png", 61),
        "helm_of_hermes": (IMAGE_DIR + "/artifacts/helm_of_hermes.png", 62),
        "o'ryans_charm": (IMAGE_DIR + "/artifacts/oryans_charm.png", 64),
        "apollo_orb": (IMAGE_DIR + "/artifacts/apollo_orb.png", 53),
        "earrings_of_portara": (IMAGE_DIR + "/artifacts/earrings_of_portara.png", 67),
        "helheim_skull": (IMAGE_DIR + "/artifacts/helheim_skull.png", 56),
        "oath's_burden": (IMAGE_DIR + "/artifacts/oaths_burden.png", 75),
        "crown_of_the_constellation": (IMAGE_DIR + "/artifacts/crown_of_the_constellation.png", 76),
        "titania's_sceptre": (IMAGE_DIR + "/artifacts/titanias_sceptre.png", 77),
        "blade_of_damocles": (IMAGE_DIR + "/artifacts/blade_of_damocles.png", 25),
        "helmet_of_madness": (IMAGE_DIR + "/artifacts/helmet_of_madness.png", 17),
        "titanium_plating": (IMAGE_DIR + "/artifacts/titanium_plating.png", 23),
        "moonlight_bracelet": (IMAGE_DIR + "/artifacts/moonlight_bracelet.png", 73),
        "amethyst_staff": (IMAGE_DIR + "/artifacts/amethyst_staff.png", 28),
        "spearit's_vigil": (IMAGE_DIR + "/artifacts/spearits_vigil.png", 87),
        "sword_of_the_royals": (IMAGE_DIR + "/artifacts/sword_of_the_royals.png", 86),
        "the_cobalt_plate": (IMAGE_DIR + "/artifacts/the_cobalt_plate.png", 88),
        "sigils_of_judgement": (IMAGE_DIR + "/artifacts/sigils_of_judgement.png", 89),
        "foilage_of_the_keeper": (IMAGE_DIR + "/artifacts/foilage_of_the_keeper.png", 90),
        "laborer's_pendant": (IMAGE_DIR + "/artifacts/laborers_pendant.png", 9),
        "bringer_of_ragnarok": (IMAGE_DIR + "/artifacts/bringer_of_ragnarok.png", 10),
        "parchment_of_foresight": (IMAGE_DIR + "/artifacts/parchment_of_foresight.png", 7),
        "unbound_gauntlet": (IMAGE_DIR + "/artifacts/unbound_gauntlet.png", 74),
        "lucky_foot_of_al-mi-raj": (IMAGE_DIR + "/artifacts/lucky_foot_of_al-mi-raj.png", 69),
        "morgelai_sword": (IMAGE_DIR + "/artifacts/morgelai_sword.png", 71),
        "ringing_stone": (IMAGE_DIR + "/artifacts/ringing_stone.png", 91),
        "quill_of_scrolls": (IMAGE_DIR + "/artifacts/quill_of_scrolls.png", 92),
        "old_king's_stamp": (IMAGE_DIR + "/artifacts/old_kings_stamp.png", 93),
        "the_magnifier": (IMAGE_DIR + "/artifacts/the_magnifier.png", 80),
        "the_treasure_of_fergus": (IMAGE_DIR + "/artifacts/the_treasure_of_fergus.png", 81),
        "the_white_dwarf": (IMAGE_DIR + "/artifacts/the_white_dwarf.png", 85),
        "strange_fruit": (IMAGE_DIR + "/artifacts/strange_fruit.png", 96),
        "hades_orb": (IMAGE_DIR + "/artifacts/hades_orb.png", 97),
    },
    "B": {
        "chest_of_contentment": (IMAGE_DIR + "/artifacts/chest_of_contentment.png", 19),
        "heroic_shield": (IMAGE_DIR + "/artifacts/heroic_shield.png", 1),
        "zakynthos_coin": (IMAGE_DIR + "/artifacts/zakynthos_coin.png", 43),
        "great_fay_medallion": (IMAGE_DIR + "/artifacts/great_fay_medallion.png", 44),
        "neko_sculpture": (IMAGE_DIR + "/artifacts/neko_sculpture.png", 45),
        "coins_of_ebizu": (IMAGE_DIR + "/artifacts/coins_of_ebizu.png", 79),
        "fruit_of_eden": (IMAGE_DIR + "/artifacts/fruit_of_eden.png", 38),
        "influential_elixir": (IMAGE_DIR + "/artifacts/influential_elixir.png", 30),
        "avian_feather": (IMAGE_DIR + "/artifacts/avian_feather.png", 42),
        "fagin's_grip": (IMAGE_DIR + "/artifacts/fagins_grip.png", 78),
        "titan's_mask": (IMAGE_DIR + "/artifacts/titans_mask.png", 11),
        "royal_toxin": (IMAGE_DIR + "/artifacts/royal_toxin.png", 41),
        "elixir_of_eden": (IMAGE_DIR + "/artifacts/elixir_of_eden.png", 6),
        "hourglass_of_the_impatient": (IMAGE_DIR + "/artifacts/hourglass_of_the_impatient.png", 65),
        "phantom_timepiece": (IMAGE_DIR + "/artifacts/phantom_timepiece.png", 48),
        "infinity_pendulum": (IMAGE_DIR + "/artifacts/infinity_pendulum.png", 36),
        "glove_of_kuma": (IMAGE_DIR + "/artifacts/glove_of_kuma.png", 27),
        "titan_spear": (IMAGE_DIR + "/artifacts/titan_spear.png", 39),
        "oak_staff": (IMAGE_DIR + "/artifacts/oak_staff.png", 37),
        "the_arcana_cloak": (IMAGE_DIR + "/artifacts/the_arcana_cloak.png", 3),
        "hunter's_ointment": (IMAGE_DIR + "/artifacts/hunters_ointment.png", 8),
        "axe_of_muerte": (IMAGE_DIR + "/artifacts/axe_of_muerte.png", 4),
        "the_master's_sword": (IMAGE_DIR + "/artifacts/the_masters_sword.png", 49),
        "mystical_beans_of_senzu": (IMAGE_DIR + "/artifacts/mystical_beans_of_senzu.png", 68),
    },
    "C": {
        "corrupted_rune_heart": (IMAGE_DIR + "/artifacts/corrupted_rune_heart.png", 46),
        "durendal_sword": (IMAGE_DIR + "/artifacts/durendal_sword.png", 55),
        "forbidden_scroll": (IMAGE_DIR + "/artifacts/forbidden_scroll.png", 13),
        "ring_of_fealty": (IMAGE_DIR + "/artifacts/ring_of_fealty.png", 15),
        "glacial_axe": (IMAGE_DIR + "/artifacts/glacial_axe.png", 16),
        "aegis": (IMAGE_DIR + "/artifacts/aegis.png", 14),
        "swamp_gauntlet": (IMAGE_DIR + "/artifacts/swamp_gauntlet.png", 12),
        "ambrosia_elixir": (IMAGE_DIR + "/artifacts/ambrosia_elixir.png", 50),
        "mystic_staff": (IMAGE_DIR + "/artifacts/mystic_staff.png", 58),
        "egg_of_fortune": (IMAGE_DIR + "/artifacts/egg_of_fortune.png", 18),
        "divine_chalice": (IMAGE_DIR + "/artifacts/divine_chalice.png", 21),
        "invader's_shield": (IMAGE_DIR + "/artifacts/invaders_shield.png", 5),
        "essence_of_kitsune": (IMAGE_DIR + "/artifacts/essence_of_kitsune.png", 54),
        "oberon_pendant": (IMAGE_DIR + "/artifacts/oberon_pendant.png", 72),
        "lost_king's_mask": (IMAGE_DIR + "/artifacts/lost_kings_mask.png", 63),
        "staff_of_radiance": (IMAGE_DIR + "/artifacts/staff_of_radiance.png", 24),
        "aram_spear": (IMAGE_DIR + "/artifacts/aram_spear.png", 57),
        "ward_of_the_darkness": (IMAGE_DIR + "/artifacts/ward_of_the_darkness.png", 60),
    },
}

# Dictionary containing all artifacts in game mapped to their respective image path. No tiers included.
ARTIFACT_MAP = {k1: v1[0] for k, v in ARTIFACT_TIER_MAP.items() for k1, v1 in v.items()}

# Create a set of artifact keys that have a max level (these shouldn't be upgraded). Assuming that
# they are maxed at all times.
ARTIFACT_WITH_MAX_LEVEL = (
    "hourglass_of_the_impatient", "phantom_timepiece", "forbidden_scroll", "ring_of_fealty",
    "glacial_axe", "aegis", "swamp_gauntlet", "infinity_pendulum", "glove_of_kuma", "titan_spear",
    "oak_staff", "the_arcana_cloak", "hunter's_ointment", "ambrosia_elixir", "mystic_staff",
    "mystical_beans_of_senzu", "egg_of_fortune", "divine_chalice", "invader's_shield", "axe_of_muerte",
    "essence_of_the_kitsune", "boots_of_hermes", "unbound_gauntlet", "oberon_pendant",
    "lucky_foot_of_al-mi-raj", "lost_king's_mask", "staff_of_radiance", "morgelai_sword", "ringing_stone",
    "quill_of_scrolls", "old_king's_stamp", "the_master's_sword", "the_magnifier", "the_treasure_of_fergus",
    "the_white_dwarf", "aram_spear", "ward_of_the_darkness",
)

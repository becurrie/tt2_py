"""
maps.py

Map any values into a single location useful for determining locations on screen
and mapping the proper values and coordinates to their respective keys.
"""
from settings import IMAGE_DIR

# All points in game that are relevant to the given resolution can be stored here.
# Not all locations need to be stored here, only locations that otherwise would be
# more of an issue trying to click on after looking for a different image.
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
            (75, 266), (100, 266), (140, 266), (200, 266), (260, 266), (320, 266), (380, 266), (440, 266),
            (75, 336), (100, 336), (140, 336), (200, 336), (260, 336), (320, 336), (380, 336), (440, 336),
            (75, 406), (100, 406), (140, 406), (200, 406), (260, 406), (320, 406), (380, 406), (406, 406),
            # Click on pet for gold bonus.
            (285, 366),
            # Click on spot where skill points appear.
            (110, 411),
            # Click on spot where equipment appears.
            (355, 411),
        ),
        "clan_crate": (70, 131),
    },
    "MINIGAMES": {
        "coordinated_offensive": (
            (139, 403), (154, 403), (160, 405), (150, 404), (162, 404), (143, 402), (162, 401), (148, 409), (159, 401),
            (166, 406), (155, 389), (179, 411), (157, 404), (162, 400), (162, 403), (167, 407), (156, 404), (160, 404),
            (161, 404), (139, 403), (154, 403), (160, 405), (150, 404), (162, 404), (143, 402), (162, 401), (148, 409),
            (159, 401), (166, 406), (155, 389), (179, 411), (157, 404), (162, 400), (162, 403), (167, 407), (156, 404),
            (160, 404), (161, 404)
        ),
        "astral_awakening": (
            (449, 159), (20, 165), (413, 171), (69, 173), (13, 212), (67, 211), (403, 215), (458, 215), (455, 257),
            (395, 256), (74, 260), (10, 258), (11, 302), (65, 300), (405, 292), (454, 292), (451, 328), (396, 331),
            (98, 333), (12, 334), (12, 366), (63, 364), (374, 349), (453, 344), (452, 377), (393, 381), (109, 394),
            (29, 392), (14, 408), (63, 424), (399, 408), (445, 406), (450, 343), (408, 344), (98, 362), (18, 361),
            (9, 314), (66, 301), (387, 298), (440, 299), (472, 296), (463, 243), (412, 243), (381, 249), (124, 265),
            (44, 264), (16, 258), (24, 214), (67, 202), (381, 210), (449, 208), (466, 201), (439, 164), (396, 164),
            (130, 167), (54, 171), (9, 171), (449, 159), (20, 165), (413, 171), (69, 173), (13, 212), (67, 211),
            (403, 215), (458, 215), (455, 257), (395, 256), (74, 260), (10, 258), (11, 302), (65, 300), (405, 292),
            (454, 292), (451, 328), (396, 331), (98, 333), (12, 334), (12, 366), (63, 364), (374, 349), (453, 344),
            (452, 377), (393, 381), (109, 394), (29, 392), (14, 408), (63, 424), (399, 408), (445, 406), (450, 343),
            (408, 344), (98, 362), (18, 361), (9, 314), (66, 301), (387, 298), (440, 299), (472, 296), (463, 243),
            (412, 243), (381, 249), (124, 265), (44, 264), (16, 258), (24, 214), (67, 202), (381, 210), (449, 208),
            (466, 201), (439, 164), (396, 164), (130, 167), (54, 171), (9, 171)
        ),
        "heart_of_midas": (
            (299, 388), (291, 384), (293, 402), (299, 388), (291, 384), (293, 402),
        ),
        "flash_zip": (
            (172, 344), (141, 288), (112, 214), (124, 158), (233, 141), (305, 144), (369, 162), (381, 230), (336, 351),
            (333, 293), (283, 371), (213, 367), (155, 291), (159, 179), (254, 145), (327, 206), (320, 286), (273, 342),
            (216, 313), (224, 219), (172, 344), (141, 288), (112, 214), (124, 158), (233, 141), (305, 144), (369, 162),
            (381, 230), (336, 351), (333, 293), (283, 371), (213, 367), (155, 291), (159, 179), (254, 145), (327, 206),
            (320, 286), (273, 342), (216, 313), (224, 219),
        ),
    },
    "PANELS": {
        "expand_collapse_top": (386, 9),
        "expand_collapse_bottom": (386, 444),
        "close_top": (449, 9),
        "close_bottom": (449, 445),
    },
    "TOURNAMENT": {
        "tournament": (30, 71),
        "tournament_prestige": (330, 536),
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
}

# When an ad is finished, the exit button is likely going to be in the
# top left or top right corner of the screen... We can click through these
# safely and it should close the ad for us.
AD_EXIT_LOCS = [
    (5, 36),
    (23, 54),
    (43, 74),
    (45, 77),
    (21, 77),
    (7, 77),
    (29, 49),
    (41, 43),
    (47, 40),
    (469, 38),
    (456, 48),
    (434, 71),
    (412, 85),
    (397, 47),
    (413, 44),
    (427, 67),
    (444, 79),
    (463, 91),
]

# Points used when clicking on locations present on the master panel.
MASTER_LOCS = {
    "master_level": (415, 136),
    "prestige": (405, 736),
    "prestige_confirm": (245, 626),
    "prestige_final": (330, 536),
    "screen_top": (240, 6),
    "achievements": (207, 503),
    "daily_achievements": (342, 89),
    "milestones": {
        "milestones_header": (245, 85),
        "milestones_collect_point": (382, 259),
    },
    "skills": {
        "heavenly_strike": (415, 236),
        "deadly_strike": (415, 316),
        "hand_of_midas": (415, 396),
        "fire_sword": (415, 474),
        "war_cry": (415, 546),
        "shadow_clone": (415, 616),
    },
    "skill_level_max": {
        "heavenly_strike": (268, 246),
        "deadly_strike": (268, 323),
        "hand_of_midas": (268, 399),
        "fire_sword": (268, 474),
        "war_cry": (268, 550),
        "shadow_clone": (268, 625),
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

ARTIFACTS_LOCS = {
    # The amount of pixels to push the mouse over when purchasing any artifact. Since the imagesearch
    # will return the top left of the image, we can add these vales to that to click on the purchase button.
    "artifact_push": {
        "x": 375,
        "y": 20,
    },
    "buy_multiplier": (410, 71),
    "buy_max": (50, 71),
    "percent_toggle": (303, 506),
}

SKILL_CAN_LEVEL_LOCS = {
    "heavenly_strike": (460, 218),
    "deadly_strike": (459, 293),
    "hand_of_midas": (460, 369),
    "fire_sword": (459, 444),
    "war_cry": (461, 520),
    "shadow_clone": (459, 594)
}

# Store any colors used (RGB) by the bot to determine so things in game.
GAME_COLORS = {
    "WHITE": (255, 255, 255),
    "DISCOVER": (60, 184, 174),
    "ENCHANT": (235, 167, 12),
    "COLLECT_GREEN": (101, 155, 28),
    "SKILL_CANT_LEVEL": (73, 72, 73),
}

# All images should have their names mapped to the file path within the module.
IMAGES = {
    "ACHIEVEMENTS": {
        "achievements_title": IMAGE_DIR + "/achievements/achievements.png",
        "daily_collect": IMAGE_DIR + "/achievements/daily_collect.png",
        "daily_watch": IMAGE_DIR + "/achievements/daily_watch.png",
    },
    "ADS": {
        "collect_ad": IMAGE_DIR + "/ads/collect.png",
        "watch_ad": IMAGE_DIR + "/ads/watch.png",
        "no_thanks": IMAGE_DIR + "/ads/no_thanks.png",
    },
    "ARTIFACTS": {
        "artifacts_discovered": IMAGE_DIR + "/artifacts/artifacts_discovered.png",
        "book_of_shadows": IMAGE_DIR + "/artifacts/book_of_shadows.png",
        "spend_max": IMAGE_DIR + "/artifacts/spend_max.png",
        "salvaged": IMAGE_DIR + "/artifacts/salvaged.png",
        "percent_on": IMAGE_DIR + "/artifacts/percent_on.png",
        "discover": IMAGE_DIR + "/artifacts/discover.png",
        "enchant": IMAGE_DIR + "/artifacts/enchant.png",
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
        "masteries": IMAGE_DIR + "/heroes/masteries.png",
    },
    "MASTER": {
        "raid_cards": IMAGE_DIR + "/master/raid_cards.png",
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
        "clan_raid_ready": IMAGE_DIR + "/no_panels/clan_raid_ready.png",
        "clan_no_raid": IMAGE_DIR + "/no_panels/clan_no_raid.png",
        "daily_reward": IMAGE_DIR + "/no_panels/daily_reward.png",
        "fight_boss": IMAGE_DIR + "/no_panels/fight_boss.png",
        "hatch_egg": IMAGE_DIR + "/no_panels/hatch_egg.png",
        "leave_boss": IMAGE_DIR + "/no_panels/leave_boss.png",
        "settings": IMAGE_DIR + "/no_panels/settings.png",
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
    "region": (214, 37, 268, 50),
}

PRESTIGE_COORDS = {
    "time_since": (300, 580, 360, 594),
    "advance_start": (145, 523, 202, 543),
}

# The regions for each skill present on the master screen if the panel
# is expanded and scrolled all the way to the top.
MASTER_COORDS = {
    "skills": {
        "heavenly_strike": (0, 199, 480, 269),
        "deadly_strike": (0, 275, 480, 346),
        "hand_of_midas": (0, 351, 480, 421),
        "fire_sword": (0, 426, 480, 497),
        "war_cry": (0, 502, 480, 573),
        "shadow_clone": (0, 578, 480, 648),
    },
}

# Regions used to level up skills in game should only take place when our
# skills are not their specified level or maxed.. We use these regions to grab
# the current level through an OCR check.
SKILL_LEVEL_COORDS = {
    "heavenly_strike": (70, 224, 115, 240),
    "deadly_strike": (70, 299, 115, 318),
    "hand_of_midas": (70, 374, 115, 395),
    "fire_sword": (70, 450, 115, 470),
    "war_cry": (70, 525, 115, 545),
    "shadow_clone": (70, 601, 115, 621),
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

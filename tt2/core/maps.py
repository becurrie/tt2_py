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
    "480x800": {
        "nox": {
            "opened_apps": (500, 815),
            "close_game": (405, 242),
            # The launch game location for all emulators / sizes should be based off of the app being placed
            # in the top most left corner of the home screen within the emulator.
            "launch_game": (53, 232),
        },
    },
}

# All points in game that are relevant to the given resolution can be stored here.
# Not all locations need to be stored here, only locations that otherwise would be
# more of an issue trying to click on after looking for a different image.
GAME_LOCS = {
    "480x800": {
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
                (65, 125), (100, 125), (140, 125), (200, 125), (260, 125), (320, 125), (380, 125), (440, 125),
                (65, 160), (100, 160), (140, 160), (200, 160), (260, 160), (320, 160), (380, 160), (440, 160),
                (65, 230), (100, 230), (140, 230), (200, 230), (260, 230), (320, 230), (380, 230), (440, 230),
                (65, 300), (100, 300), (140, 300), (200, 300), (260, 300), (320, 300), (380, 300), (440, 300),
                (65, 370), (100, 370), (140, 370), (200, 370), (260, 370), (320, 370), (380, 370), (440, 370),
                (65, 440), (100, 440), (140, 440), (200, 440), (260, 440), (320, 440), (380, 440), (440, 440),
                # Click on pet for gold bonus.
                (285, 400),
                # Click on spot where skill points appear.
                (110, 445),
                # Click on spot where equipment appears.
                (355, 445),
            ),
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
            "clan_battle_ready": (82, 59),
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
    }
}

# Points used when clicking on locations present on the master panel.
MASTER_LOCS = {
    "480x800": {
        "master_level": (415, 170),
        "prestige": (405, 770),
        "prestige_confirm": (245, 660),
        "prestige_final": (330, 570),
        "screen_top": (240, 40),
        "skills": {
            "heavenly_strike": (415, 270),
            "deadly_strike": (415, 350),
            "hand_of_midas": (415, 430),
            "fire_sword": (415, 500),
            "war_cry": (415, 580),
            "shadow_clone": (415, 650),
        }
    },
}

# Points used when clicking on locations present in the heroes panel.
HEROES_LOCS = {
    "480x800": {
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
    },
}

ARTIFACTS_LOCS = {
    "480x800": {
        # The amount of pixels to push the mouse over when purchasing any artifact. Since the imagesearch
        # will return the top left of the image, we can add these vales to that to click on the purchase button.
        "artifact_push": {
            "x": 336,
            "y": 55,
        },
        "buy_multiplier": (410, 105),
        "buy_max": (50, 105),
    },
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
        "battle_available": IMAGE_DIR + "/clan_battle/battle_available.png",
        "diamond": IMAGE_DIR + "/clan_battle/diamond.png",
        "goal_complete": IMAGE_DIR + "/clan_battle/goal_complete.png",
        "deal_110_next_attack": IMAGE_DIR + "/clan_battle/deal_110_next_attack.png",
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
}

# All coordinates mapped to their respective resolutions for grabbing
# each stat image that will be parsed by pytesseract.
STATS_COORDS = {
    "480x800": {
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
    },
}

STAGE_COORDS = {
    "480x800": (205, 65, 265, 85),
}

# The regions for each skill present on the master screen if the panel
# is expanded and scrolled all the way to the top.
MASTER_COORDS = {
    "480x800": {
        "skills": {
            "heavenly_strike": (0, 233, 480, 303),
            "deadly_strike": (0, 309, 480, 380),
            "hand_of_midas": (0, 385, 480, 455),
            "fire_sword": (0, 460, 480, 531),
            "war_cry": (0, 536, 480, 607),
            "shadow_clone": (0, 612, 480, 682),
        },
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

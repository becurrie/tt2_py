"""
maps.py

Store any of the mock snapshots that are used by the Bot instance to check for images being present or not.
"""
from settings import TEST_IMAGE_DIR

IMAGES = {
    "ADS": {
        "skill_prompt": TEST_IMAGE_DIR + "/ads/skill_prompt.png",
    },
    "PANELS": {
        "artifacts_collapsed": TEST_IMAGE_DIR + "/panels/artifacts_collapsed.png",
        "artifacts_expanded": TEST_IMAGE_DIR + "/panels/artifacts_expanded.png",
        "equipment_collapsed": TEST_IMAGE_DIR + "/panels/equipment_collapsed.png",
        "equipment_expanded": TEST_IMAGE_DIR + "/panels/equipment_expanded.png",
        "heroes_collapsed": TEST_IMAGE_DIR + "/panels/heroes_collapsed.png",
        "heroes_expanded": TEST_IMAGE_DIR + "/panels/heroes_expanded.png",
        "master_buy_option_open_collapsed": TEST_IMAGE_DIR + "/panels/master_buy_option_open_collapsed.png",
        "master_buy_option_open_expanded": TEST_IMAGE_DIR + "/panels/master_buy_option_open_expanded.png",
        "master_collapsed": TEST_IMAGE_DIR + "/panels/master_collapsed.png",
        "master_expanded": TEST_IMAGE_DIR + "/panels/master_expanded.png",
        "no_panel_open": TEST_IMAGE_DIR + "/panels/no_panel_open.png",
        "no_panel_open_clan_battle": TEST_IMAGE_DIR + "/panels/no_panel_open_clan_battle.png",
        "pets_collapsed": TEST_IMAGE_DIR + "/panels/pets_collapsed.png",
        "pets_expanded": TEST_IMAGE_DIR + "/panels/pets_expanded.png",
        "shop_open": TEST_IMAGE_DIR + "/panels/shop_open.png",
    },
    "MASTER": {
        "master_bottom_collapsed": TEST_IMAGE_DIR + "/master/master_bottom_collapsed.png",
        "master_bottom_expanded": TEST_IMAGE_DIR + "/master/master_bottom_expanded.png",
        "master_collapsed": TEST_IMAGE_DIR + "/master/master_collapsed.png",
        "master_expanded": TEST_IMAGE_DIR + "/master/master_expanded.png",
        "master_prestige_open": TEST_IMAGE_DIR + "/master/master_prestige_open.png",
    },
    "HEROES": {
        "heroes_stats_bottom": TEST_IMAGE_DIR + "/stats/heroes_stats_bottom.png",
    },
    "STAGE": {
        "stage_crop_01": TEST_IMAGE_DIR + "/stats/stage_crop_01.png",
        "stage_crop_02": TEST_IMAGE_DIR + "/stats/stage_crop_02.png",
        "stage_crop_03": TEST_IMAGE_DIR + "/stats/stage_crop_03.png",
    },
    "STATS_TEST": {
        "highest_stage_reached": TEST_IMAGE_DIR + "/stats/test_set/highest_stage_reached.png",
        "total_pet_level": TEST_IMAGE_DIR + "/stats/test_set/total_pet_level.png",
        "gold_earned": TEST_IMAGE_DIR + "/stats/test_set/gold_earned.png",
        "taps": TEST_IMAGE_DIR + "/stats/test_set/taps.png",
        "titans_killed": TEST_IMAGE_DIR + "/stats/test_set/titans_killed.png",
        "bosses_killed": TEST_IMAGE_DIR + "/stats/test_set/bosses_killed.png",
        "critical_hits": TEST_IMAGE_DIR + "/stats/test_set/critical_hits.png",
        "chestersons_killed": TEST_IMAGE_DIR + "/stats/test_set/chestersons_killed.png",
        "prestiges": TEST_IMAGE_DIR + "/stats/test_set/prestiges.png",
        "play_time": TEST_IMAGE_DIR + "/stats/test_set/play_time.png",
        "relics_earned": TEST_IMAGE_DIR + "/stats/test_set/relics_earned.png",
        "fairies_tapped": TEST_IMAGE_DIR + "/stats/test_set/fairies_tapped.png",
        "daily_achievements": TEST_IMAGE_DIR + "/stats/test_set/daily_achievements.png",
        "tournament_points": TEST_IMAGE_DIR + "/stats/test_set/tournament_points.png",
    },
}

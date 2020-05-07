from django.urls import path

from . import views


urlpatterns = [
    path('status', views.status, name='status'),
    # MAIN DASHBOARD.
    path('', views.dashboard, name='dashboard'),
    # CONFIGURATIONS.
    path('configurations', views.configurations, name='configurations'),
    path('configuration/<pk>/', views.configuration, name='configuration'),
    path('configurations/add/', views.add_configuration, name='add_configuration'),
    path('configurations/delete/', views.delete_configuration, name='delete_configuration'),
    path('configurations/import/', views.import_configuration, name='import_configuration'),
    path('configurations/save/', views.save_configuration, name='save_configuration'),
    # GLOBAL SETTINGS.
    path('globals', views.globals, name='globals'),
    path('globals/save/', views.save_globals, name='save_globals'),
    path('globals/save/log/', views.save_log_level, name='save_log_level'),
    # SECONDARY URLS.
    path('project_settings', views.project_settings, name='settings'),
    path('all_prestiges', views.all_prestiges, name='all_prestiges'),
    path('artifacts', views.artifacts, name='artifacts'),
    path('statistics', views.statistics, name='statistics'),
    path('shortcuts', views.shortcuts, name='shortcuts'),
    # SESSIONS.
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/<uuid>/', views.session, name='session'),
    # TOURNAMENTS.
    path('tournaments/', views.tournaments, name='tournaments'),
    path('tournament/<identifier>/', views.tournament, name='tournament'),
    path('tournament/delete/<identifier>', views.delete_tournament, name='delete_tournament'),
    # LOGS.
    path('logs/<pk>/', views.log, name='log'),
    # AJAX URLS.
    path('ajax/release', views.release, name='release'),
    path('ajax/bot_instance/get', views.instance, name='bot_instance'),
    path('ajax/bot_instance/kill', views.kill_instance, name='kill_instance'),
    path('ajax/signal', views.signal, name='signal'),
    path('ajax/prestige', views.prestiges, name='prestiges'),
    path('ajax/game_screen', views.screen, name='game_screen'),
    path('ajax/generate_queued', views.generate_queued, name='generate_queued'),
    path('ajax/theme_change', views.theme_change, name='theme_change'),
    path('ajax/instances/create', views.create_instance, name='create_instance'),
    path('ajax/instances/remove', views.remove_instance, name='remove_instance'),
    path('ajax/open_log', views.open_log, name='open_log'),
    path('ajax/artifacts/toggle', views.toggle_artifact, name='toggle_artifact')
]

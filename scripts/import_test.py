import importlib

modules = [
    'bot',
    'bot.config',
    'bot.db',
    'bot.models',
    'bot.services.dep_service',
    'bot.services.rank_service',
    'bot.services.achievement_service',
    'bot.cogs.dep_cog',
]

for m in modules:
    importlib.import_module(m)

print('imported OK')

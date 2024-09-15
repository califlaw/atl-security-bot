help:
	@echo 'Available commands:                                                '
	@echo '                                                                   '
	@echo 'Usage:                                                             '
	@echo ' make start                                   start application bot'
	@echo ' make init_config                 create local config from template'
	@echo ' make normalize                                       run normalize'

init_config:
	cp bot.config.ini-example bot.config.ini

start:
	@echo "Start cyber bot"
	@python -m src.main

normalize:
	isort ./src
	ruff format ./src

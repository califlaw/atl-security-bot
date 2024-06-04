help:
	@echo 'Available commands:                                                '
	@echo '                                                                   '
	@echo 'Usage:                                                             '
	@echo ' make start                          		 start application bot'
	@echo ' make init_env                       create .env from .env.template'
	@echo ' make normalize                                         run linters'

init_env:
	cp .env.template .env

start:
	@pass

normalize:
	isort ./src
	ruff format ./src

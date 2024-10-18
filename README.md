# ATLANTS SECURITY BOT


## Getting started
ATLANTS SECURITY Bot is an open-source application designed to combat cyber fraud in Kyrgyzstan. Our mission is to protect citizens from the increasing threats posed by cybercriminals and to promote online safety.
Features

Report Cyber Fraud: Users can submit complaints about potential instances of cyber fraud, contributing to a collective effort to identify and combat malicious activities online.

Fraud Detection: Check if specific web resources, such as nicknames, credit card numbers, financial applications, and phone numbers, have been flagged in connection with cyber fraud.

Community-Driven: The bot empowers users to take an active role in the fight against cybercrime by allowing them to report suspicious activities and share their experiences.

User-Friendly Interface: The application is designed with user experience in mind, making it easy for anyone to navigate and report issues.

Join Us in the Fight Against Cybercrime!

As a community, we can make a difference in safeguarding our online environment. By using ATL SEC Bot, you contribute to a larger movement aimed at protecting fellow citizens from cyber threats.

For more information, join our telegram community-group, and also feel free to contribute to the project!

Together, let's stand up against cyber fraud!

***

## Add your files

- [x] [Create merge request](https://github.com/AtlantsIT/atl-security-bot/pulls) with set reviewer `@kdelinx`
- [x] Write on [tg channel](https://t.me/+ztaJjDEotH5hZTQ9) about new commit MR
- [x] Await on approve or comment your version code

```
cd existing_repo
git remote add origin https://github.com/AtlantsIT/atl-security-bot.git
git branch -M feature/<your-update-branch-name>
git push -uf origin feature/<your-update-branch-name>
```

## Installation and development
For development version you need pull from gitlab latest version. Within all dependency dev-tools, like make / gcc / python-dev, and etc... As main package version we use a `poetry>=1.8`, this tools will install on existed virtual environment or could create new. Before that, dont forget install dependencies for your OS (linux / macos / windows) - `libpq-dev`, `python3.11-dev`, `make`, `rustc`. And start will successfully.

**To start dev mode application:**
- set config variable as `environment = dev` in [bot.config.ini](bot.config.ini) file 
- use a command line to execute server bot `$ make start`
- reload application when have added new logic code


## Deploy

If your want deploy bot on your server, you just need fill up settings file ([bot.config.ini](bot.config.ini)). 
Set constants on registered bot name and start image code by command:

**Migrate database**
```shell
# auth by postgres in linux shell
$ su - postgres
# create role and database
$ createrole cyberbot_u && createdb cyberbot -O cyberbot_u
# start migrate sql file to database server
$ psql -U cyberbot_u -d cyberbot < migrations/initial.sql
```

**Init configuration file and start**
```shell
$ make init_config
# fill configs and keys of your bot / database / etc...
$ make start
```

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful.

## Support
All support questions accept on [Telegram channel](https://t.me/+ztaJjDEotH5hZTQ9) or gitlab project issues.

***

## License
For open source projects, say how it is licensed.

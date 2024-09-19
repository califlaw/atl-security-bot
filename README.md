# ATLCyberBot



## Getting started
ATL Cyber Bot - application to detect claims on Kyrgyzstan world wide network. 
The most negative persons, who make citizens on low facture mind.

Everybody could find malefactor and reacted as you need.

***

## Add your files

- [x] [Create merge request](https://gitlab.com/kdelinxd/bot-cyber-detection/-/merge_requests) with set reviewer `@kdelinxd`
- [x] Write on [tg channel](https://t.me/+Ey_WXRTHA7E0YmY1) about new commit MR
- [x] Await on approve or comment your version code

```
cd existing_repo
git remote add origin https://gitlab.com/kdelinxd/bot-cyber-detection.git
git branch -M feature/<your-update-branch-name>
git push -uf origin feature/<your-update-branch-name>
```

## Deploy

If your want deploy bot on your server, you just need fill up settings file ([bot.config.ini](bot.config.ini)). 
Set constants on registered bot name and start image code by command:

Migrate database
```shell
# auth by postgres in linux shell
$ su - postgres
# create role and database
$ createrole cyberbot_u && createdb cyberbot -O cyberbot_u
# start migrate sql file to database server
$ psql -U cyberbot_u -d cyberbot < migrations/initial.sql
```

```shell
$ make init_config
# fill configs and keys of your bot / database / etc...
$ make start
```

## Installation and development
For development version you need pull from gitlab latest version. Within all dependency dev-tools, like make / gcc / python-dev, and etc... As main package version we use a `poetry>=1.8`, this tools will install on existed virtual environment or could create new. Before that, dont forget install dependencies for your OS (linux / macos / windows) - `libpq-dev`, `python3.11-dev`, `make`, `rustc`. And start will successfully.   

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful.

## Support
All support questions accept on [Telegram channel](https://t.me/+Ey_WXRTHA7E0YmY1) or gitlab project issues.

***

## License
For open source projects, say how it is licensed.

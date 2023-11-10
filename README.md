# Statisctics admin Telegram bot
This is an Administrative Telegram bot for the [Bets statistics bot](https://github.com/Den1sproger/bets_statistic_bot "Statistics bot repository"). The admin selects sports games on [this site](https://www.flashscorekz.com/favourites/ "www.flashscorekz.com") and fills them into the database and googlesheets.

The following actions are available to the admin:
* Filling sports games into googlesheets
* Arrangement of own coefficients in googlesheets, approving and recording sports games to the MySQL database
* Clearing table in googlesheets from sports games
* Full calculating the all statistics after the next users voting and recording statistics into DB and googlesheets
* Updating current coefficients of games to more current ones
* Deleting games from MySQL DB and finishing tournament

## To start
### Clone this repository
```
git clone https://github.com/Den1sproger/statisctics-admin-bot.git
```

### Create virtual environment

Windows:
```
python -m venv venv
```

Linux\Mac OS:
```
python3 -m venv venv
```

### Install dependencies

Windows:
```
pip install -r requirements.txt
```

Linux\Mac OS:
```
pip3 install -r requirements.txt
```

### Create MySQL Database
How to create a MySQL database, see [HERE](https://github.com/Den1sproger/bets_statistic_bot "Statistics bot repository")

### Create Telegram Bot
Go to [BotFather](https://t.me/BotFather "Bot Father") and create bot. Save API TOKEN to environment variable under the name **STATISTICS_ADMIN_TOKEN**. Also you should write Telegram chat id of admin to environment variable **ADMIN**.

### Create GoogleSheets
How to create tables in googlesheets and connect with to them, see [HERE](https://github.com/Den1sproger/bets_statistic_bot "Statistics bot repository")

### Launch main file
Windows:
```
python app.py
```

Linux\Mac OS:
```
python3 app.py
```

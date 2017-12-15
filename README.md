# steem-curatebot
Steemit curation bot with Discord integration.

The bot will login to Discord and starts to listen to the blockchain in the background.

If the correct "curateword" is included in a comment from one of the curators, the bot will post the Steemit URL to the predefined Discord "channel".

For demo purposes I have included two Discord bot commands, ?help and ?top10.

?help will return a simple help menu

?top10 will display the Top 10 posts from "utopian-io" tag with the highest payout value. 

## Prerequisites:

* steem-python (https://github.com/steemit/steem-python)
* discord.py (https://github.com/Rapptz/discord.py)
* A Discord bot account with the bot token (https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)

In curatebot.py, update the following lines.

```
curators = ['SteemCurator1','SteemCurator2']
curateword = '!curate'
channel = discord.Object(id='ChannelID')
bottoken = 'DiscordBotToken'
```

## Run:

python3 curatebot.py

## Logging:

Logs will be written to steemit.log

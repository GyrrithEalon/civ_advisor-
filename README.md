#PYTHON 3.13

py-cord nest_asyncio python-dotenv table2ascii aiohttp

#Might move from pycord to discord.py in the future

#
This is an early coding project and it's structured poorly but I have cleaned it up a little for other people to use.

We must be nice to our past selves as they lacked the experience you have in the present, 
and your present self lacks the experience your future self will have.


Deep issue I'm not fixing is making the code properly async. The data this works with is tiny so request collision is unlikely, but not 0%
#
# IMPORTANT
Civ 6 only uses the name the game defined when the cloud game is made, and no other identifier. As a result, there is no good way to differentiate two games that share the same name. Make sure you give your civ games unique names in civ or the civbot will assume they are the game.

#
Setup:
Get a discord bot credential in the discord developer portal. Set your avatar and bot name there.
Bot only responds to slash commands and posts on a channel, I don't think you need extra OAuth or server permissions

https://discord.com/developers/applications

In Discord settings Advanced > Dev mode so you can right-click your server ID (guild ID) and channel ID.

#

```
#Prep env
cp .env-example .env
vim .env
```
Get the expressions ready, list is already randomized and the number at the top of the list is the last used line
```
cp expression.txt-init expression.txt
```
#
connect civ 6
At least one person in each civ game needs to configure Civ 6 to send updates to the bot
```
Civ 6 > Game Options > Game > Play By Cloud Webhook URL:        http://<domain>/<END_POINT_URL>
                            > Play By Cloud Webhook Frequency:  Every Turn
```

Once the bot is connected to your server, have everyone register their user with the bot so that @mentions will work.
If the game doesn't @ someone, have them reregister with the exact name in the games.json (case sensitive).
`/reg-name <Name_in_civ>`
#
Admin commands can CRUD the games database through Discord slash command, useful if something goes wrong.
Make sure the discord id of the admin is put into the env

#
Stale games
Rather than have the Python code understand the concept of time, I used a "magic string" to have 
the bot remind people that it's their turn. Very lazy coding. If an update for a game named 
"GENERATEPING" comes in, the bot @mentions all games that were updated later than "STALE_TIMER_HOURS" in env

```
cp reminder.json ~/reminder.json
crontab -e
#Every day at 5:30pm
30 17 * * * curl -X POST -H 'Content-Type: application/json' -d @reminder.json <bots_URL>
```

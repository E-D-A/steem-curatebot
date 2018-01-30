import discord
from discord.ext import commands
import asyncio
import time
import logging
import json
from steem import Steem

# *** Configure variables ***
curators = ['SteemCurator1','SteemCurator2']
curateword = '!curate'
channel = discord.Object(id='ChannelID')
bottoken = 'DiscordBotToken'

# Setup steem RPC nodes
my_nodes = ['https://api.steemit.com', 'https://rpc.buildteam.io']
steem = Steem(nodes=my_nodes)

# Discord bot description used by the 'help' command
description = '''**```-- Simple Curation Bot --
Below a list of available commands:```**
'''

# Define command prefix for the bot
bot = commands.Bot(command_prefix='?')
# Remove built-in help command. Define own one below
bot.remove_command('help')

# Setup logging
logger = logging.getLogger('steemit')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='steemit.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Global variable to keep track of the last processed block
index = 0

# Discord help command - Displays the menu
@bot.command(pass_context=True)
async def help(context):
    """'?help' - Displays this help message."""
    logger.info("User:" + str(context.message.author) + ", Command: " + str(context.message.content) + ", Channel: " + str(context.message.channel))
    helpmsg = description
    helpmsg += '**?help** - ``Display this help message.``\n'
    helpmsg += '**?top10** - ``Display the top 10 posts with #utopian-io tag with highest payout value.``\n'
    await bot.say(helpmsg)

# Discord Top10 command
@bot.command(pass_context=True)
async def top10(context):
    """'?top10' - Display the top 10 posts in #utopian-io with highest payout value"""
    logger.info("User:" + str(context.message.author) + ", Command: " + str(context.message.content) + ", Channel: " + str(context.message.channel))
    url = "__***--- Top 10 Posts with Highest Payout Value in #utopian-io ---***__ \n"
    for post in steem.steemd.get_posts(sort="payout", category="utopian-io"):
        url += "*https://steemit.com" + post.url + "* - **" + str(post.pending_payout_value) + "**\n"
    await bot.say(url)

# Background task to stream data from the blockchain
async def background_task():
    logger.info('***Steemit Listener Started***: ' + steem.hostname)

    # At program start, fetch the 20 latest blocks
    for attempt in range(6):
        try:
            # Global variable to keep track of the last processed block
            global index
            index = steem.steemd.head_block_number - 20
        except Exception:
            logger.error("Error with steem.steemd.last_irreversible_block_num: " + steem.hostname)
            steem.next_node() # Try the next RPC node
        else:
            break

    # Indefinite loop until bot is stopped
    while not bot.is_closed:
        # For each loop, fetch the 20 latest block
        for attempt in range(6):
            try:
                # Store the value of the last block
                lastblock = steem.steemd.head_block_number
            except Exception:
                logger.error("Error with steem.steemd.last_irreversible_block_num: " + steem.hostname)
                steem.next_node() # Try the next RPC node
            else:
                break
        # Call function to stream data from the blockchain up until the latest block number
        await stream(lastblock)
        # Sleep for 30 seconds to have the stream function run in intervalls of 30 seconds
        await asyncio.sleep(30)

# Stream data from the blockchain
# Look for comments matching the curation variables set above
# Post matching Steemit URL to above defined Discord channel
async def stream(lastblock):
    # Global variable to keep track of the last processed block
    global index
    # Check if we processed all blocks
    if index <= lastblock:
        while index <= lastblock:
            # Prepare to fetch 10 blocks at once
            next_index = index + 10
            # If there are less than 10 blocks, we fetch up to the lastest block + 1
            if next_index > lastblock:
                next_index = lastblock + 1
            # Call function to perform API call
            # We fetch blocks from: index until: next_index
            blocks = get_blocks(steem, index, next_index)
            # Loop through each fetched block
            for block in blocks:
                # Look through items of the type 'transactions'
                for item in block['transactions']:
                    # Check if it is a comment
                    if(item['operations'][0][0] == 'comment'): ### Need to confirmed this is a universal format
                        # Store comment information
                        post = item['operations'][0][1]
                        # Check if there is a match against curation variable set above
                        if(curateword in post['body'].lower() and post['author'] in curators):
                            # Send the URL to Discord and log the request
                            await bot.send_message(channel, 'https://steemit.com/@' + post['parent_author'] + '/' + post['parent_permlink'])
                            logger.info('Curated: ' + 'https://steemit.com/@' + post['parent_author'] + '/' + post['parent_permlink'])
            index = next_index
    # All blocks processed. Fully synced.
    else:
        print('full sync')

# Function to perform the API call
def get_blocks(steem, index, next_index):
    # In case of RPC issues, change node and retry
    for attempt in range(50):
        try:
            blocks = steem.get_blocks_range(index,next_index)
        except Exception:
            logger.info('Error with get_blocks_range: ' + steem.hostname)
            steem.next_node()
            time.sleep(5)
        else:
            return blocks
            break

# Create the loop for the background task
bot.loop.create_task(background_task())
# Start the Discord bot with the bot token
bot.run(bottoken)


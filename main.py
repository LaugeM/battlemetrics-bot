import discord
from discord.ext import commands
from discord.ext.commands import Greedy, Context
from discord import ui, app_commands
import asyncio
import re
from typing import Literal, Optional
import battlemetrics_api
import read_setup_file
import chunked_data
import steam_data
import database

class bot(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.default(), command_prefix=commands.when_mentioned_or("!"))
        self.synced = False
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"Logged in as {self.user}.")
            
aclient=bot()
tree = aclient.tree

# variables
bot_id = ""
bm_api_key = ""


def read_config_file_now():

    global bot_id
    global bm_api_key
    global steam_api_key

    # read the config file and assign the values
    setupDic = read_setup_file.read_config()

    for key in setupDic:
        if key == 'bot_id':
            bot_id = setupDic[key]
        elif key == 'bm_api_key':
            bm_api_key = setupDic[key]
        elif key == 'steam_api_key':
            steam_api_key = setupDic[key]

read_config_file_now()
class Menu(discord.ui.View):
    def __init__(self, bm_id=None):
        super().__init__()
        self.value = None
        self.id = bm_id
        
    @discord.ui.button(label='Name history', style=discord.ButtonStyle.grey)
    async def names_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.id != None:
            bm_names = bm_names_class(interaction, self.id)
            await bm_names.send_bm_names()
            self.stop()
        else:
            await interaction.response.send_message("Battlemetrics id required, register one to enable name history feature")
            self.stop()
            
class player_embed():
    def __init__(self, interaction, team_member):
        super().__init__()
        self.interaction = interaction
        self.team_member = team_member
        self.embed = None
        self.view = None
    async def send_player_embed(self):
        
        avatar = steam_data.grabProfileData(steam_data.convertID(self.team_member[1], "id"), "avatar", steam_api_key)
        current_name = steam_data.grabProfileData(steam_data.convertID(self.team_member[1], "id"), "name", steam_api_key)
        profile_visiblity = steam_data.grabProfileData(steam_data.convertID(self.team_member[1], "id"), "visiblity", steam_api_key)
        visiblity = "Public" if profile_visiblity == 3 else "Private"
        embed=discord.Embed(title=self.team_member[0])
        embed.set_thumbnail(url=avatar)
        
        if self.team_member[0] != current_name:
            embed.add_field(name=f"Player changed name", value=f"Now playing as: {current_name}", inline=False)
        if self.team_member[2] != "Null":
            bm_id = self.team_member[2].split("/")[-1]
            view = Menu(bm_id)
            embed.add_field(name="Rust servers played:", value=battlemetrics_api.get_player_info(bm_id, bm_api_key, "server_count"), inline=True)
            embed.add_field(name="Rust hours:", value=f"{battlemetrics_api.get_player_info(bm_id, bm_api_key, 'hours')[0]}{' (This might not be correct as player has been in over 250 servers)' if battlemetrics_api.get_player_info(bm_id, bm_api_key, 'hours')[1] >= 250 else ''}", inline=True)
            embed.add_field(name="Aim train hours:", value=battlemetrics_api.get_player_info(bm_id, bm_api_key, "aim_hours"), inline=True)
            online = battlemetrics_api.get_player_info(bm_id, bm_api_key, "online")
            if online != False:
                embed.add_field(name="Currently online:", value=online, inline=False)
            view.add_item(discord.ui.Button(label="Steam", url=f"{self.team_member[1]}"))
            view.add_item(discord.ui.Button(label="Battlemetrics", url=f"{self.team_member[2]}"))
        else:
            print("No battlemetrics registered to player in database")
            view = Menu()
            view.add_item(discord.ui.Button(label="Steam", url=f"{self.team_member[1]}"))
        embed.add_field(name=f"Steam: ", value=f"{visiblity} steam profile", inline=False)
        self.embed = embed
        self.view = view
        await self.interaction.followup.send(embed=embed, view=view)
    
class team_select_view(discord.ui.View):
    options = [
        discord.SelectOption(
            label=str(team)[2:-3],
            description=f"{str(database.count_rows(str(team)[2:-3]))} team members registered"
        )
        for team in database.get_teams()
    ]
    
    @discord.ui.select(min_values=1, max_values=1, placeholder="Click me to choose a team", options=options)
    async def select_callback(self, interaction: discord.Interaction, select):
        team_select_view.disabled = True
        await interaction.response.send_message(f"You chose: {select.values[0]}")
        team_list = database.lookup_team(select.values[0])
        if len(team_list) > 0:
            for team_member in team_list:
                player = player_embed(interaction, team_member)
                await player.send_player_embed()
        print(f"Successfully delivered team: {select.values[0]} to channel")
        
    
class add_player_modal(discord.ui.Modal, title="Add a player to a team"):
    team = discord.ui.TextInput(
        label='Team',
        required=True,
        placeholder='Enter the team the player should be added to here'
    )
    steam = discord.ui.TextInput(
        label='Steam',
        placeholder='Enter the players steam ID or link here',
        required=True,
        max_length=75
    )
    bm_link = discord.ui.TextInput(
        label='Battlemetrics link',
        placeholder="Enter the players battlemetrics link here",
        required=False,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        check_bm_link = re.match(
            "^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]battlemetrics+)\.com\/players\/([^\/]+)$", self.bm_link.value)
        if check_bm_link == True or len(self.bm_link.value) == 0:
            print("No bm link")
        if len(self.bm_link.value) == 0:
            add_player = add_player_class(interaction, self.team.value, self.steam.value)
        else: 
            add_player = add_player_class(interaction, self.team.value, self.steam.value, self.bm_link.value)
        await add_player.add_to_database()
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class bm_names_class():
    def __init__(self, interaction, id):
        super().__init__()
        self.interaction = interaction
        self.id = id
    async def send_bm_names(self):
        await self.interaction.response.send_message("Getting bm names from api")
        p_info = battlemetrics_api.get_player_info(self.id, bm_api_key, "names")
        if len(p_info) > 0:
            chunked_names_list = chunked_data.get_chunked_data(p_info)
            for all_names in chunked_names_list:
                await self.interaction.followup.send(all_names)
        
class add_player_class():
    def __init__(self, interaction, team, steam, bm_link=None):
        super().__init__()
        self.interaction = interaction
        self.team = team
        self.steam = steam
        self.bm_link = bm_link
    async def add_to_database(self):
        print("add_to_database")
        if self.bm_link:
            print("check bm link")
            check_bm_link = re.match(
                "^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]battlemetrics+)\.com\/players\/([^\/]+)$", self.bm_link)
            print(check_bm_link)
        if self.steam != None:
            print("steam input")
            clean_steam = re.sub('http(s)?(:)?(\/\/)?|(\/\/)?(www\.)?', '', self.steam)
            steam_id = steam_data.convertID(clean_steam, "id")
            player_name = steam_data.grabProfileData(steam_id, "name", steam_api_key)
            if self.bm_link and check_bm_link:
                print("bm link good, trying to add player")
                database.create_player_table(self.team)
                steam_link = steam_data.convertID(clean_steam, "url")
                bm = battlemetrics_api.convert_input(self.bm_link)
                print(bm)
                print(steam_link)
                database.add_player_data(self.team, player_name, steam_link, bm)
                await self.interaction.response.send_message(f"Successfully added player: {player_name} to {self.team}'s team")
            elif self.bm_link == None or not check_bm_link:
                print("invalid bm link, adding player to database without")
                database.create_player_table(self.team)
                steam_link = steam_data.convertID(clean_steam, "url")
                print(steam_link)
                database.add_player_data(self.team, player_name, steam_link)
                await self.interaction.response.send_message(f"Successfully added player: {player_name} to {self.team}'s team without battlemetrics")          
        else:
            print("Needs atleast steam input")
            await self.interaction.response.send_message("Error adding player to team. Have you checked if your input is correct?")
        
#test command
@commands.is_owner()
@tree.command(name="bm_test", description="test command")
async def self(interaction: discord.Interaction): 
    print("recieved test command")
    await interaction.response.send_message('You used the test command')

#ping command
@tree.command(name="ping", description="test ping")
async def self(interaction: discord.Interaction): 
    print("recieved ping command")
    await interaction.response.send_message('Pong')

#names command
@tree.command(name="names", description="Get recent names of player from BM api")
async def self(interaction: discord.Interaction, id: int):
    print("recieved names command")
    try:
        bm_names = bm_names_class(interaction, id)
        await bm_names.send_bm_names()
        
                    
    except Exception as e:
        print('An error occured in on_message Discord Bot ::' + str(e))

#add player to team command
@tree.command(name="add", description="Register a player to a team")
async def self(interaction: discord.Interaction, team: str=None, steam: str=None, bm_link: str=None):
    print("recieved add command")
    try:
        if team==None and steam==None and bm_link==None:
            print("No input, sending modal")
            await interaction.response.send_modal(add_player_modal())
        else:
            player_class = add_player_class(interaction, team, steam, bm_link)
            await player_class.add_to_database()
    except Exception as e:
        print('An error occured in on_message Discord Bot ::' + str(e))
            
        
#show team command     
@tree.command(name="team", description="Shows registered members of a team")
async def self(interaction: discord.Interaction, team: str=None):
    print("recieved team command")
    try:
        if team != None:
            team_list = database.lookup_team(team)
            if len(team_list) > 0:
                await interaction.response.send_message("Team recieved from database, delivering to channel")
                for team_member in team_list:
                    player = player_embed(interaction, team_member)
                    await player.send_player_embed()
            print("Successfully delivered team to channel")
        elif team == None:
            print("No argument recived, showing select menu")
            view = team_select_view()
            await interaction.response.send_message(view=view)
    except Exception as e:
        print('An error occured in on_message Discord Bot ::' + str(e))
        
#hours command
@tree.command(name="hours", description="get rust hours from battlemetrics api")
async def self(interaction: discord.Interaction, bm_id: int): 
    print("recieved hours command")
    player_hours = battlemetrics_api.get_player_info(bm_id, bm_api_key, "hours")
    player_info = battlemetrics_api.get_player_info(bm_id, bm_api_key, "info")
    await interaction.response.send_message(f'Player "{player_info[0]}" was first seen {player_info[1][:10]} and has {player_hours} hours in rust')
        
#sync command  
# stolen directly from the discord.py guild
@aclient.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    print("recieved sync command")
    if not guilds:
        if spec == "~":
            synced = await tree.sync(guild=ctx.guild)
        elif spec == "*":
            tree.copy_global_to(guild=ctx.guild)
            synced = await bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            tree.clear_commands(guild=ctx.guild)
            await tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

aclient.run(bot_id)
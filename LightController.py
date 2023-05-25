import random
import datetime
import discord
import serial
import LightControllerClient as LCC
import threading
from discord import app_commands
import time

"""
    Kaydle's Discord Light Controller
    Controlling IR lights over arduino, 
    with controls for discord and a windows tray client.
    
    Feel free to steal
"""

arduino_connected = False
lights_public = True
lights_on = True

# set to you own Discord id to have owner controls.
owner_id = None

# attempt to Connect to arduino
try:
    arduino = serial.Serial("COM3")
    arduino.baudrate = 9600
    arduino.bytesize = 8

    arduino_connected = True

    # Run Personal windows tray client. Pystray library not daemon by default.
    LCC.x.run_detached()
except serial.serialutil.SerialException as exc:
    print(exc)

# Personal Light function and names for the Light's controller
lightfunctions = ['12', '16', '0A', '03', '12', '17', '0B', '04', '13', '18', '0C', '05', '14', '19',
                  '0D', '06']
lightfunctionsnames = ["Candle", "Bulb", "Sun", "Cold", "low", "bed", "Bright", "Zen", "Morning", "Rainbow #1",
                       "Rainbow #2", "Beach", "Forest", "Ocean", "Fire", "Love"]

# in if statement to collapse in IDE's - Just defining embeds
if True:
    Functions_embed = discord.Embed(title="Functions", colour=0x323332,
                                    description="This is a list of available functions for the "
                                                "'Lightsfunction' and 'random' commands. Functions are "
                                                "modes/colors the light can be switched on to")
    content_string = ""
    for i, val in enumerate(lightfunctionsnames):
        content_string = content_string + f"\t{i + 1}, {val}\n"
    Functions_embed.add_field(name="Functions", value=content_string)
    Functions_embed.set_author(name="Kaydle's Lights", icon_url="https://cdn-icons-png.flaticon.com/512/32/32175.png")

    Help_embed = discord.Embed(title="Info and commands.", colour=0xa1a3a5,
                               description="This bot is a discord bot to control Kaydle's lights. There is no point for"
                                           " This bot to be public. But it is. Dont be annoying pls.")
    content_string = ("\t**/lightson** - *Turn lights on (duh)*"
                      "\n\t**/lightsoff** - *Turn lights off*"
                      "\n\t**/lightsfunction** - *Set light to a specific function (/functions for more info)*"
                      "\n\t**/functions** - *Show available functions*"
                      "\n\t**/random** - *Set lights to a random function*"
                      "\n\t**/reconnect** - *Reconnect Arduino if disconnected*"
                      "\n\t**/help** - *Help about this bot*")
    Help_embed.add_field(name="Commands.", value=content_string)
    Help_embed.set_author(name="Kaydle's Lights", icon_url="https://cdn-icons-png.flaticon.com/512/32/32175.png")


def date_header():
    tc = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"\u001b[36m({tc})\u001b[0m"


# Headers for Console coloring
class Headers:
    LOGGER = '\u033b\u033b[LOGGER]\033[0m'
    COMMAND = '\u033b\u331b[COMMAND]\033[0m'
    SET_LIGHTS = '\u033b\u033b[SERIAL]\033[0m'


# Threadable object for running Windows tray client
def tray_threaded():
    while True:
        # Disabling time.sleep will make very high cpu usage
        time.sleep(0.3)
        if LCC.event_list:
            x = LCC.event_list[0]
            LCC.event_list.pop(0)
            if type(x) is list:
                set_lights(int(lightfunctions[x[1] - 1], 16))
            elif x == 0:
                set_lights(2)
            elif x == 1:
                set_lights(1)
            elif x == 2:
                set_lights(int(random.choice(lightfunctions), 16))


# Define Discord command tree and client
class Aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await bot.sync(guild=None)
            self.synced = True
        print(f"{self.user} Has logged in")
        print(f"Arduino status: {arduino_connected}")

        td = threading.Thread(target=tray_threaded, daemon=True)
        td.start()


client = Aclient()
bot = app_commands.CommandTree(client)


# logging function
def log(pubdata, truedata, file="log.txt"):
    try:
        print(f"{Headers.LOGGER} {date_header()} Logging: {*pubdata,} ")

        log_file = open(file, "a")
        log_file.write(f"[LOG] {datetime.datetime.utcnow()}; {truedata}" + "\n")
        log_file.close()
    except Exception as excep:
        print(excep)


# Send command to arduino to set lights
def set_lights(bytestring):
    print(f"{Headers.SET_LIGHTS} {date_header()} Sending arduino: {bytestring}")
    arduino.write(str(bytestring).encode('utf-8'))
    return arduino.readline()


# Called upon arduino not connected
async def not_active(interaction: discord.Interaction):
    await interaction.response.send_message("Arduino not active!")


# Called upon discord user using bot when public is not active and user not owner
async def not_public(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is disabled from public usage :(.")


"""
    Discord Commands Below.
"""


@bot.command(name="lightson", description="set lights on", guild=None)
async def lights_on_command(interaction: discord.Interaction):
    if not lights_public and not interaction.user.id == owner_id:
        await not_public(interaction)
        return

    print(f"{Headers.COMMAND} {date_header()} Lights_on_Command Run")
    log((interaction.user.name, interaction.guild.name, "C: Lights_On"),
        (f"U: {interaction.user.id}", f"G: {interaction.guild_id}", "C: Lights_On"))

    if arduino_connected:
        set_lights(1)
        await interaction.response.send_message("set lights on")
        global lights_on
        lights_on = True
    else:
        await not_active(interaction)


@bot.command(name="lightsoff", description="set lights off", guild=None)
async def lights_off_command(interaction: discord.Interaction):
    if not lights_public and not interaction.user.id == owner_id:
        await not_public(interaction)
        return
    print(f"{Headers.COMMAND} {date_header()} Lights_off_Command Run")
    log((interaction.user.name, interaction.guild.name, "C: Lights_Off"),
        (f"U: {interaction.user.id}", f"G: {interaction.guild_id}", "C: Lights_Off"))

    if arduino_connected:
        set_lights(2)
        await interaction.response.send_message("set lights off")
        global lights_on
        lights_on = False
    else:
        await not_active(interaction)


@bot.command(name="lightsfunction", description="change light to function from 1 - 16", guild=None)
async def lights_function_command(interaction: discord.Interaction, functionint: int):
    print(f"{Headers.COMMAND} {date_header()} Lights_Function_Command Run")
    log((interaction.user.name, interaction.guild.name, "C: Lights_Function"),
        (f"U: {interaction.user.id}", f"G: {interaction.guild_id}", "C: Lights_Function"))

    if not lights_public and not interaction.user.id == owner_id:
        await not_public(interaction)
        return

    if arduino_connected:
        if not 0 < functionint < 17:
            await interaction.response.send_message(f"Please choose a number between 1 - 16")
            return

        command = lightfunctions[functionint - 1]
        set_lights(int(command, 16))
        await interaction.response.send_message(f"set lights too {functionint}. {lightfunctionsnames[functionint - 1]}")
    else:
        await not_active(interaction)


@bot.command(name="random", description="Set light to random setting", guild=None)
async def lights_random_command(interaction: discord.Interaction):
    print(f"{Headers.COMMAND} {date_header()} Lights_Function_Random Run")
    log((interaction.user.name, interaction.guild.name, "C: Lights_Random"),
        (f"U: {interaction.user.id}", f"G: {interaction.guild_id}", "C: Lights_Random"))

    if not lights_public and not interaction.user.id == owner_id:
        await not_public(interaction)
        return

    if arduino_connected:
        choice = random.randrange(1, 18)
        if choice == 1:
            set_lights(1)
            await interaction.response.send_message(f"Set lights on.")
        elif choice == 2:
            set_lights(2)
            await interaction.response.send_message("Set lights off.")
        else:
            set_lights(1)
            command = lightfunctions[choice - 3]
            await interaction.response.send_message(f"Set lights to {lightfunctionsnames[choice - 3]} "
                                                    f"(Function #{choice - 2})")
            set_lights(int(command, 16))


@bot.command(name="functions", description="Show Availiable Functions", guild=None)
async def arduino_functions_command(interaction: discord.Interaction):
    await interaction.response.send_message(embed=Functions_embed)


@bot.command(name="help", description="What is this bot about? what are the commands?", guild=None)
async def discord_help_command(interaction: discord.Interaction):
    await interaction.response.send_message(embed=Help_embed)


@bot.command(name="reconnect", description="Reconnect to unconnected arduino", guild=None)
async def arduino_reconnect_command(interaction: discord.Interaction):
    try:
        global arduino
        arduino = serial.Serial("COM3")
        arduino.baudrate = 9600
        arduino.bytesize = 8
        global arduino_connected
        arduino_connected = True
        await interaction.response.send_message(f"Arduino connected succesfully")

    except serial.serialutil.SerialException:
        await interaction.response.send_message(f"Arduino failed to connect")


@bot.command(name="toggle_public", description="toggle public-ness of Discord Bot", guild=None)
async def toggle_public(interaction: discord.Interaction):
    if interaction.user.id == owner_id:
        global lights_public
        lights_public = not lights_public

        await interaction.response.send_message(f"Light publicity set to {lights_public}")
    else:
        await interaction.response.send_message("Owner only command!")


# Put your client token here
client.run("")

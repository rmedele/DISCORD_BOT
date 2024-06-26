import discord
from discord.ext import commands, tasks
from Tokens import *  # Import API keys and other variables from Tokens module
import requests
from google.cloud import texttospeech
import os

# Quickly connect to Google Cloud for credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Coding\\Discord\\discord-bot-427402-178a8a992e01.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

tts_client = texttospeech.TextToSpeechClient()
last_live_data = {}

@client.event
async def on_ready():
    print("DISCORD BOT CONNECTED")
    print("---------------------")
    monitor_live_events.start()

@client.command(pass_context=True)
async def exit(ctx):
    if ctx.author.id == AUTHOR_ID:
        await ctx.send("Goodbye..")
        await client.close()
    else:
        await ctx.send("You can't do that!")

@client.command(pass_context=True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Not in a Voice Channel")

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Leaving Voice channel")
    else:
        await ctx.send("Not in a Voice Channel")

def get_live_match():
    url = 'https://v3.football.api-sports.io/fixtures?live=all'
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['response']
    return None

def synthesize_text(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return response.audio_content

@tasks.loop(seconds=60)  # every 60 seconds
async def monitor_live_events():
    global last_live_data
    current_live_data = get_live_match()

    if current_live_data:
        if not last_live_data:
            last_live_data = {match['fixture']['id']: match for match in current_live_data}
            return

        for match in current_live_data:
            match_id = match['fixture']['id']
            current_events = match.get('events', [])

            if match_id not in last_live_data:
                last_live_data[match_id] = {'events': []}

            last_events = last_live_data[match_id].get('events', [])
            new_events = [event for event in current_events if event not in last_events]

            for event in new_events:
                event_type = event['type']
                event_message = ""

                if event_type == 'goal':
                    scorer = event['player']['name']
                    team = event['team']['name']
                    event_message = f"Goal for {team} by {scorer}"
                elif event_type == 'yellow card':
                    player = event['player']['name']
                    event_message = f"Yellow card for {player}"
                elif event_type == 'red card':
                    player = event['player']['name']
                    event_message = f"Red card for {player}"
                elif event_type == 'free kick':
                    team = event['team']['name']
                    event_message = f"Free kick for {team}"
                elif event_type == 'corner':
                    team = event['team']['name']
                    event_message = f"Corner for {team}"

                if event_message:
                    audio_content = synthesize_text(event_message)
                    with open('event_announcement.mp3', 'wb') as out:
                        out.write(audio_content)

                    for channel in client.get_all_channels():
                        if isinstance(channel, discord.VoiceChannel):
                            voice_client = await channel.connect()
                            if voice_client.is_connected():
                                voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source="event_announcement.mp3"))
                                await voice_client.disconnect()

            last_live_data[match_id]['events'] = current_events

@client.command()
async def details(ctx, country=None):
    if not country:
        await ctx.send("Country not entered.")
        return

    url = f'https://v3.football.api-sports.io/fixtures?live=all'
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_data = response.json().get('response', [])

        if match_data:
            found_match = False
            for match in match_data:
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                league = match['league']['country']
                
                # Check if the country matches
                if country.lower() in league.lower() or country.lower() in home_team.lower() or country.lower() in away_team.lower():
                    found_match = True
                    home_score = match['goals']['home']
                    away_score = match['goals']['away']
                    status = match['fixture']['status']['short']
                    scorers = match.get('goals', {}).get('scorers', [])

                    details_message = f"{home_team} vs {away_team}\n"
                    details_message += f"CURRENT SCORE: {home_team} {home_score} - {away_score} {away_team}\n"
                    details_message += f"Status: {status}\n"

                    if scorers:
                        details_message += "**Goal Scorers:**\n"
                        for scorer in scorers:
                            details_message += f"- {scorer['player']['name']} ({scorer['time']['elapsed']}')\n"

                    await ctx.send(details_message)

            if not found_match:
                await ctx.send(f"No live match details found for {country}.")
        else:
            await ctx.send(f"No live match details found for {country}.")
    else:
        await ctx.send(f"Failed to fetch data from API. Status code: {response.status_code}")

@client.command()
async def test(ctx):
    await ctx.send("TESTING!")

@client.command()
async def bot_help(ctx):
    help_message = "----- COMMANDS FOR BOT -----\n" \
                   "!live: Shows live match results and score\n" \
                   "!test: Test print for bot\n" \
                   "!exit: Turns off Bot\n" \
                   "!join: Bot joins current users VC\n" \
                   "!leave: Bot leaves current users VC"
    await ctx.send(help_message)
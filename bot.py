import discord
import os
from dotenv import load_dotenv
import re
import maxroll_scrap
import datetime

# Load secrete and config Variable File
load_dotenv('.env')

# Instanciation liste des leaderboards surveillés
lboards = ['barbarian','crusader','dh','monk','wd','wizard','team-2','team-3','team-4']

# TODO : Personnalisation du client en mode objet
client = discord.Client()

# Feedback bot en ligne
@client.event
async def on_ready():
    print(datetime.datetime.now()) 
    print(">> Bot prêt à l'écoute <<")
    channel = client.get_channel(os.getenv('BOT_CHANNEL'))#  channel a mettre dans un fichier de config
    await channel.send("Bonjour, Je suis à l'écoute de vos commandes (!help)") #  Sends message to channel

# Fonction d'écoute de mot clef
@client.event
async def on_message(message):
    print(f"Message reçu : '{message.content}'")
    cmd = message.content
    # message traité si commence par un '!' et est sur le canal écouté 
    if cmd[0] == "!" and message.channel.name == os.getenv('BOT_CHANNEL'):
        cmd = cmd[1:]

        ### Commandes classements BriTs
        # vérif présence d'options
        if " " in cmd:
            cmd = cmd.split(" ")
            # identification des options
            for arg in cmd:
                if arg == "--soft":
                    mode = arg
                # si saisie multiple d'option num saison, seule la première est lue 
                if re.search("^-S\d{1,2}$", arg) and not 'season' in locals():
                    season = arg[2:]
            # contrôle de validité du radical de la commande
            if cmd[0] in lboards:
                # valorisation des appels scrap en fonction des options trouvées
                if 'team' in cmd[0]:
                    r = maxroll_scrap.get_teams(cmd[0],\
                    season if 'season' in locals() else '',\
                    mode if 'mode' in locals() else '')
                else:
                    r = maxroll_scrap.get_single_class(cmd[0],\
                    season if 'season' in locals() else '',\
                    mode if 'mode' in locals() else '')
            elif re.search("^[a-zA-Z]+#\d{4,6}$", cmd[0]):
                r = maxroll_scrap.get_btag(cmd[0],\
                    season if 'season' in locals() else '',\
                    mode if 'mode' in locals() else '',\
                    lboards)
            
        # Si un seul param, alors uniquement type ladder (sinon cmd invalide sans feedback user)
        else:
            if cmd in lboards:
                if 'team' in cmd:
                    r = maxroll_scrap.get_teams(cmd,'','')
                else:
                    r = maxroll_scrap.get_single_class(cmd,'','')
            elif re.search("^[a-zA-Z]+#\d{4,6}$", cmd):
                r = maxroll_scrap.get_btag(cmd,"","",lboards)

        
        # Liste des commandes
        if cmd == "help":
            r = f"```fix\nUsage : classements BriTs\n> Affiche les 5 premiers BriTs par ladder```"
            r = r + "**![ladder]** [*-Sxx*] [*--soft*]\n"
            r = r + f"__Liste des ladders__ : {str(lboards)}\n"
            r = r + f"\n **Option** *-S'numéro de saison sur 2 caractères (01 à {str(maxroll_scrap.get_current_season())})'* -> Facultatif, saison en cours par défaut."
            r = r + f"\n **Option** *--soft* : retourne les classements softcore -> Facultatif, classements hardcore par défaut.\n"
            r = r + f"Exemples :"
            r = r + f"```!dh```"
            r = r + f"```!crusader -S23```"
            r = r + f"```!team-4 -S05 --soft```"
            r = r + "\n```fix\nUsage : classements par BattleTag```<*Coming soon*>"

        if cmd == "test":
            field1 = f"**![ladder]** [*-Sxx*] [*--soft*]\n__Liste des ladders__ :\n{str(lboards)}\n**Option** *-S'numéro de saison sur 2 caractères (01 à {str(maxroll_scrap.get_current_season())})'* -> Facultatif, saison en cours par défaut.\n **Option** *--hc* : retourne les classements hardcore -> Facultatif, classements softcore par défaut.\n"
            field2 = "!dh\n!crusader -S23\n!team-4 -S05 --hc\n"
            field3 = "Facultatif, classements softcore par défaut.\n"
            #### Create the initial embed object ####
            embedVar=discord.Embed(title="D3RANKINGBOT HELP PAGE", description="Explication des commandes du Bot", color=0x109319)
            # Add author, thumbnail, fields, and footer to the embed
            embedVar.set_author(name="RBD3", icon_url="https://i.pinimg.com/564x/0f/78/35/0f78351ab8e87c159ce442d7fb6912a5.jpg")
            embedVar.set_thumbnail(url="https://static.wikia.nocookie.net/dauntless_gamepedia_en/images/a/a8/Riftsoul_Shard_Icon_001.png")
            embedVar.add_field(name="Les BriT dans le classement", value=field1, inline=True) 
            embedVar.add_field(name="Exemples :", value=field2, inline=True)
            embedVar.add_field(name="Usage Classements par BattleTag", value=field3, inline=False)
            embedVar.set_footer(text="This is the footer. It contains text at the bottom of the embed")
            await message.channel.send(embed=embedVar)

    if 'r' in locals():
        if r.count('\n') < 4:
            await message.channel.send(f"{r}*<Pas de classement Top1000 EU à afficher>*")
        else:
            await message.channel.send(r)

# Exécution du bot
client.run(os.getenv('TOKEN'))
import discord
import os
from dotenv import load_dotenv
import re
import maxroll_scrap
import datetime

# Load secrete and config Variable File
load_dotenv('.env')

# Instanciation liste des leaderboards surveillés
lboards = ['barbarian','crusader','dh','monk','necromancer','wd','wizard','team-2','team-3','team-4']

# TODO : Personnalisation du client en mode objet
client = discord.Client()

# Feedback bot en ligne
@client.event
async def on_ready():
    print(datetime.datetime.now()) 
    print(">> Bot prêt à l'écoute <<")

# Fonction d'écoute de mot clef
@client.event
async def on_message(message):
    print(f"Message reçu : '{message.content}'")
    cmd = message.content
    # message traité si commence par un '!' et est sur le canal écouté 
    if cmd[0] == "!" and message.channel.name == os.getenv('BOT_CHANNEL_NAME'):
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
            #Contenu des embed
            usage = f"la commande doit debutée par ** ! ** et etre suivie sans espace du classement désiré parmi la liste ci-apres\n{str(lboards)}"
            option = f"separées d'un espace de la commande et prefixé de 1 ou 2 tirets,\
            \nelles permettent de précicer une saison et/ou un mode:\
            \n**-S** suivi directement du numero de saison sur 2 caracteres\
            \n**--** suivi directement de *sc*/*hc* pour respectivement softcore ou hardcore\
            \nSans l'ajout d'option, les classements seront ceux de \nla derniere __*saison*__ en __*Hardcore*__"
            exemple = f"!dh : *Chasseur de demon en Hardcore de la derniere saison {str(maxroll_scrap.get_current_season())}*\
            \n!crusader -S17 : *Croisé en Hardcore de la saison 17*\
            \n!team-4 -S05 --sc : *4 joueurs en Softcore de la saison 5*"
            usage_btag = "<*Coming soon*>"
            vide=""
            #### Create the initial embed object ####
            embedVar=discord.Embed(title="Consultez les classements Hardcore et Softcore\n de vos heros et ceux des membres de votre clan", description="Ci-dessous les commandes du Bot et leurs utilisations", color=0x9b59b6)
            # Add author, thumbnail, fields, and footer to the embed
            embedVar.set_author(name="Diablo III Ranking Bot", icon_url="https://static.wikia.nocookie.net/dauntless_gamepedia_en/images/a/a8/Riftsoul_Shard_Icon_001.png")
            embedVar.set_thumbnail(url="https://static.wikia.nocookie.net/dauntless_gamepedia_en/images/a/a8/Riftsoul_Shard_Icon_001.png")
            embedVar.add_field(name="Les Commandes ", value=usage, inline=False)
            embedVar.add_field(name="Les Options", value=option, inline=False)
            embedVar.add_field(name="Exemples de demande de classement", value=exemple, inline=False)
            embedVar.add_field(name="Usage Classements par BattleTag", value=usage_btag, inline=False)
            embedVar.set_footer(text="Sont seulement pris en compte les joueurs du Top 1000")
            await message.channel.send(embed=embedVar)

    if 'r' in locals():
        if r.count('\n') < 4:
            await message.channel.send(f"{r}*<Pas de classement Top1000 EU à afficher>*")
        else:
            await message.channel.send(r)

# Exécution du bot
client.run(os.getenv('TOKEN'))
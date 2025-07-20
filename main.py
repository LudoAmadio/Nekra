import discord
import json
import asyncio
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

class TicketButtonsView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for btn in config.get("ticket_buttons", []):
            style = btn.get("style", 1)
            self.add_item(Button(label=btn["label"], custom_id=btn["custom_id"], style=discord.ButtonStyle(style)))

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for btn in config["buttons"]:
            self.add_item(Button(label=btn["label"], style=discord.ButtonStyle.primary, custom_id=btn["custom_id"]))

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")

@bot.command()
async def send_ticket(ctx):
    embed = discord.Embed(
        title="🎫 Support",
        description="Merci de sélectionner le véhicule sorti du Garage 50 sur Grappeseed",
        color=discord.Color.light_grey()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id")

    if custom_id and custom_id.startswith("create_ticket_"):
        vehicle_name = custom_id.replace("create_ticket_", "").replace("_", "-")
        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{vehicle_name.lower()}",
            overwrites=overwrites,
            topic=f"Ticket ouvert par {interaction.user.display_name} pour {vehicle_name}"
        )

        await ticket_channel.send(
            content=f"{interaction.user.mention}",
            embed=discord.Embed(
                title=f"Ticket - {vehicle_name}",
                description=config["ticket_message"],
                color=discord.Color.green()
            ),
            view=TicketButtonsView()
        )

        await interaction.response.send_message(f"🎟️ Ticket créé ici : {ticket_channel.mention}", ephemeral=True)

    elif custom_id == "close_ticket":
        await interaction.channel.send("🔒 Fermeture du ticket dans 5 secondes...")
        await interaction.response.defer()
        await asyncio.sleep(5)
        await interaction.channel.delete()

    elif custom_id == "request_quote":
        await interaction.response.send_message("🧾 Un devis sera préparé par un membre du staff.", ephemeral=True)

bot.run("TON_TOKEN_ICI")

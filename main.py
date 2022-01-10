import discord
from discord.ext import commands
from discord import DMChannel
import random
import time
import os
import asyncio
import datetime
import json

os.chdir("C:\\Users\\lgshu\\Desktop\\Python Programs\\Bank System\\tempsys\\Bank-System\\Bank-System-Revamp")

from discord.ext.commands.bot import Bot
from apikeys import *


#This is a discord bot used for money and gambling stuff


client = commands.Bot(command_prefix= "~")
client.remove_command("help")


@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title = "Help", description = "Use ~help [command] for extended information on a command.",color = ctx.author.color)

    em.add_field(name = "Bank Management", value = "~balance, ~beg, ~withdraw, ~deposit, ~send, ~spend, ~slots")
    em.add_field(name = "Miscellaneous", value = "~roll_dice, ~jm, ~flip_coin")

    await ctx.send(embed = em)


@help.command()
async def balance(ctx):

    em = discord.Embed(title = "Balance", description = "Checks the balance in your bank account. If you do not have one, it will create it.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~balance")

    await ctx.send(embed = em)


@help.command()
async def beg(ctx):

    em = discord.Embed(title = "Beg", description = "Begs nearby people to donate to you.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~beg")

    await ctx.send(embed = em)


@help.command()
async def withdraw(ctx):

    em = discord.Embed(title = "Withdraw", description = "Withdraws money from your bank account and adds it to your wallet.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~withdraw [amount]")

    await ctx.send(embed = em)


@help.command()
async def deposit(ctx):

    em = discord.Embed(title = "Deposit", description = "Takes money from your wallet and deposits it to your bank account.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~deposit [amount]")

    await ctx.send(embed = em)


@help.command()
async def send(ctx):

    em = discord.Embed(title = "Send", description = "A P2P payment method. Sends another user some of your money.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~send [user] [amount]")

    await ctx.send(embed = em)


@help.command()
async def spend(ctx):

    em = discord.Embed(title = "Spend", description = "A more documented version of send. Lets you buy something from a user",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~spend [amount] [user]")

    await ctx.send(embed = em)


@help.command()
async def slots(ctx):

    em = discord.Embed(title = "Slots", description = "Risk your money at a slot machine. If you win, you get double what you gambled. If you lose, you lose what you gambled",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~slots [amount]")

    await ctx.send(embed = em)


@help.command()
async def flip_coin(ctx):

    em = discord.Embed(title = "Flip_Coin", description = "Flips a coin, the bot answers with heads or tails.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~flip_coin")

    await ctx.send(embed = em)


@help.command()
async def roll_dice(ctx):

    em = discord.Embed(title = "Roll dice", description = "The bot rolls some dice and will tell you what it lands on.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~roll_dice")

    await ctx.send(embed = em)


@help.command()
async def jm(ctx):

    em = discord.Embed(title = "JM", description = "If you don't know what this command does, don't worry about it. If someone refers you they will tell you.",color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "~jm")

    await ctx.send(embed = em)


@client.event
async def on_ready():
    print("The bot is ready")
    print("################")


@client.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title = f"{ctx.author.name}'s balance",color = discord.Color.red())
    em.add_field(name = "Wallet",value = wallet_amt)
    em.add_field(name = "Bank balance",value = bank_amt)
    await ctx.send(embed = em)


@client.command()
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()
    user = ctx.author
    earnings = random.randrange(101)
    await ctx.send(f"Someone gave you {earnings} credits!")
    
    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users,f)


@client.command()
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return
    
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that many credits!")
        return

    if amount<0:
        await ctx.send("Amount must be positive!")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")

    await ctx.send(f"You withdrew {amount} credits!")


@client.command()
async def deposit(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return
    
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("You don't have that many credits!")
        return

    if amount<0:
        await ctx.send("Amount must be positive!")
        return

    await update_bank(ctx.author,-1*amount,"wallet")
    await update_bank(ctx.author,amount,"bank")

    await ctx.send(f"You deposited {amount} credits!")


@client.command()
async def spend(ctx,amount,member:discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that many credits")
        return
    
    if amount<0:
        await ctx.send("Amount must be positive!")
        return
    
    await update_bank(ctx.author,-1*amount,"bank")
    await update_bank(member,amount,"bank")
    
    await ctx.send(f"You just bought something from {member} for {amount} credits")


@client.command()
async def send(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Please enter the amount")
        return
    
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that many credits!")
        return

    if amount<0:
        await ctx.send("Amount must be positive!")
        return

    await update_bank(ctx.author,-1*amount,"bank")
    await update_bank(member,amount,"bank")

    await ctx.send(f"You gave {amount} credits!")


@client.command()
async def slots(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return
    
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("You don't have that many credits!")
        return

    if amount<0:
        await ctx.send("Amount must be positive!")
        return

    final = []
    for i in range(3):
        a = random.choice(["X", "O", "Q"])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
        await update_bank(ctx.author,2*amount)
        await ctx.send("You won!")
    else:
        await update_bank(ctx.author,-1*amount)
        await ctx.send("You lost!")


async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json", "w") as f:
        json.dump(users,f)
    return True


async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json", "w") as f:
        json.dump(users,f)

    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal
    return True


@client.event
async def on_member_join(member):
    channel = client.get_channel(920843623967383613)
    await channel.send(f"{member} Has been welcomed to the government")


@client.command()
async def roll_dice(ctx):
    dice1 = random.randint(1, 6)
    await ctx.send(dice1)


@client.command(name='jm', pass_context=True)
async def jm(ctx):
    username = str(ctx.author).split('#')[0]
    user = await client.fetch_user("407036243138838529")
    await DMChannel.send(user, f"{username} Requests to join the mafia")
    await ctx.send("Your request is being processed please be patient and wait for further notice")


@client.command()
async def flip_coin(ctx):
    answer = ["Heads", "Tails"]
    hort = random.choice(answer)
    await ctx.send(hort)


client.run(token) 
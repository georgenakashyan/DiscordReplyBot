import asyncio
from distutils.log import error
import discord
from discord.ext import commands
import random
import json

#If running this on a RaspberryPi and it doesn't run on startup, uncomment this. It might need to wait for the networking to finish setting up.
#import time
#time.sleep(15)

#GO TO THE BOTTOM OF THE CODE AND INSERT YOUR BOT'S AUTH-ID FOR IT TO WORK.
#
#To Do:
#Add ability to get / set conditions to check for.
#Add profiles to make that easier ^^
#Generalize variable and method names
#Use Python Dictionaries to have multiple conditions.
#Fix page system for large outputs.
#
#v1.0

#Bot declaration.
client = commands.Bot(command_prefix="~")
client.remove_command("help")
chanceForER = 10
chanceForJoey = 10

#Startup
@client.event
async def on_ready():
  activity = discord.Game(name="~help for commands")
  await client.change_presence(status=discord.Status.online, activity=activity)
  print("AlanBot Running...")

#When a message is sent in any chat, it checks for multiple conditions and acts depending on what the message is.
@client.event
async def on_message(message):
  if message.author == client.user:
    return
  elif message.author.id == "235232787110559745" and random.randint(1, chanceForJoey) == 1:
    await message.channel.send(get_quote("JoeyQuotes.txt"))
  elif (("er" in message.content.lower()) and (random.randint(0, chanceForER) == 1)) or ("eternal return" in message.content.lower()):
    await message.channel.send(message.author.mention + " " + get_quote("AlanQuotes.txt"))
  await client.process_commands(message)

#New Member joining 
@client.event
async def on_member_join(ctx, member : discord.member):
  await ctx.send(member.mention + " " + get_quote("AlanQuotes.txt"))

#[===============]
# Normal Commands
#[===============]

#Help Command
@client.command()
async def help(ctx):
  await ctx.send("""**
[==================]
   Normal Commands:
[==================]
```
~addquote <alan/joey> "<Insert Quote Here>" -** Adds new responses.
**~quotelist <alan/joey> -** Prints a list of all quotes.
**~checkchance <alan/joey> -** Prints the chance for AlanBot to respond.
```**
[==================]
   Admin Commands:
[==================]
```
~delquote <alan/joey> <Insert Line Number Here> -** Removes a quote at a line number.
**~backup <alan/joey> -** Backs up the current list of quotes. **WARNING OVERWRITES BACKUP**
**~restore <alan/joey> -** Restores the current list of quotes from the backup. **WARNING OVERWRITES CURRENT**
**~backupquotelist <alan/joey> -** Sends a list of all the quotes in backup quotes.
**~changechance <Number greater than 1> -** Changes the chance of AlanBot responding to 1/input.
**~adminlist -** Lists all admin users by their userID.
**~addadmin -** Adds an person to bot admin role.
```""")

#Appends a new quote (Quote) to a new line in the file (alan or joey)
@client.command()
async def addquote(ctx, person : str, quote):
  try:
    fileN = fileName(person.lower(), "main")
    with open(fileN, "a") as f:
      f.write("\n" + quote)
    await ctx.send("Successfully added \"" + quote + "\" to " + fileN + ".")
  except:
    await ctx.send("Failed to add \"" + quote + "\" to " + person + "'s quotes. Please dm George the message you sent.")

#Outputs the entire quotelist for the person specified
@client.command()
async def quotelist(ctx, person : str):
  pages = 4
  cur_page = 1
  msg = discord.Message()
  await msg.send("Page " + str(cur_page) + "/" + str(pages) + ":\n") # + get_quote_page[person, cur_page]
  await msg.add_reaction("◀️")
  await msg.add_reaction("▶️")
  while True:
    try:
      reaction, user = await client.wait_for("reaction_add", timeout=60)
      if str(reaction.emoji) == "▶️":
        if cur_page == pages:
          cur_page = 1
        else:
          cur_page += 1
      elif str(reaction.emoji) == "◀️":
        if cur_page == 1:
          cur_page = pages
        else:
          cur_page -= 1
      await msg.edit(content=f"Page {cur_page}/{pages}:\n{get_quote_page[person, cur_page]}")
      await msg.remove_reaction(reaction, user)
    except asyncio.TimeoutError:
      await msg.delete()
      break

@client.command()
async def checkchance(ctx, person: str):
  if person.lower().contains("alan"):
    await ctx.send("The chance for me to respond to \"er\" is 1/" + str(chanceForER) + ".")
  elif person.lower().contains("joey"):
    await ctx.send("The chance for me to respond to \"joey\" is 1/" + str(chanceForJoey) + ".")
  else:
    await ctx.send("Incorrect syntax.")

#[===============]
# Admin Commands
#[===============]

#Deletes a specific line from the filename
@client.command()
async def delquote(ctx, person: str, ltd : str):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    try:
      fileN = fileName(person.lower(), "main")
      lineToDel = int(ltd)
      with open(fileN,'r') as read_file:
        lines = read_file.readlines()
      currentLine = 1
      with open(fileN,'w') as write_file:
        for line in lines:
          if currentLine != lineToDel:
            write_file.write(line)
          currentLine += 1
      await ctx.send("Successfully deleted line " + ltd + " from " + fileN + ".")
    except:
      await ctx.send("Failed to delete line " + ltd + " from " + person + "'s quote list.")
  else:
    await ctx.send("Only specific bot admins can use this command.")

#Replaces backup file with current.
@client.command()
async def backup(ctx, person : str):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    try:
      r_file = fileName(person.lower(), "main")
      w_file = fileName(person.lower(), "backup")
      with open(r_file, "r") as read_file:
        lines = read_file.readlines()
      with open(w_file, "w") as write_file:
        for line in lines:
          write_file.write(line)
      await ctx.send("Successful backup from " + r_file + " to " + w_file + ".")
    except:
      await ctx.send("Failed to backup " + r_file + " to " + w_file + ".")
  else:
    await ctx.send("Only specific bot admins can use this command.")

#Replaces current file with backup.
@client.command()
async def restore(ctx, person : str):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    try:
      r_file = fileName(person.lower(), "backup")
      w_file = fileName(person.lower(), "main")
      with open(r_file, "r") as read_file:
        lines = read_file.readlines()
      with open(w_file, "w") as write_file:
        for line in lines:
          write_file.write(line)
      await ctx.send("Successful restore from " + r_file + " to " + w_file + ".")
    except:
      await ctx.send("Failed to restore " + r_file + " to " + w_file + ".")
  else:
    await ctx.send("Only specific bot admins can use this command.")
#Outputs the entire quotelist for a backup file
@client.command()
async def backupquotelist(ctx, person : str):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    try:
      fileN = fileName(person.lower(), "main")
      with open(fileN, "r") as f:
        output = "[=========]" + fileN + "[=========]\n"
        count = 1
        for line in f:
          output += "Line " + str(count) + ": " + line.rstrip() + "\n"
          count += 1
      await ctx.send(output)
    except:
      await ctx.send("Failed to open " + person + "'s quote list.")
  else:
    await ctx.send("Only specific bot admins can use this command.")

#Changes the chanceForER variable for 1/num
@client.command()
async def changechance(ctx, person : str, num):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    chance = int(num)
    if person.lower().contains("alan"):
      if chance > 1:
        chanceForER = chance
        await ctx.send("Changed chance to 1/" + str(chanceForER) + ".")
      else:
        ctx.send("**Invalid input:** Input for checkchance cannot be < 1.")
    elif person.lower().contains("joey"):
      if chance > 1:
        chanceForJoey = chance
        await ctx.send("Changed chance to 1/" + str(chanceForJoey) + ".")
      else:
        ctx.send("**Invalid input:** Input for checkchance cannot be < 1.")
      return
  else:
    await ctx.send("Only specific bot admins can use this command.")

#Adds a person to bot admin role.
@client.command()
async def addadmin(ctx, id : str):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    try:
      with open("Admin.txt", "a") as f:
        f.write("\n" + id)
      await ctx.send("Successfully added " + id + " to Admin.txt.")
    except:
      await ctx.send("Failed to add " + id + " to Admin.txt. Please dm George the message you sent.")
  else:
    await ctx.send("Only specific bot admins can use this command.")

#Returns all admins on bot
@client.command()
async def adminlist(ctx):
  if checkID(ctx.message.author.id, "Admin") or checkID(ctx.message.author.id, "Creator"):
    try:
      with open("Admin.txt", "r") as f:
        output = "[=========]Admin.txt[=========]\n"
        count = 1
        for line in f:
          output += "Line " + str(count) + ": " + line.rstrip() + "\n"
          count += 1
      await ctx.send(output)
    except:
      await ctx.send("Failed to open Admin.txt list.")
  else:
    await ctx.send("Only specific bot admins can use this command.")
#[===============]
# Internal Commands
#[===============]

#Returns the correct file name for the person and their main or backup quote list
def fileName(person, file):
  if person == "alan":
    if file == "main":
      return "AlanQuotes.txt"
    elif file == "backup":
      return "AlanQuoteBackup.txt"
  elif person == "joey":
    if file == "main":
      return "JoeyQuotes.txt"
    elif file == "backup":
      return "JoeyQuoteBackup.txt"
  else:
    return "error"

#Checks for a list of ID's and permissions
def checkID(personID, role):
  ID = str(personID)
  if role == "Creator" and ID == "226710459766669312":
    return True
  elif role == "Admin":
    with open("Admin.txt","r") as f:
      lines = f.readlines()
    for l in lines:
      if l == ID:
        return True
  return False

#Returns a random quote from a random line in the file under the name of fileName
def get_quote(fileName):
  with open(fileName, "r") as f:
    lines = f.readlines()
    output = lines[random.randint(0, len(lines)-1)]
  return output

#Returns contents of a specific page in a quotelist
def get_quote_page(person, pageNum):
  try:
    output = ""
    fileN = fileName(person.lower(), "main")
    beginLine = (pageNum * 5) - 4
    with open(fileN, "r") as f:
      quotes = ""
      count = 1
      for line in f in range(beginLine, beginLine + 5):
        f.seek(beginLine)
        quotes += "Line " + str(count) + ": " + line.rstrip() + "\n"
        count += 1
    return quotes
  except:
    return "Failed to get page " + str(pageNum) + "."

client.run("") #<--ENTER YOUR BOT'S AUTH-ID IN HERE

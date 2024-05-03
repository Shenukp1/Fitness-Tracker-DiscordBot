
import discord
from discord.ext import commands, tasks
import datetime 
from datetime import date
from datetime import datetime
import json
import asyncio
import re
from text import G_CHANNEL_ID, R_CHANNEL_ID
#UTILITES - AKA extra functions used



#validates time in a specific format
def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False
    
#Check if its a valid date
def is_valid_date(dateTime_str): #make this into a function that checks all formats
    
    try:

        datetime.strptime(dateTime_str, "%d/%m/%Y")
        
        return True
    except ValueError:
        return False


def Reminded(c_Date): #remind you and removes previous reminders
    today = date.today()
    today_Date = today.strftime("%d/%m/%Y")
    with open('reminder.json', 'r') as file:
        data = json.load(file)
        if c_Date == today_Date:
            
            count = data[today_Date]["count"]
            int_count = int(count)

            if int_count == 0:   
                del data[today_Date]
                with open('reminder.json', 'w') as file:
                    json.dump(data, file)
            else:
                int_count = int_count - 1
                str_count = str(int_count)
                data[today_Date]["count"] = str_count
                with open('reminder.json', 'w') as file:
                    json.dump(data, file)
        
        
#remove any reminder that are out of date
def removeReminder(): 
    today = date.today()
    today_Date = today.strftime("%d/%m/%Y")
    with open('reminder.json', 'r') as file:
        data = json.load(file)

        try:
            for day in data:
                if day <= today_Date:
                    #data = json.load(file)
                    del data[day]
                    with open('reminder.json', 'w') as file:
                        json.dump(data, file)
        except:
            pass            
        

#saving the reminder data   
def save_reminder(reminder_date, reminder,time_str,count):
    print(reminder_date,"date")
    print(reminder,"date")
    print(time_str,"date")
    print(count,"date")

    try:
        with open('reminder.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}  # Initialize empty dictionary if file not found or has invalid content

    # Add new data
    data[reminder_date] = {"reminder": reminder, "time": time_str, "count": count}

    # Write updated data back to the file
    with open('reminder.json', 'w') as file:
        json.dump(data, file)


def load_reminder(today_Date):#if i use todays date. then the try catch should not crash function 
    try:
        with open('reminder.json', 'r') as file:
            data = json.load(file)
        if today_Date in data:
            return data[today_Date]["reminder"],data[today_Date]["time"]   
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None,None#i think it will be none
        

#==============Setup=================

USER_PROTEIN_INTAKE = 150 #this can be changed 
user_protein = {}#dictionary to remember user and their protien intake

def setup_commands(client):
    
    @client.event
    async def on_ready():
        starting = client.get_channel(R_CHANNEL_ID)
        
        await starting.send("Hello friend! I am a reminder bot. Type:!help1 to see my commands")
        print(f'{client.user} is now running!')

        #constantly checks Reminder and protien
            #add more checker if needed.
        while True:
            await check_protien()
            await check_reminder()
            await asyncio.sleep(5)
    #CREATE A WAY TO REMOVE REMINDERS BY USER/CHECK REMINDERS TOO/DISPLAY REMINDERS WHEN NEW ONE IS ADDED


   
    #Checks reminder constantly to see if there is a reminder today
    async def check_reminder():
        channel = client.get_channel(R_CHANNEL_ID)
        today = date.today()
        now = datetime.now()
        today_Date = today.strftime("%d/%m/%Y")
        print(today_Date)#seeing the user input

        reminder, r_time = load_reminder(today_Date)#will give us either reminder/date or none

        try:
            r_Hour, r_time = r_time.rstrip(":")
            r_Hour = int(r_Hour)
            r_time = int(r_time)
            if (reminder != None) and (now.hour >= r_Hour) and (now.minute >= r_Hour):
                await channel.send(f"today is {today_Date}, and its {r_Hour}:{r_time}. this is your reminder:{reminder}")
            #then remove the date and reminder. i dont think i need a try and catch because the if statement checks
                Reminded(today_Date)
        except:
            pass
        
    #Function that check protien consumtion within time interval.
        #if protien consumtion does not meet what is required within the time interval. bot will message user to have protien        
    async def check_protien():
        now = datetime.now()
        formated_now = now.strftime("%H:%M")
        print(f"time is: {formated_now}")
        channel = client.get_channel(G_CHANNEL_ID)  # Replace YOUR_CHANNEL_ID with the ID of the channel you want to send a message to

        #TODO could add a way to figure out if you will hit optimal protien intake
        
        #Time Interval for protien intake checks. 
        time_IntervalP = {
            ("10:00","12:00"):20,
            ("14:00","15:00"):40,#2pm -3pm
            ("17:00","18:00"):60,
            ("19:00","20:00"):80,#7pm -8pm
            ("21:00","22:00"):100,
            ("00:00","01:00"):150,
        }
        for (start,end),req_protien in time_IntervalP.items():
            print(start,end)
            if (start <= formated_now <= end ):
                    print("HERE")

                    for user_id, protein in user_protein.items():# is this BAD PRACTICE
                        print("Hello",user_id,protein)
                        
                        if(protein < req_protien):
                            diffProtien = req_protien - protein
                            user_id = int(user_id)
                            user = await client.fetch_user(int(user_id))
                            await channel.send(f"{user.mention}, Reminder: You have only consumed {protein}g of protein today. Try to eat {diffProtien}g more!")
                            await asyncio.sleep(1)
                               

    #Help Command - used to list all the 
    @client.command()
    async def help1(ctx):
        helpInstructions = [
            "1.!checkProtein will tell you your current protein intake",
            "2.!protein is how can input the protein intake.",
            "3.!remind is your remind command.the format for remind is(note '|' is used to seperate): !remind your reminder | dd/mm/yyyy | 00(hour):00(mins)(note: times in 24 hour clock) | count(how many times its repeated) "
            
            
            ]
        
        for help in helpInstructions:
            await ctx.send(help)


    #Shows all the reminders that have been saved
    @client.command()
    async def showR(ctx):
        with open('reminder.json', 'r') as file:
            data = json.load(file)
            for reminder_date, info in data.items():
                new_reminder_date = reminder_date
                reminder = info["reminder"]
                time_str = info["time"]
                count = info["count"]
                await ctx.send(f"Reminder Date: {reminder_date}  Reminder: {reminder}  Time: {time_str}  Count: {count}")


    #allows user to remove a reminder 
    #TODO Issue: goes into except
    @client.command()
    async def removeR(ctx,*,dateOfReminder):
        today = date.today()
        today_Date = today.strftime("%d/%m/%Y")
        print("hello: "+dateOfReminder)
        try:
            with open('reminder.json', 'r') as file:
                data = json.load(file)
                for day in data:
                    if day == dateOfReminder:
                        del data[day]
                        with open('reminder.json', 'w') as file:
                            json.dump(data, file)

    

        except:
            await ctx.send(f"whooopse something went wrong!")


    #checking protein intake BY USER
    @client.command()
    async def checkProtein(context):
        #get the user who did this command
        user_id = context.author.id  # Get the user's ID
        protein = user_protein.get(user_id, 0)  # Retrieve the protein value for this user, default to 0 if not found
        await context.send(f"You have consumed {protein}g of protein today.")

    
    #To add protien consumed
    @client.command()
    async def protein(ctx, amount: int):
        print(f"Received command: protein {amount}")
        user_id = ctx.message.author.id

        if user_id in user_protein:
            user_protein[user_id] += amount
            
            await ctx.send(f"You've consumed {user_protein[user_id]}g of protein today.")

        else:#adding amount of protein intake for the first time
            user_protein[user_id] = amount
            await ctx.send(f"You've consumed {user_protein[user_id]}g of protein today.")

        if user_protein[user_id] >= 150:
            await ctx.send("You've reached your protein goal for today! Good job!")


    #reminder maker
    #help command for all the commands in this bot
    #TODO need to make sure you cant add anything before a certain time
    @client.command() 
    async def remind(ctx,*,dateTime):
        #count will be how many times the reminder will repeat until it is deleted 
        today = date.today()
        today_Date = today.strftime("%d/%m/%Y")
        print(today_Date)#seeing the user input
        
        try:
            reminder, dateTime_str, time, count = dateTime.rsplit("|")
            dateTime_str = dateTime_str.strip()
            time_str = time.strip()
            count = count.strip()


            if is_valid_date(dateTime_str) and (is_valid_time(time_str) == True) and (dateTime_str >= today_Date):
                await ctx.send(f"we will remind you to: {reminder},@ date: {dateTime_str} @time: {time_str}")

                save_reminder(dateTime_str,reminder,time_str,count) #save reminder here
            else:
                await ctx.send("make sure the format is: day/month/year")
        except: 
            await ctx.send("this is the format: reminder | day/month/year | 00:00 | x(x is can be any number of time you want to repeat this reminder)")
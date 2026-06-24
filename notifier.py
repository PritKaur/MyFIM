import winotify #Imports the winotify library
from winotify import Notification, audio #Notification class builds the popup and audio is for the notification sound

#This function will fire a Windows toast notification that will be displayed & able to be clicked by the user when a file change is detected
#It is the function that will be called by monitor.py
def send_alert(file_name, change_type): #Takes the name of file and type of change 
    toast = Notification( #This builds the notification body itself
        app_id="MyFIM", #A label windows uses to see which app sent the notification
        title="File Integrity Monitoring Alert", #Header of the popup
        msg=f"File: {file_name}\nChange detected: {change_type}\n\nClick to view more details about the file change on the dashboard.", #The body of the popup
        duration="long" #Tells windows to keep the notification visible for long
    )
    #Attaches a sound to the notification
    toast.set_audio(audio.Default, loop=False) #loop=false means that the sound only plays once

    #Adds a clickable button to the notification
    toast.add_actions(label="Open Dashboard", launch="http://localhost:5000/login")

    toast.show() #This is what triggers the notification to make it appear on the user's screen
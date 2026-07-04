import winotify #Imports the winotify library
from winotify import Notification, audio #Notification class builds the popup and audio is for the notification sound
import smtplib #Used to connect to Gmail's SMTP server and send the email
import threading #Used to send the email in the background so it doesn't block monitor.py
from email.mime.text import MIMEText #Builds the plain-text email message

#Email settings are imported from email_config.py, which is gitignored and holds the real credentials
#If that file doesn't exist (e.g. on a fresh clone from GitHub), email alerts are disabled rather than crashing
try:
    from email_config import SENDER_EMAIL, APP_PASSWORD, RECIPIENT_EMAIL
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False

#This function sends the alert to the admin's email as a second, independent channel
#It's called from inside send_alert() so every alert automatically triggers both channels
def send_email_alert(file_name, change_type):
    #This inner function is what actually runs on the background thread
    def _send():
        if not EMAIL_ENABLED: #Skips silently if email_config.py wasn't found
            return
        try:
            msg = MIMEText(
                f"File Integrity Monitoring Alert\n\n"
                f"File: {file_name}\n"
                f"Change detected: {change_type}\n\n"
                f"Check the dashboard for more details: http://localhost:5000/login"
            )
            msg["Subject"] = f"MyFIM Alert: {change_type} - {file_name}"
            msg["From"] = SENDER_EMAIL
            msg["To"] = RECIPIENT_EMAIL

            #SMTP_SSL connects securely to Gmail's mail server on port 465
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)

            print(f"Email alert sent for {file_name}")

        #Broad except here because failure could be a bad password, no internet, Gmail rate-limiting, etc
        #This must never raise, since it runs unattended on a background thread
        except Exception as e:
            print(f"Could not send email alert for {file_name}: {e}")

    #daemon=True means this thread won't stop the program from exiting if it's still running
    threading.Thread(target=_send, daemon=True).start()

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

    #Fires the email alert as a second, independent channel alongside the desktop toast
    send_email_alert(file_name, change_type)

#Just to test if notifier.py actually works on its own as a script
if __name__ == "__main__":
    import time
    send_alert("test_file.txt", "Modified")
    time.sleep(5) #Keeps the script alive briefly so the background email thread has time to finish and print its result
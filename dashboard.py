from flask import Flask, jsonify, session, request, redirect, render_template
import json
import os
from baseline import load_decrypted_baseline

#This creates the web application, the dashboard
app = Flask(__name__) 

#This is the password that Flask will use to encrypt the session cookie that is stored in the user's browser
app.secret_key = "flask_secret_key" #Sessions will break if this key is not there 

#These are the login credentials for the dashboard
username = "admin"
password = "adminpass"

#This will tell the dashboard where to get the alert data from, the data that is generated in monitor.py
alerts_file = "alerts.json"

#This is the login route and it handles two scenarios (GET and POST)
@app.route('/login', methods=['GET', 'POST'])#This function handles when someone visits the login page (GET) and when they enter the login details (POST)
def login():
    error = None #Error is set to none meaning there is no error to show yet 

    #This if block will be skipped if it's a GET request, meaning the user has just visited the /login page on their browser
    if request.method == 'POST':
        username_entered = request.form['username'] #Grabs the username that was typed in the field
        password_entered = request.form['password'] #Grabs the password that was typed in the field

        if username_entered == username and password_entered == password: #The entered username and password are compared with the stored credentials
            #This session part sets a flag in the session when a login is successful and every protected route will check for this before granting the user access
            session['logged_in'] = True #Credentials match
            return redirect('/dashboard') #User is sent to the dashboard page
        else:
            error = "Username or password entered was incorrect. Please try again!"
    
    return render_template('login.html', error=error)

#This is the logout route and it clears the user session, redirecting the user back to the login page
@app.route('/logout')#No GET/POST is needed here since logout will just be triggered by visiting the /logout URL
def logout():
    session.clear() #This will remove the session flag, meaning delete everything that's stored in the session
    return redirect('/login') #This will send the user back to the login page

#This is the dashboard route and it's a protected route
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: #If the user has not logged in
        return redirect('/login') #Takes them back to the login page
    return render_template('dashboard.html') #If the user has logged in the dashboard will be loaded and shown to the user

#This is the API alerts route
@app.route('/api/alerts')
def alerts():

    #If the user hasn't logged in they will be redirected to the login page again
    if 'logged_in' not in session:
        return redirect('/login')
    
    #If the alerts file doesn't exist, an empty list will be returned to avoid the program crashing
    if not os.path.exists(alerts_file): #Monitor.py needs to run for this file to exist
        return jsonify([])
    
    try:
        with open(alerts_file, 'r') as f: #Opens the file in read mode
            data = json.load(f) #Converts the JSON strings into a python list
        return jsonify(data) #Converts the list back to JSON format and sends it as a HTTP response to the web browser that the javascript can actually read
    except (json.JSONDecodeError, OSError): #Catches errors like JSON in the file being corrupted or the file is not being able to be read
        return jsonify([]) #Returns an empty list to avoid the program crashing
    
#This is the API monitored files route which returns the list of the file paths being monitored 
@app.route('/api/monitored-files')
def monitored_files():
     #If the user hasn't logged in they will be redirected to the login page again
    if 'logged_in' not in session:
        return redirect('/login')
    
    try:
        baseline = load_decrypted_baseline() #Decrypts and loads the baseline dictionary
        file_list = list(baseline.keys()) #Extracts the file paths of the files being monitored
        return jsonify(file_list) #Sends the list of the file paths back to JSON
    except (FileNotFoundError, OSError): #Catches errors like the file not being found or not being able to be read 
        return jsonify([]) #Returns an empty list to avoid the program crashing

#Only runs when I execute this script directly, it won't run when another script imports from this script
if __name__ == "__main__":
    #The user_reloader=False turns off the file watcher (watchdog) which was causing a reloading loop when I ran this file directly
    app.run(debug=True, use_reloader=False) 
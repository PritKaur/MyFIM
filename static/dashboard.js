//This function loads the list of the files being monitored 
async function loadMonitoredFiles(){
    try{
        //Asks the server for the list of files 
        const response = await fetch('/api/monitored-files') //fetch sends a GET request to the Flask routes in dashboard.py
        const files = await response.json(); //Parses the HTTP response body as a JSON array

        //Finds the table on the page and wipes it clean because it runs every 5 seconds so if it's not celared, there would be duplicate rows each time 
        const tbody = document.getElementById('monitoredFilesBody'); //Grabs the <tbody> element from dashboard.html
        tbody.innerHTML = '';

        //For each file, the file name is extracted by removing the folder part like C:\Users\prita\OneDrive - Strathmore University\Desktop
        files.forEach(filePath =>{ //Loops over every file path string
            const fileName = filePath.split('\\').pop().split('/').pop(); //Splits on backslash and takes the last segment for windows style paths and the / does the same cause my backend normalizes file paths
            const  row = document.createElement('tr'); //Creates a new <tr> element (table row)
            //This will build a table row for every file
            row.innerHTML = `
                <td><strong>${fileName}</strong></td>
                <td class = "filepath">${filePath}</td> 
            `;
            tbody.appendChild(row); //Row is  added to the table 
        });
        document.getElementById('totalFiles').textContent = files.length; //Shows how many files are being monitored (Total Files summary card at the top of the dashboard page)
    } catch (error){
        console.error('Failed to load the monitored files: ', error); //The error is printed to the browser console in case anything goes wrong so that the page doesn't crash
    }
}

//Loads the alert logs from alerts.json
async function loadAlerts() {
    try{
        //Asks the server for the list of file change alerts 
        const response = await fetch('/api/alerts');
        const alerts = await response.json();

        //Clears the alerts table 
        const tbody = document.getElementById('alertsBody');
        tbody.innerHTML = '';

        //Makes a flipped copy of the alerts list so that the newest alert shows up at the top
        const reversedAlerts = [...alerts].reverse(); //Copies the array first so it doesn't mess up the original order

        //Builds one row per file alert
        reversedAlerts.forEach(alert => {
            const row = document.createElement('tr');
            //row with four cells: file name, path, type of change, when the change happened 
            row.innerHTML = `
                <td><strong>${alert.file}</strong></td> 
                <td class = "filepath">${alert.path}</td> 
                <td class = "text-danger">${alert.change_type}</td>
                <td>${alert.timestamp}</td> 
                `;
                tbody.appendChild(row);
        });
        //The summary cards at the top of the page are updated
        document.getElementById('totalAlerts').textContent = alerts.length;
        document.getElementById('totalModified').textContent = alerts.filter(a => a.change_type === 'Modified').length;
        document.getElementById('totalDeleted').textContent = alerts.filter(a => a.change_type === 'Deleted').length;
    } catch (error){
        console.error('Failed to load the alerts: ', error); //The error is printed to the browser console in case anything goes wrong so that the page doesn't crash
    }
}

//Both functions are ran immediately the page loads 
loadMonitoredFiles();
loadAlerts();

//The functions repeat every 5 seconds so the dashboard refreshes automatically 
setInterval(loadAlerts, 5000);
setInterval(loadMonitoredFiles, 5000);

//This waits for the page to fullu load, then looks for the logout button
document.addEventListener('DOMContentLoaded', function(){ //Waits for the full HTML document to be parsed before touching the DOM
    const logoutButton = document.querySelector('.logout-button');
    if (logoutButton) { //If there is a logout button
        logoutButton.addEventListener('click', function(){ //When a user clicks on it
            window.location.href = '/logout'; //Sends the user to /logout route which logs them out and sends them to the login page again
        });
    }
});
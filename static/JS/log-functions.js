
import { tp } from './timepicker.js';
import { processLogChart, generateDoughnutChart } from './chart.js';

function formatTime(timeStr) {
    let hours = parseInt(timeStr.substring(0, 2), 10);
    let minutes = parseInt(timeStr.substring(2, 4), 10);
  
    return `${hours} hour ${minutes} minutes`;
  }
  
  function convertTimeToDecimal(timeStr) {
    let hours = parseInt(timeStr.substring(0, 2), 10);
    let minutes = parseInt(timeStr.substring(2), 10);
  
    // Convert minutes to a fraction of an hour
    let hoursDecimal = minutes / 60;
    let totalHours = hours + hoursDecimal;
  
    return totalHours;
  }
  
  function showPopup(time){
    const message = "Logged: " + formatTime(time);
            const popup = document.createElement("div");
  
            // Set the style for the floating popup
            popup.style.position = 'fixed';
            popup.style.top = '20px';
            popup.style.right = '20px';
            popup.style.zIndex = '1000';
            popup.style.padding = '10px';
            popup.style.backgroundColor = 'green';
            popup.style.border = '1px solid black';
            popup.style.borderRadius = '5px';
  
            // Set the message for the popup
            popup.textContent = message;
  
            // Add the popup to the body
            document.body.appendChild(popup);
  
            // Remove the popup after 3 seconds
            setTimeout(() => {
                document.body.removeChild(popup);
            }, 3000);
  
  }
  
  function showTimeExceededPopup() {
    const message = "Error: Total log time for a day cannot exceed 24 hours.";
    const popup = document.createElement("div");

    // Set the style for the floating popup
    popup.style.position = 'fixed';
    popup.style.top = '20px';
    popup.style.right = '20px';
    popup.style.zIndex = '1000';
    popup.style.padding = '10px';
    popup.style.backgroundColor = 'red'; // Changed color to red for error
    popup.style.color = 'white'; // Text color set to white for contrast
    popup.style.border = '1px solid darkred';
    popup.style.borderRadius = '5px';
    popup.style.boxShadow = '0px 4px 6px rgba(0, 0, 0, 0.1)'; // Optional: added some shadow for better visibility

    // Set the message for the popup
    popup.textContent = message;

    // Add the popup to the body
    document.body.appendChild(popup);

    // Remove the popup after 5 seconds
    setTimeout(() => {
        document.body.removeChild(popup);
    }, 5000);
}

function checkTotalLogHoursForDay(record) {
    const requestData = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ date: record.date })
    };

    return fetch('/get_total_log_hours_per_day', requestData)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Total log hours for the day:', data, 'Total : ', data.total_hours + record.log_hour);
            var total = data.total_hours + record.log_hour;
            if (total > 24) {
                return true; // Time exceeds 24 hours
            }
            return false; // Time does not exceed 24 hours
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
            return false; // Handle error case as time does not exceed 24 hours
        });
}

  
  function writeToDB(username, record) {
    if(!username) {
        return Promise.reject(new Error("No username provided"));
    }
    const table_name = 'user_' + username;
    return fetch('/write_record', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            table: table_name, 
            record: record      
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        return data;  // Return the data to chain the promise
    })
    .catch(error => {
        console.error('Error:', error);
        return Promise.reject(error);  // Return the error to chain the promise
    });
  }
  
  
  function refreshData() {
    fetch('/get_user_data')
        .then(response => response.json())
        .then(data => {
            console.log('data ---', data);
            if (Array.isArray(data)) {
                const today_date = new Date() //.toISOString().split('T')[0];
                var today = 'Y-mm-dd'
                    .replace('Y', today_date.getFullYear())
                    .replace('mm', (today_date.getMonth() + 1).toString().padStart(2, '0')) // Pad month
                    .replace('dd', today_date.getDate().toString().padStart(2, '0')); // Pad day

                let totalMinutesToday = 0;
                let totalMinutes = data.reduce((acc, row) => {
                    // Assuming 'row' is an array with log_hour at index 1 and date at index 2
                    let logHour = parseFloat(row[1]);
                    let logDate = row[3].split('T')[0]; // Adjust if your date format is different
                    // console.log('Today ',today, logDate)
                    if (logDate === today) {
                        totalMinutesToday += logHour * 60;
                    }
  
                    return acc + (logHour * 60);
                }, 0);
  
                // Convert total minutes back into days, hours, and minutes for the total log time
                let days = Math.floor(totalMinutes / (24 * 60));
                totalMinutes %= (24 * 60);
                let hours = Math.floor(totalMinutes / 60);
                let minutes = totalMinutes % 60;
  
                // Convert total minutes today into hours and minutes for today's log time
                let todayHours = Math.floor(totalMinutesToday / 60);
                let todayMinutes = totalMinutesToday % 60;
  
                // Update the total log time div
                const logtimeDiv = document.querySelector('.logtime');
                logtimeDiv.textContent = `Total log time ⌛: ${days} day, ${hours} hrs, ${minutes} mins`;
  
                // Update today's log time div
                const todayTimeDiv = document.querySelector('.progress-amount');
                todayTimeDiv.textContent = `⏰ ${todayHours} hrs, ${todayMinutes} mins`;
            }
        })
        .catch(error => console.error('Error fetching user data:', error));
  }
  
  
  function fetchAndDisplayRecords() {
    fetch('/get_recent_records')
        .then(response => response.json())
        .then(data => {
            const recordsContainer = document.getElementById('recent-records-container');
            recordsContainer.innerHTML = ''; // Clear existing entries
  
            data.forEach(record => {
                const row = recordsContainer.insertRow();
                const logIdCell = row.insertCell(0);
                const logHourCell = row.insertCell(1);             
                const infoCell = row.insertCell(2);
                const dateCell = row.insertCell(3);
                const deleteCell = row.insertCell(4);
  
                logIdCell.textContent = record[0];
                logHourCell.textContent = parseFloat(record[1]).toFixed(2); // Keep 2 decimal places
                infoCell.textContent = record[2];
                dateCell.textContent = new Date(record[3]).toLocaleString(); // Convert to readable date
  
                 // Create a delete button
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.onclick = function() { deleteRecord(record[0]); };
                deleteCell.appendChild(deleteButton);
            });
        })
        .catch(error => {
            console.error('Error fetching recent records:', error);
        });
  }
  
  function deleteRecord(logId) {
    if (confirm(`Are you sure you want to delete log ID ${logId}?`)) {
        fetch(`/delete_record/${logId}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                console.log('Delete response:', data);
                refreshData();
                fetchAndDisplayRecords(); // Refresh the list of records after deletion
                processLogChart();
                generateDoughnutChart();
            })
            .catch(error => console.error('Error deleting the record:', error));
    }
  }
  
  document.addEventListener("DOMContentLoaded", () => {


    refreshData();
    fetchAndDisplayRecords();
    processLogChart();
    generateDoughnutChart();
    tp.init(); // Initialize the time picker

    const logButton = document.getElementById('tp-set');
    logButton.addEventListener('click', () => tp.set());
    const closeButton = document.getElementById('tp-close');
    closeButton.addEventListener('click', () => tp.hwrap.classList.remove('show'));
    const tuneButton = document.getElementById('tuneButton');
    let tune = false; // Initialize the tune variable
    const defaultColor = tuneButton.style.backgroundColor;
  
    tuneButton.addEventListener('click', () => {
        tune = !tune; 
        tuneButton.style.backgroundColor = tune ? '#ffffff15'  : defaultColor;
        tuneButton.textContent = tune ? 'Tuned' : 'Tune';
        generateDoughnutChart(); 
    });
    

    const username = document.getElementById('user_id') ? document.getElementById('user_id').value : null;
    if(!username){
      window.location.href = '/logout';
    }
    tp.attach({
        target: document.getElementById("addLog"), // The current "+" button
        "24": true, // Use 24-hour format
        after: time => {
          const now = new Date();
          
          var info = document.getElementById("tp-info").value
          var date = document.getElementById("tp-date").value
          document.getElementById("tp-info").value = "";


  
        //   console.log('got time ===> ', convertTimeToDecimal(time), time, info,  now, date)
          
          const record = {'log_hour': convertTimeToDecimal(time), 'info': info, 'date' : date || now }
          checkTotalLogHoursForDay(record).then(exceeds => {
            if (exceeds) {
                showTimeExceededPopup();
                return false;
            }
            else{
                writeToDB(username, record)
                .then(() => {
                    // Now refreshData will be called after the data has been successfully written
                    refreshData();
                    fetchAndDisplayRecords();
                    processLogChart();
                    generateDoughnutChart();
                })
                .catch(error => {
                    console.log('Error writing to DB:', error);
                });
            
                showPopup(time);
            }

          });
        }
    });
  });
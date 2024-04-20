import { processLogChart } from './chart.js';

function logoutUser() {
    // Here you can add any logout logic you need, like clearing session storage, etc.
    sessionStorage.clear();
    history.pushState(null, null, null);
    window.addEventListener('popstate', function () {
      // Handle the back button event and prevent going back to dashboard
      history.pushState(null, null, null);
    });
    // Redirect to index.html
    window.location.href = '/logout';
  }

document.addEventListener('DOMContentLoaded', function() {
    // Set the initial visibility state
    setInitialVisibility();

    // Menu item click events
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            // Remove 'active' class from all menu items
            document.querySelectorAll('.menu-item').forEach(innerItem => {
                innerItem.classList.remove('active');
            });

            // Add 'active' class to the clicked item
            this.classList.add('active');

            // Toggle the visibility based on the clicked menu item
            toggleVisibility(this.id);
        });
    });
});

function setInitialVisibility() {
    const todayProgressBox = document.querySelector('.today-progress-box');
    const studyLogBox = document.querySelector('.study-log-box');
    const historyLogBox = document.getElementById('history-box')
    const historyLogCircle = document.getElementById('history-circle')

    console.log(todayProgressBox, studyLogBox, historyLogBox)

    todayProgressBox.style.display = 'block'; // Show the today-progress-box
    studyLogBox.style.display = 'none'; // Hide the study-log-box
    historyLogBox.style.display = 'block';
    historyLogCircle.style.display = 'none';
}

function toggleVisibility(clickedId) {
    const todayProgressBox = document.querySelector('.today-progress-box');
    const studyLogBox = document.querySelector('.study-log-box');
    const historyLogBox = document.getElementById('history-box')
    const historyLogCircle = document.getElementById('history-circle')

    // Hide all elements initially
    todayProgressBox.style.display = 'none';
    studyLogBox.style.display = 'none';
    historyLogBox.style.display = 'none';
    historyLogCircle.style.display = 'none';

    // Show the relevant element based on clickedId
    if (clickedId === 'logging') {
        studyLogBox.style.display = 'block';
    } else if (clickedId === 'dashboard') {
        todayProgressBox.style.display = 'block';
        historyLogBox.style.display = 'block';
    } else if (clickedId === 'ai_analysis') {
        historyLogCircle.style.display = 'block';
    } else if (clickedId === 'logout') {
        logoutUser();
    }
}





  window.onload = function() {

    if (window.history && window.history.pushState) {
        window.history.pushState('forward', null, './#forward');
        window.onpopstate = function(event) {
            if (event.state && event.state === 'forward') {
                window.location.href = '/'; // Redirect to the home page or login page
            }
        };
    }

    for (var i = 1; i <= 24; i++) {
        if (i !== 6) { // Skip the default value to avoid duplicate
            var opt = document.createElement('option');
            opt.value = i;
            opt.innerHTML = i;
            document.getElementById('number-select').appendChild(opt);
        }
    }

    for (var i = 1; i <= 100; i++) {
        if (i !== 15) { // Skip the default value to avoid duplicate
            var opt = document.createElement('option');
            opt.value = i;
            opt.innerHTML = i;
            document.getElementById('days-select').appendChild(opt);
        }
    }

    function handleSelectChange() {
        var daysSelect = document.getElementById('days-select');
        processLogChart(daysSelect.value || 15).then(average => {
            console.log('average -->', average);
        });
    }
    
    // IDs of select elements to attach the onchange event
    var selectIDs = ['number-select', 'days-select'];
    
    // Attach the event handler to each select element found by ID
    selectIDs.forEach(id => {
        var selectElement = document.getElementById(id);
        if (selectElement) {
            selectElement.onchange = handleSelectChange;
        }
    });
    
    
};



  
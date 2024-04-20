function getColorForValue(hour, targetLog) {
  if (hour >= targetLog) {
    return 'rgba(75, 192, 192, 0.2)';
  } else if (hour >= (targetLog / 2) && hour < targetLog) {
    return 'rgba(54, 162, 235, 0.2)';
  } else {
    return 'rgba(255, 99, 132, 0.2)';
  }
}

function generateColorArray(categoryCount) {
  const colorArray = [];
  const hueStep = 360 / categoryCount; // Divide the color wheel into equal parts based on the number of categories

  for (let i = 0; i < categoryCount; i++) {
      // Generate a hue value, keeping saturation and lightness constant
      // Adjust the saturation and lightness values to match your preferred color tone
      const hue = i * hueStep;
      colorArray.push(`hsla(${hue}, 70%, 70%, 0.2)`);
  }

  return colorArray;
}
            
              
async function getUserData() {
    try {
      const response = await fetch('/get_user_data');
  
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`); // Use template literal for cleaner string formatting
      }
  
      const data = await response.json();
      // console.log('-----return-------',data)
      return data;
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
      return null;
    }
  }
  
  function processDataForChart(userData, limit=15) {
    const today = new Date();
    const lastLimitDays = [];
    const dateHoursMap = {};
  
    // Generate labels for the last Limit days
    for (let i = 0; i <= limit; i++) { // Start from 0 for better date calculations
      const pastDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i);
      const label = `${pastDate.getDate()} ${pastDate.toLocaleString('default', { month: 'short' })}`;
      lastLimitDays.push(label);
      dateHoursMap[label] = 0;
    }
  
    // Loop through user data, summing hours for each date
    userData.forEach(record => {
      const date = new Date(record[3]); // Assuming date is at index 3
      const label = `${date.getDate()} ${date.toLocaleString('default', { month: 'short' })}`;
  
      if (lastLimitDays.includes(label)) {
        dateHoursMap[label] += record[1]; // Assuming hours are at index 1
      }
    });
  
    return { labels: Object.keys(dateHoursMap).reverse(), logHours: Object.values(dateHoursMap).reverse() };
  }
  
  async function retrieveData(immediateReturn=false, limit=15) {
    // console.log("log", immediateReturn, limit)
    try {
      const userData = await getUserData();
      if(immediateReturn)
      {
        console.log('-----------return raw',userData)
        return userData;
      }
      if (userData) {
        const chartData = processDataForChart(userData, limit);
        return chartData; // Return the processed data
      } else {
        console.error('No user data returned');
        return { labels: [], logHours: [] }; // Return empty data on no user data
      }
    } catch (error) {
      console.error('Error retrieving data:', error);
      return { labels: [], logHours: [] }; // Return empty data on error
    }
  }
  
  export async function processLogChart(limit=15) {
    const canvas = document.getElementById('myChart');
    const ctx = canvas.getContext('2d');

  
    try {
      // Retrieve data with optional error handling
      const { labels, logHours } = await retrieveData(false, limit);
      var total = logHours.reduce((partialSum, a) => partialSum + a, 0);
      total = parseFloat((total / limit).toFixed(2));
      console.log("lohggg",total, limit)
     
       // Get the selected target log value
      const targetLog = parseInt(document.getElementById('number-select').value, 10);

      // Map the logHours to their colors based on the selected target log
      const backgroundColors = logHours.map(hour => getColorForValue(hour, targetLog));

      console.log(targetLog, backgroundColors);
      // Check if a chart already exists
      const existingChart = Chart.getChart('myChart');
  
      // Destroy existing chart if necessary
      if (existingChart) {
        existingChart.destroy();
        console.log('destroyeddd')
      }
  
      // Create a bar chart with updated data
      const chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: `Avg Log ${limit}D ::  ${total} Hours`,

            data: logHours,
            backgroundColor: backgroundColors,
            borderColor: backgroundColors.map(color => color.replace('0.2', '1')),
            borderWidth: 1,
          },],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });


      return total;

      
    } catch (error) {
      console.error('Error creating chart:', error);
    }
  }
  

  async function processUserData(tune=false) {
    try {
      const response = await fetch(`/process_user_data?tune=${tune}`);
  
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`); // Use template literal for cleaner string formatting
      }
  
      const data = await response.json();
      // console.log('-----return-------',data)
      const categories = Object.keys(data);
      const hoursLogged = Object.values(data);

      return { categories, hoursLogged };
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
      return null;
    }
  }



  export async function generateDoughnutChart() {
    const chartElement = document.getElementById('myCircle');
    const chartContext = chartElement.getContext('2d');
    const tuneButton = document.getElementById('tuneButton');
    const buttonText = tuneButton.textContent; 
    let tune = buttonText === 'Tuned';

    try {
        const { categories, hoursLogged } = await processUserData(tune);
        const totalHours = hoursLogged.reduce((a, b) => a + b, 0);
        const colorArray = generateColorArray(categories.length);

        const existingDoughnutChart = Chart.getChart('myCircle');
        if (existingDoughnutChart) {
            existingDoughnutChart.destroy();
        }

        const doughnutChart = new Chart(chartContext, {
            type: 'doughnut',
            data: {
                labels: categories,
                datasets: [{
                    label: 'Hours Logged',
                    data: hoursLogged,
                    backgroundColor: colorArray,
                    borderColor: colorArray.map(color => color.replace('0.2', '1')),
                    borderWidth: 1,
                }],
            },
            options: {
                cutout: '50%',
                rotation: -0.5 * Math.PI,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const data = context.parsed;
                                return `${label}: ${data} hours (${((data / totalHours) * 100).toFixed(2)}%)`;
                            }
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                    }
                }
            },
        });
    } catch (error) {
        console.error('Error generating doughnut chart:', error);
    }
}

// result.js - Updated with IoT and Shelf Life

let currentResultId = null;
let currentRipeness = null;

// Load prediction result and image on page load
window.addEventListener('DOMContentLoaded', function() {
  const resultData = sessionStorage.getItem('predictionResult');
  const imageData = sessionStorage.getItem('uploadedImage');
  
  // Display the uploaded image
  const resultImage = document.getElementById('resultImage');
  if (imageData && resultImage) {
    resultImage.src = imageData;
  }
  
  // Display prediction results
  const predictionBox = document.getElementById('predictionBox');
  if (resultData && predictionBox) {
    const prediction = JSON.parse(resultData);
    currentResultId = prediction.result_id;
    currentRipeness = prediction.ripeness;
    
    if (!prediction.is_fruit) {
      predictionBox.innerHTML = `
        <h3>⚠️ Not a Fruit Detected</h3>
        <p><strong>Detection:</strong> ${prediction.ripeness}</p>
        <p><strong>Confidence:</strong> ${(prediction.ripeness_conf * 100).toFixed(2)}%</p>
        <p class="warning-text">Please provide an apple or orange image.</p>
      `;
    } else {
      predictionBox.innerHTML = `
        <h3>✅ Fruit Detected</h3>
        <p><strong>Fruit Type:</strong> ${prediction.fruit} (${(prediction.fruit_conf * 100).toFixed(2)}% confidence)</p>
        <p><strong>Ripeness:</strong> ${prediction.ripeness} (${(prediction.ripeness_conf * 100).toFixed(2)}% confidence)</p>
      `;
      
      // Show IoT section for fruits
      document.getElementById('iotSection').style.display = 'block';
    }
  } else {
    if (predictionBox) {
      predictionBox.innerHTML = '<p>No prediction data available.</p>';
    }
  }
});

// Read IoT sensor
async function readSensor() {
  const loadingOverlay = document.getElementById('loadingOverlay');
  loadingOverlay.style.display = 'flex';
  
  try {
    const response = await fetch('http://127.0.0.1:5000/read_sensor', {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error('Sensor read failed');
    }
    
    const data = await response.json();
    
    // Display sensor data
    document.getElementById('tempValue').textContent = data.temperature.toFixed(1);
    document.getElementById('humValue').textContent = data.humidity.toFixed(1);
    document.getElementById('sensorData').style.display = 'block';
    
    // Calculate and display shelf life
    const shelfLife = calculateShelfLife(currentRipeness, data.temperature, data.humidity);
    document.getElementById('shelfLifeValue').textContent = shelfLife;
    document.getElementById('shelfLifeBox').style.display = 'block';
    
    // Update result in CSV
    await updateResultWithIoT(data.temperature, data.humidity, shelfLife);
    
    loadingOverlay.style.display = 'none';
    alert('✅ Environmental data saved successfully!');
  } catch (error) {
    loadingOverlay.style.display = 'none';
    console.error('Sensor error:', error);
    alert('❌ Failed to read sensor: ' + error.message);
  }
}

async function updateResultWithIoT(temp, hum, shelfLife) {
  try {
    await fetch('http://127.0.0.1:5000/update_result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        result_id: currentResultId,
        temperature: temp,
        humidity: hum,
        shelf_life: shelfLife
      })
    });
  } catch (error) {
    console.error('Update error:', error);
  }
}

function calculateShelfLife(ripeness, temp, hum) {
  const baseShelfLife = {
    'Unripe': [5, 7],
    'Ripe': [2, 3],
    'Overripe': [0, 0]
  };
  
  if (!baseShelfLife[ripeness]) return 'N/A';
  
  let [low, high] = baseShelfLife[ripeness];
  
  if (ripeness === 'Overripe') {
    return '0 days';
  }
  
  if (temp === null || hum === null) {
    return `${low}-${high} days`;
  }
  
  let factor = 1.0;
  
  if (temp > 30) {
    factor = 0.6;
  } else if (temp >= 20 && temp <= 30 && hum >= 50 && hum <= 80) {
    factor = 1.0;
  } else if (temp < 20 && hum >= 55 && hum <= 65) {
    factor = 1.2;
  } else {
    factor = 0.8;
  }
  
  const adjLow = Math.max(0, Math.round(low * factor));
  const adjHigh = Math.max(0, Math.round(high * factor));
  
  return `${adjLow}-${adjHigh} days`;
}

function scanAnotherImage() {
  sessionStorage.clear();
  window.location.href = 'preview.html';
}

function goHome() {
  sessionStorage.clear();
  window.location.href = 'index.html';
}

function goDashboard() {
  window.location.href = 'dashboard.html';
}

function goHistory() {
  window.location.href = 'history.html';
}

function goContact() {
  window.location.href = 'index.html#contact';
}

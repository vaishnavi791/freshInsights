// Load prediction result and image on page load
window.addEventListener('DOMContentLoaded', function() {
  const resultData = sessionStorage.getItem('predictionResult');
  const imageData = sessionStorage.getItem('uploadedImage');
  
  // Display the uploaded image
  const resultImage = document.getElementById('resultImage');
  if (imageData && resultImage) {
    resultImage.src = imageData;
  } else {
    console.error('No image data found in sessionStorage');
  }
  
  // Display prediction results
  const predictionBox = document.getElementById('predictionBox');
  if (resultData && predictionBox) {
    const prediction = JSON.parse(resultData);
    
    predictionBox.innerHTML = `
      <h3>Prediction Results</h3>
      <p><strong>Fruit Type:</strong> ${prediction.fruit} (${(prediction.fruit_conf * 100).toFixed(2)}% confidence)</p>
      <p><strong>Ripeness:</strong> ${prediction.ripeness} (${(prediction.ripeness_conf * 100).toFixed(2)}% confidence)</p>
    `;
  } else {
    if (predictionBox) {
      predictionBox.innerHTML = '<p>No prediction data available. Please scan an image first.</p>';
    }
  }
});

function scanAnotherImage() {
  sessionStorage.clear();
  window.location.href = 'preview.html';
}

function goHome() {
  sessionStorage.clear();
  window.location.href = 'index.html';
}

function goContact() {
  window.location.href = 'index.html#contact';
}

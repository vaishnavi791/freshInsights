let uploadedFile = null;
let cameraStream = null;
let capturedImageBlob = null;

// Handle file upload
document.getElementById('uploadFile').addEventListener('change', function(e) {
  uploadedFile = e.target.files[0];
  capturedImageBlob = null;
  
  if (uploadedFile) {
    // Show preview
    const reader = new FileReader();
    reader.onload = function(event) {
      const previewImg = document.getElementById('imagePreview');
      const previewContainer = document.getElementById('imagePreviewContainer');
      
      if (previewImg && previewContainer) {
        previewImg.src = event.target.result;
        previewContainer.style.display = 'block';
      }
    };
    reader.readAsDataURL(uploadedFile);
  }
});

// Open camera
async function openCamera() {
  const video = document.getElementById('cameraFeed');
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 640, height: 480 } 
    });
    video.srcObject = cameraStream;
    video.style.display = 'block';
    addCaptureButton();
  } catch (err) {
    alert('Camera access denied: ' + err.message);
  }
}

function addCaptureButton() {
  if (document.getElementById('captureBtn')) return;
  
  const video = document.getElementById('cameraFeed');
  const captureBtn = document.createElement('button');
  captureBtn.id = 'captureBtn';
  captureBtn.className = 'action-btn';
  captureBtn.textContent = 'Capture Photo';
  captureBtn.onclick = captureFromCamera;
  video.parentNode.insertBefore(captureBtn, video.nextSibling);
}

function captureFromCamera() {
  const video = document.getElementById('cameraFeed');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  canvas.toBlob(function(blob) {
    capturedImageBlob = blob;
    uploadedFile = null;
    
    // Show preview
    const previewImg = document.getElementById('imagePreview');
    const previewContainer = document.getElementById('imagePreviewContainer');
    if (previewImg && previewContainer) {
      previewImg.src = URL.createObjectURL(blob);
      previewContainer.style.display = 'block';
    }
    
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      video.style.display = 'none';
    }
    
    const captureBtn = document.getElementById('captureBtn');
    if (captureBtn) captureBtn.remove();
    
    alert('Photo captured! Click Submit to analyze.');
  }, 'image/jpeg', 0.95);
}

function retakeImage() {
  uploadedFile = null;
  capturedImageBlob = null;
  document.getElementById('uploadFile').value = '';
  
  const previewContainer = document.getElementById('imagePreviewContainer');
  if (previewContainer) previewContainer.style.display = 'none';
  
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    document.getElementById('cameraFeed').style.display = 'none';
  }
  
  const captureBtn = document.getElementById('captureBtn');
  if (captureBtn) captureBtn.remove();
}

// Submit image to backend
async function submitImage() {
  if (!uploadedFile && !capturedImageBlob) {
    alert('Please upload or capture an image first!');
    return;
  }

  const formData = new FormData();
  
  if (uploadedFile) {
    formData.append('image', uploadedFile);
  } else if (capturedImageBlob) {
    formData.append('image', capturedImageBlob, 'captured-photo.jpg');
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/predict', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();
    
    // Store prediction result
    sessionStorage.setItem('predictionResult', JSON.stringify(result));
    
    // Store image as base64 for result page
    const reader = new FileReader();
    reader.onloadend = function() {
      sessionStorage.setItem('uploadedImage', reader.result);
      window.location.href = 'result.html';
    };
    
    // Read as base64 data URL
    if (uploadedFile) {
      reader.readAsDataURL(uploadedFile);
    } else if (capturedImageBlob) {
      reader.readAsDataURL(capturedImageBlob);
    }
    
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to get prediction: ' + error.message);
  }
}

function goHome() {
  window.location.href = 'index.html';
}

function goContact() {
  window.location.href = 'index.html#contact';
}

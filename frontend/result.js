// Show the uploaded image from localStorage
function showImage(src) {
  document.getElementById("resultImage").src = src;
}

// Scan another → go back to preview
function scanAnotherImage() {
  localStorage.removeItem("capturedImage");
  window.location.href = "preview.html";
}

// Fetch prediction from backend
async function fetchPrediction(imageData) {
  try {
    // Convert base64 to blob correctly
    const resImage = await fetch(imageData);
    const blob = await resImage.blob();

    // Prepare FormData
    const formData = new FormData();
    formData.append("image", blob, "upload.png");  // filename is important

    // Send to backend
    const res = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData
    });

    // Read backend
    const data = await res.json();
    console.log("BACKEND RESPONSE:", data);

    // Directly pass data (it matches frontend keys)
    showPrediction(data);

  } catch (err) {
    console.error(err);
    alert("Error fetching prediction!");
  }
}

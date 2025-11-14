// Header icon actions
const mailIcon = document.getElementById('mailIcon');
const githubIcon = document.getElementById('githubIcon');
const linkedinIcon = document.getElementById('linkedinIcon');
const infoBox = document.getElementById('infoBox');

mailIcon.addEventListener('click', () => {
  infoBox.style.display = 'block';
  infoBox.innerHTML = '✉︎ freshInsight9@gmail.com';
});

githubIcon.addEventListener('click', () => {
  infoBox.style.display = 'block';
  infoBox.innerHTML = `<a href="https://github.com/vaishnavi791/freshInsights" target="_blank">🐱 GitHub Project Link</a>`;
});

linkedinIcon.addEventListener('click', () => {
  window.location.href = 'team-member.html';  // Your team member page
});

function goHome() {
  window.location.href = "index.html"; // homepage
}
function goContact() {
  const contactSection = document.getElementById("contact");
  if (contactSection) {
    contactSection.scrollIntoView({ behavior: "smooth" });
  } else {
    // fallback if not on homepage → redirect to homepage#contact
    window.location.href = "index.html#contact";
  }
}let stream;
let capturedImage = null;

// Open camera
function openCamera() {
  const video = document.getElementById("cameraFeed");
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(mediaStream => {
      stream = mediaStream;
      video.srcObject = mediaStream;
      video.style.display = "block";

      // Listen for Enter key to capture the image
      document.addEventListener("keydown", enterCapture);
    })
    .catch(err => {
      alert("Camera access denied!");
      console.error(err);
    });
}

// Function triggered on Enter key
function enterCapture(event) {
  if(event.key === "Enter") {
    captureImage();
  }
}

// Capture current frame from video
function captureImage() {
  const video = document.getElementById("cameraFeed");
  if (!video.srcObject) return alert("Camera not started!");

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  capturedImage = canvas.toDataURL("image/png");

  // Stop camera
  if(stream) stream.getTracks().forEach(track => track.stop());
  video.style.display = "none";

  // Remove Enter listener so it doesn’t trigger again
  document.removeEventListener("keydown", enterCapture);

  // Save and redirect
  localStorage.setItem("capturedImage", capturedImage);
  window.location.href = "result.html";
}

// Retake / stop camera
function retakeImage() {
  const video = document.getElementById("cameraFeed");
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    video.style.display = "none";
    capturedImage = null;
  }
}

// Upload file
document.getElementById("uploadFile").addEventListener("change", function(e){
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(){
    capturedImage = reader.result;
    localStorage.setItem("capturedImage", capturedImage);  // <-- FIXED
  }
  reader.readAsDataURL(file);
});
// Submit button for upload
function submitImage() {
  if (!capturedImage) {
    alert("Please upload or capture an image first!");
    return;
  }
  localStorage.setItem("capturedImage", capturedImage);
  window.location.href = "result.html";
}

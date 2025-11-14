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

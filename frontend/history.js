// history.js - Analysis History Implementation

let historyData = [];
let filteredHistoryData = [];

window.addEventListener('DOMContentLoaded', function() {
  loadHistory();
});

async function loadHistory() {
  try {
    const response = await fetch('http://127.0.0.1:5000/history_data');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    historyData = await response.json();
    filteredHistoryData = historyData;
    
    populateFilterDropdowns();
    displayHistory(historyData);
  } catch (error) {
    console.error('Error loading history:', error);
    document.getElementById('historyTableBody').innerHTML = 
      '<tr><td colspan="10" style="text-align: center; color: red;">Failed to load history data</td></tr>';
  }
}

function populateFilterDropdowns() {
  const fruitTypes = [...new Set(historyData.map(d => d.Fruit_Type))];
  const ripenessTypes = [...new Set(historyData.map(d => d.Ripeness))];
  
  const fruitFilter = document.getElementById('fruitFilter');
  fruitFilter.innerHTML = '<option value="all">All</option>' +
    fruitTypes.map(f => `<option value="${f}">${f}</option>`).join('');
  
  const ripenessFilter = document.getElementById('ripenessFilter');
  ripenessFilter.innerHTML = '<option value="all">All</option>' +
    ripenessTypes.map(r => `<option value="${r}">${r}</option>`).join('');
}

function displayHistory(data) {
  const tbody = document.getElementById('historyTableBody');
  
  if (!data || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" style="text-align: center;">No data available</td></tr>';
    return;
  }
  
  tbody.innerHTML = data.map(row => `
    <tr ${row.Fruit_Confidence < 50 ? 'class="low-confidence"' : ''}>
      <td>${row.ID}</td>
      <td>${row.Timestamp}</td>
      <td>${row.Fruit_Type}</td>
      <td>${row.Fruit_Confidence}%</td>
      <td>${row.Ripeness}</td>
      <td>${row.Ripeness_Confidence}%</td>
      <td>${row.Temperature_C !== null ? row.Temperature_C.toFixed(1) : 'N/A'}</td>
      <td>${row.Humidity_pct !== null ? row.Humidity_pct.toFixed(1) : 'N/A'}</td>
      <td>${row.Shelf_Life || 'N/A'}</td>
      <td>${row.Source}</td>
    </tr>
  `).join('');
}

function applyFilters() {
  const fruitValue = document.getElementById('fruitFilter').value;
  const ripenessValue = document.getElementById('ripenessFilter').value;
  
  filteredHistoryData = historyData.filter(row => {
    const fruitMatch = fruitValue === 'all' || row.Fruit_Type === fruitValue;
    const ripenessMatch = ripenessValue === 'all' || row.Ripeness === ripenessValue;
    return fruitMatch && ripenessMatch;
  });
  
  displayHistory(filteredHistoryData);
}

function clearFilters() {
  document.getElementById('fruitFilter').value = 'all';
  document.getElementById('ripenessFilter').value = 'all';
  filteredHistoryData = historyData;
  displayHistory(historyData);
}

function downloadHistoryCSV() {
  window.location.href = 'http://127.0.0.1:5000/download_csv';
}

// Navigation functions
function goHome() {
  window.location.href = 'index.html';
}

function goUpload() {
  window.location.href = 'preview.html';
}

function goDashboard() {
  window.location.href = 'dashboard.html';
}

function goContact() {
  window.location.href = 'index.html#contact';
}

// dashboard.js - Complete Dashboard Implementation

let dashboardData = null;
let filteredData = null;

// Load dashboard on page load
window.addEventListener('DOMContentLoaded', function() {
  loadDashboardData();
});

async function loadDashboardData() {
  showLoading(true);
  
  try {
    const response = await fetch('http://127.0.0.1:5000/dashboard_data');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    dashboardData = data;
    filteredData = data;
    
    // Populate filters
    populateFilters(data.rawData);
    
    // Display metrics
    displayMetrics(data.metrics);
    
    // Display insights
    displayInsights(data.insights);
    
    // Render all charts
    renderAllCharts(data.charts);
    
    showLoading(false);
  } catch (error) {
    console.error('Error loading dashboard:', error);
    showLoading(false);
    alert('Failed to load dashboard data. Please ensure the backend is running and data exists.');
  }
}

function displayMetrics(metrics) {
  document.getElementById('totalAnalyses').textContent = metrics.total_analyses || '-';
  document.getElementById('avgFruitConf').textContent = metrics.avg_fruit_conf ? `${metrics.avg_fruit_conf}%` : '-';
  document.getElementById('avgRipenessConf').textContent = metrics.avg_ripeness_conf ? `${metrics.avg_ripeness_conf}%` : '-';
  document.getElementById('mostCommonFruit').textContent = metrics.most_common_fruit || '-';
  document.getElementById('avgTemp').textContent = metrics.avg_temp ? `${metrics.avg_temp}°C` : 'N/A';
  document.getElementById('avgHumidity').textContent = metrics.avg_humidity ? `${metrics.avg_humidity}%` : 'N/A';
}

function displayInsights(insights) {
  const container = document.getElementById('insightsContainer');
  if (!insights || insights.length === 0) {
    container.innerHTML = '<p class="info-message">No insights available yet.</p>';
    return;
  }
  
  container.innerHTML = insights.map(insight => 
    `<div class="insight-card">${insight}</div>`
  ).join('');
}

function renderAllCharts(charts) {
  // Environmental Conditions
  if (charts.tempHumCombined) {
    Plotly.newPlot('tempHumCombinedChart', charts.tempHumCombined.data, charts.tempHumCombined.layout, {responsive: true});
  }
  
  if (charts.tempDistribution) {
    Plotly.newPlot('tempDistributionChart', charts.tempDistribution.data, charts.tempDistribution.layout, {responsive: true});
  }
  
  if (charts.humDistribution) {
    Plotly.newPlot('humDistributionChart', charts.humDistribution.data, charts.humDistribution.layout, {responsive: true});
  }
  
  if (charts.tempHumCorrelation) {
    Plotly.newPlot('tempHumCorrelationChart', charts.tempHumCorrelation.data, charts.tempHumCorrelation.layout, {responsive: true});
  }
  
  // Environmental stats
  if (charts.stats) {
    displayEnvironmentalStats(charts.stats);
  }
  
  // Box plots by category
  if (charts.tempByFruit) {
    Plotly.newPlot('tempByFruitChart', charts.tempByFruit.data, charts.tempByFruit.layout, {responsive: true});
  }
  
  if (charts.tempByRipeness) {
    Plotly.newPlot('tempByRipenessChart', charts.tempByRipeness.data, charts.tempByRipeness.layout, {responsive: true});
  }
  
  if (charts.humByFruit) {
    Plotly.newPlot('humByFruitChart', charts.humByFruit.data, charts.humByFruit.layout, {responsive: true});
  }
  
  if (charts.humByRipeness) {
    Plotly.newPlot('humByRipenessChart', charts.humByRipeness.data, charts.humByRipeness.layout, {responsive: true});
  }
  
  // Heatmaps
  if (charts.tempHeatmap) {
    Plotly.newPlot('tempHeatmapChart', charts.tempHeatmap.data, charts.tempHeatmap.layout, {responsive: true});
  }
  
  if (charts.humHeatmap) {
    Plotly.newPlot('humHeatmapChart', charts.humHeatmap.data, charts.humHeatmap.layout, {responsive: true});
  }
  
  // Gauges
  if (charts.tempGauge) {
    Plotly.newPlot('tempGaugeChart', charts.tempGauge.data, charts.tempGauge.layout, {responsive: true});
  }
  
  if (charts.humGauge) {
    Plotly.newPlot('humGaugeChart', charts.humGauge.data, charts.humGauge.layout, {responsive: true});
  }
  
  // Quality status
  if (charts.qualityStatus) {
    displayQualityStatus(charts.qualityStatus);
  }
  
  // Core charts
  if (charts.confidenceScatter) {
    Plotly.newPlot('confidenceScatterChart', charts.confidenceScatter.data, charts.confidenceScatter.layout, {responsive: true});
  }
  
  if (charts.sourceDistribution) {
    Plotly.newPlot('sourceDistributionChart', charts.sourceDistribution.data, charts.sourceDistribution.layout, {responsive: true});
  }
  
  if (charts.fruitDistribution) {
    Plotly.newPlot('fruitDistributionChart', charts.fruitDistribution.data, charts.fruitDistribution.layout, {responsive: true});
  }
  
  if (charts.ripenessDistribution) {
    Plotly.newPlot('ripenessDistributionChart', charts.ripenessDistribution.data, charts.ripenessDistribution.layout, {responsive: true});
  }
  
  if (charts.stackedBar) {
    Plotly.newPlot('stackedBarChart', charts.stackedBar.data, charts.stackedBar.layout, {responsive: true});
  }
  
  if (charts.groupedBar) {
    Plotly.newPlot('groupedBarChart', charts.groupedBar.data, charts.groupedBar.layout, {responsive: true});
  }
  
  if (charts.fruitConfBox) {
    Plotly.newPlot('fruitConfBoxChart', charts.fruitConfBox.data, charts.fruitConfBox.layout, {responsive: true});
  }
  
  if (charts.ripenessConfBox) {
    Plotly.newPlot('ripenessConfBoxChart', charts.ripenessConfBox.data, charts.ripenessConfBox.layout, {responsive: true});
  }
}

function displayEnvironmentalStats(stats) {
  document.getElementById('minTemp').textContent = stats.minTemp ? `${stats.minTemp}°C` : 'N/A';
  document.getElementById('maxTemp').textContent = stats.maxTemp ? `${stats.maxTemp}°C` : 'N/A';
  document.getElementById('avgTempStat').textContent = stats.avgTemp ? `${stats.avgTemp}°C` : 'N/A';
  document.getElementById('minHum').textContent = stats.minHum ? `${stats.minHum}%` : 'N/A';
  document.getElementById('maxHum').textContent = stats.maxHum ? `${stats.maxHum}%` : 'N/A';
  document.getElementById('avgHumStat').textContent = stats.avgHum ? `${stats.avgHum}%` : 'N/A';
  document.getElementById('correlation').textContent = stats.correlation ? stats.correlation.toFixed(3) : 'N/A';
}

function displayQualityStatus(status) {
  const container = document.getElementById('currentStatus');
  
  if (status.optimal) {
    container.innerHTML = '<p class="status-optimal">✅ Current conditions are optimal!</p>';
  } else if (status.acceptable) {
    container.innerHTML = '<p class="status-acceptable">⚠️ Current conditions are acceptable.</p>';
  } else {
    container.innerHTML = '<p class="status-poor">❌ Current conditions need adjustment.</p>';
  }
}

function populateFilters(rawData) {
  if (!rawData || rawData.length === 0) return;
  
  // Fruit filter
  const fruitTypes = [...new Set(rawData.map(d => d.Fruit_Type))];
  const fruitFilter = document.getElementById('fruitFilter');
  fruitFilter.innerHTML = '<option value="all" selected>All</option>' +
    fruitTypes.map(f => `<option value="${f}">${f}</option>`).join('');
  
  // Ripeness filter
  const ripenessTypes = [...new Set(rawData.map(d => d.Ripeness))];
  const ripenessFilter = document.getElementById('ripenessFilter');
  ripenessFilter.innerHTML = '<option value="all" selected>All</option>' +
    ripenessTypes.map(r => `<option value="${r}">${r}</option>`).join('');
  
  // Date range
  const dates = rawData.map(d => new Date(d.Date)).filter(d => !isNaN(d));
  if (dates.length > 0) {
    const minDate = new Date(Math.min(...dates));
    const maxDate = new Date(Math.max(...dates));
    document.getElementById('dateFrom').value = minDate.toISOString().split('T')[0];
    document.getElementById('dateTo').value = maxDate.toISOString().split('T')[0];
  }
}

function applyFilters() {
  // This would filter the data and re-render charts
  // For simplicity, we'll just reload for now
  alert('Filtering functionality - reload dashboard to reset');
}

function clearFilters() {
  document.getElementById('fruitFilter').selectedIndex = 0;
  document.getElementById('ripenessFilter').selectedIndex = 0;
  loadDashboardData();
}

function downloadCSV() {
  window.location.href = 'http://127.0.0.1:5000/download_csv';
}

function refreshDashboard() {
  loadDashboardData();
}

function showLoading(show) {
  const overlay = document.getElementById('loadingOverlay');
  overlay.style.display = show ? 'flex' : 'none';
}

// Navigation functions
function goHome() {
  window.location.href = 'index.html';
}

function goUpload() {
  window.location.href = 'preview.html';
}

function goHistory() {
  window.location.href = 'history.html';
}

function goContact() {
  window.location.href = 'index.html#contact';
}

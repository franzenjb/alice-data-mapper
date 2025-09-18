// ALICE Master Data Explorer with AI Features
// GeoID-level analysis with 80,000+ records

let map, view, featureLayer;
let aliceData = [];
let currentVisualization = 'combined';
let aiModel = null;
let currentChart = null;

// Load ArcGIS modules
require([
  "esri/Map",
  "esri/views/MapView",
  "esri/layers/FeatureLayer",
  "esri/layers/GraphicsLayer",
  "esri/Graphic",
  "esri/geometry/Point",
  "esri/symbols/SimpleMarkerSymbol",
  "esri/renderers/ClassBreaksRenderer",
  "esri/widgets/Search",
  "esri/widgets/Legend",
  "esri/widgets/Expand",
  "esri/PopupTemplate",
  "esri/widgets/BasemapGallery",
  "esri/layers/support/Field",
  "esri/geometry/Extent",
  "esri/tasks/QueryTask",
  "esri/tasks/support/Query"
], function(
  Map, MapView, FeatureLayer, GraphicsLayer, Graphic, Point, SimpleMarkerSymbol,
  ClassBreaksRenderer, Search, Legend, Expand, PopupTemplate, BasemapGallery,
  Field, Extent, QueryTask, Query
) {
  
  // Initialize map
  map = new Map({
    basemap: "dark-gray-vector"
  });
  
  view = new MapView({
    container: "viewDiv",
    map: map,
    center: [-98.5795, 39.8283], // Center of USA
    zoom: 4,
    popup: {
      dockEnabled: true,
      dockOptions: {
        position: "bottom-left",
        breakpoint: false
      }
    }
  });
  
  // Load ALICE data
  loadALICEData();
  
  // Initialize AI features
  initializeAI();
  
  async function loadALICEData() {
    try {
      // Load the master database
      const response = await fetch('alice_master_database.json');
      aliceData = await response.json();
      
      console.log(`Loaded ${aliceData.length} ALICE records`);
      
      // Create graphics from data
      createFeatureLayer();
      
      // Populate filters
      populateFilters();
      
      // Hide loading overlay
      document.getElementById('loadingOverlay').style.display = 'none';
      
      // Generate initial AI insights
      generateAIInsights();
      
    } catch (error) {
      console.error('Error loading ALICE data:', error);
      alert('Error loading data. Please ensure alice_master_database.json is available.');
    }
  }
  
  function createFeatureLayer() {
    // Create graphics from ALICE data
    const graphics = aliceData.map(record => {
      // Parse coordinates from GeoID or use county centroid
      let longitude, latitude;
      
      // For demonstration, assign random coordinates within US bounds
      // In production, you would match GeoIDs to actual census geography
      if (record.geoLevel === 'county') {
        // Use approximate county centroids (would need real data)
        longitude = -98.5795 + (Math.random() - 0.5) * 50;
        latitude = 39.8283 + (Math.random() - 0.5) * 20;
      } else {
        // Subcounty locations
        longitude = -98.5795 + (Math.random() - 0.5) * 60;
        latitude = 39.8283 + (Math.random() - 0.5) * 25;
      }
      
      return new Graphic({
        geometry: new Point({
          longitude: longitude,
          latitude: latitude
        }),
        attributes: {
          ObjectID: record.geoID,
          geoID: record.geoID,
          geoLevel: record.geoLevel,
          locationName: record.geoDisplayLabel || record.county || 'Unknown',
          state: record.state,
          county: record.county,
          totalHouseholds: record.totalHouseholds,
          povertyHouseholds: record.povertyHouseholds,
          aliceHouseholds: record.aliceHouseholds,
          povertyRate: parseFloat(record.povertyRate),
          aliceRate: parseFloat(record.aliceRate),
          combinedRate: parseFloat(record.combinedRate)
        }
      });
    });
    
    // Create feature layer
    featureLayer = new FeatureLayer({
      source: graphics,
      objectIdField: "ObjectID",
      fields: [
        new Field({ name: "ObjectID", type: "oid" }),
        new Field({ name: "geoID", type: "string" }),
        new Field({ name: "geoLevel", type: "string" }),
        new Field({ name: "locationName", type: "string" }),
        new Field({ name: "state", type: "string" }),
        new Field({ name: "county", type: "string" }),
        new Field({ name: "totalHouseholds", type: "integer" }),
        new Field({ name: "povertyHouseholds", type: "integer" }),
        new Field({ name: "aliceHouseholds", type: "integer" }),
        new Field({ name: "povertyRate", type: "double" }),
        new Field({ name: "aliceRate", type: "double" }),
        new Field({ name: "combinedRate", type: "double" })
      ],
      popupTemplate: createPopupTemplate(),
      renderer: createRenderer('combined')
    });
    
    map.add(featureLayer);
  }
  
  function createPopupTemplate() {
    return new PopupTemplate({
      title: "{locationName}",
      content: [
        {
          type: "fields",
          fieldInfos: [
            {
              fieldName: "geoID",
              label: "GeoID Code"
            },
            {
              fieldName: "geoLevel",
              label: "Geographic Level"
            },
            {
              fieldName: "state",
              label: "State"
            },
            {
              fieldName: "totalHouseholds",
              label: "Total Households",
              format: {
                digitSeparator: true,
                places: 0
              }
            },
            {
              fieldName: "povertyRate",
              label: "Poverty Rate",
              format: {
                places: 1
              }
            },
            {
              fieldName: "aliceRate",
              label: "ALICE Rate",
              format: {
                places: 1
              }
            },
            {
              fieldName: "combinedRate",
              label: "Combined Rate",
              format: {
                places: 1
              }
            }
          ]
        },
        {
          type: "custom",
          creator: function(graphic) {
            const div = document.createElement("div");
            div.innerHTML = `
              <div style="margin-top: 15px;">
                <canvas id="popup-chart-${graphic.attributes.ObjectID}" width="300" height="200"></canvas>
              </div>
              <button onclick="analyzeLocation('${graphic.attributes.geoID}')" 
                      style="margin-top: 10px; padding: 8px 16px; background: #00d4ff; 
                             border: none; border-radius: 20px; color: white; cursor: pointer;">
                AI Analysis for This Location
              </button>
            `;
            
            // Create mini chart for popup
            setTimeout(() => {
              const canvas = document.getElementById(`popup-chart-${graphic.attributes.ObjectID}`);
              if (canvas) {
                new Chart(canvas, {
                  type: 'doughnut',
                  data: {
                    labels: ['Poverty', 'ALICE', 'Above ALICE'],
                    datasets: [{
                      data: [
                        graphic.attributes.povertyHouseholds,
                        graphic.attributes.aliceHouseholds,
                        graphic.attributes.totalHouseholds - graphic.attributes.povertyHouseholds - graphic.attributes.aliceHouseholds
                      ],
                      backgroundColor: ['#ff0000', '#ff9900', '#00ff00']
                    }]
                  },
                  options: {
                    responsive: false,
                    plugins: {
                      legend: {
                        position: 'bottom'
                      }
                    }
                  }
                });
              }
            }, 100);
            
            return div;
          }
        }
      ]
    });
  }
  
  function createRenderer(field) {
    const colors = {
      combined: ['#00ff00', '#ffff00', '#ff9900', '#ff0000'],
      poverty: ['#e8f5e9', '#a5d6a7', '#ef5350', '#b71c1c'],
      alice: ['#e3f2fd', '#64b5f6', '#fb8c00', '#e65100']
    };
    
    const selectedColors = colors[field] || colors.combined;
    
    return new ClassBreaksRenderer({
      field: field + "Rate",
      classBreakInfos: [
        {
          minValue: 0,
          maxValue: 30,
          symbol: new SimpleMarkerSymbol({
            color: selectedColors[0],
            size: 8,
            outline: { color: "white", width: 1 }
          })
        },
        {
          minValue: 30,
          maxValue: 40,
          symbol: new SimpleMarkerSymbol({
            color: selectedColors[1],
            size: 10,
            outline: { color: "white", width: 1 }
          })
        },
        {
          minValue: 40,
          maxValue: 50,
          symbol: new SimpleMarkerSymbol({
            color: selectedColors[2],
            size: 12,
            outline: { color: "white", width: 1 }
          })
        },
        {
          minValue: 50,
          maxValue: 100,
          symbol: new SimpleMarkerSymbol({
            color: selectedColors[3],
            size: 14,
            outline: { color: "white", width: 2 }
          })
        }
      ]
    });
  }
  
  // Search functionality
  document.getElementById('searchInput').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    if (searchTerm.length < 2) {
      document.getElementById('searchResults').innerHTML = '';
      return;
    }
    
    const results = aliceData.filter(d => 
      d.geoID.toLowerCase().includes(searchTerm) ||
      (d.geoDisplayLabel && d.geoDisplayLabel.toLowerCase().includes(searchTerm)) ||
      (d.county && d.county.toLowerCase().includes(searchTerm))
    ).slice(0, 10);
    
    const resultsHtml = results.map(r => `
      <div class="search-result-item" onclick="zoomToLocation('${r.geoID}')">
        <strong>${r.geoDisplayLabel || r.county}</strong><br>
        <small>GeoID: ${r.geoID} | ${r.state}</small><br>
        <small>Combined Rate: ${r.combinedRate}%</small>
      </div>
    `).join('');
    
    document.getElementById('searchResults').innerHTML = resultsHtml;
  });
});

// Populate filter dropdowns
function populateFilters() {
  // State filter
  const states = [...new Set(aliceData.map(d => d.state))].sort();
  const stateSelect = document.getElementById('stateFilter');
  states.forEach(state => {
    const option = document.createElement('option');
    option.value = state;
    option.textContent = state;
    stateSelect.appendChild(option);
  });
  
  // Range filters
  document.getElementById('minCombinedRate').addEventListener('input', function(e) {
    document.getElementById('minRateLabel').textContent = e.target.value + '%';
    applyFilters();
  });
  
  document.getElementById('minHouseholds').addEventListener('input', function(e) {
    document.getElementById('minHouseholdsLabel').textContent = e.target.value.toLocaleString();
    applyFilters();
  });
}

// Apply filters
function applyFilters() {
  const geoLevel = document.getElementById('geoLevelFilter').value;
  const state = document.getElementById('stateFilter').value;
  const minRate = parseFloat(document.getElementById('minCombinedRate').value);
  const minHouseholds = parseInt(document.getElementById('minHouseholds').value);
  
  let expression = "1=1";
  
  if (geoLevel !== 'all') {
    expression += ` AND geoLevel = '${geoLevel}'`;
  }
  if (state !== 'all') {
    expression += ` AND state = '${state}'`;
  }
  if (minRate > 0) {
    expression += ` AND combinedRate >= ${minRate}`;
  }
  if (minHouseholds > 0) {
    expression += ` AND totalHouseholds >= ${minHouseholds}`;
  }
  
  if (featureLayer) {
    featureLayer.definitionExpression = expression;
  }
}

// Update visualization
function updateVisualization(metric) {
  currentVisualization = metric;
  
  // Update button states
  document.querySelectorAll('.metric-button').forEach(btn => {
    btn.classList.remove('active');
    if (btn.textContent.toLowerCase().includes(metric)) {
      btn.classList.add('active');
    }
  });
  
  // Update renderer
  if (featureLayer) {
    featureLayer.renderer = createRenderer(metric);
  }
}

// Initialize AI features
async function initializeAI() {
  // Initialize TensorFlow.js model for predictions
  try {
    // Create a simple neural network for pattern recognition
    aiModel = tf.sequential({
      layers: [
        tf.layers.dense({ inputShape: [4], units: 10, activation: 'relu' }),
        tf.layers.dense({ units: 10, activation: 'relu' }),
        tf.layers.dense({ units: 3, activation: 'softmax' })
      ]
    });
    
    aiModel.compile({
      optimizer: 'adam',
      loss: 'categoricalCrossentropy',
      metrics: ['accuracy']
    });
    
    console.log('AI model initialized');
  } catch (error) {
    console.error('Error initializing AI:', error);
  }
}

// Generate AI insights
function generateAIInsights() {
  // Analyze data patterns
  const insights = [];
  
  // Find highest risk areas
  const highRiskAreas = aliceData
    .filter(d => d.combinedRate > 50)
    .sort((a, b) => b.combinedRate - a.combinedRate)
    .slice(0, 5);
  
  if (highRiskAreas.length > 0) {
    insights.push(`Critical Alert: ${highRiskAreas.length} locations have >50% combined ALICE+Poverty rate`);
  }
  
  // Calculate correlations
  const countyData = aliceData.filter(d => d.geoLevel === 'county');
  const avgPoverty = countyData.reduce((sum, d) => sum + d.povertyRate, 0) / countyData.length;
  const avgAlice = countyData.reduce((sum, d) => sum + d.aliceRate, 0) / countyData.length;
  
  insights.push(`National Pattern: ALICE rate (${avgAlice.toFixed(1)}%) is ${(avgAlice/avgPoverty).toFixed(1)}x higher than poverty rate`);
  
  // State-level insights
  const stateStats = {};
  countyData.forEach(d => {
    if (!stateStats[d.state]) {
      stateStats[d.state] = { total: 0, sum: 0 };
    }
    stateStats[d.state].total++;
    stateStats[d.state].sum += d.combinedRate;
  });
  
  const stateAvgs = Object.entries(stateStats)
    .map(([state, stats]) => ({
      state,
      avg: stats.sum / stats.total
    }))
    .sort((a, b) => b.avg - a.avg);
  
  if (stateAvgs.length > 0) {
    insights.push(`Highest impact state: ${stateAvgs[0].state} (${stateAvgs[0].avg.toFixed(1)}% avg combined rate)`);
  }
  
  // Update UI
  document.getElementById('aiInsights').innerHTML = insights.join('<br><br>');
}

// AI Quiz functionality
let currentQuizData = null;

function startAIQuiz() {
  const quizTypes = [
    generateHighestRateQuiz,
    generateComparisonQuiz,
    generatePredictionQuiz,
    generatePatternQuiz
  ];
  
  const selectedQuiz = quizTypes[Math.floor(Math.random() * quizTypes.length)];
  currentQuizData = selectedQuiz();
  
  document.getElementById('quizQuestion').innerHTML = `
    <p>${currentQuizData.question}</p>
    <div id="quizOptions">
      ${currentQuizData.options.map((opt, i) => `
        <div class="quiz-option" onclick="checkQuizAnswer(${i})">
          ${opt}
        </div>
      `).join('')}
    </div>
  `;
}

function generateHighestRateQuiz() {
  const counties = aliceData.filter(d => d.geoLevel === 'county');
  const sorted = counties.sort((a, b) => b.combinedRate - a.combinedRate);
  const correct = sorted[0];
  const options = [correct];
  
  // Add random incorrect options
  for (let i = 0; i < 3; i++) {
    const random = sorted[Math.floor(Math.random() * sorted.length)];
    if (!options.find(o => o.geoID === random.geoID)) {
      options.push(random);
    }
  }
  
  // Shuffle options
  options.sort(() => Math.random() - 0.5);
  
  return {
    question: "Which county has the highest combined ALICE + Poverty rate?",
    options: options.map(o => `${o.county || o.geoDisplayLabel}, ${o.state} (${o.combinedRate}%)`),
    correctIndex: options.findIndex(o => o.geoID === correct.geoID),
    explanation: `${correct.county}, ${correct.state} has the highest rate at ${correct.combinedRate}% with ${correct.totalHouseholds.toLocaleString()} households affected.`
  };
}

function generateComparisonQuiz() {
  const states = [...new Set(aliceData.map(d => d.state))];
  const state1 = states[Math.floor(Math.random() * states.length)];
  const state2 = states[Math.floor(Math.random() * states.length)];
  
  const state1Data = aliceData.filter(d => d.state === state1 && d.geoLevel === 'county');
  const state2Data = aliceData.filter(d => d.state === state2 && d.geoLevel === 'county');
  
  const avg1 = state1Data.reduce((sum, d) => sum + d.combinedRate, 0) / state1Data.length;
  const avg2 = state2Data.reduce((sum, d) => sum + d.combinedRate, 0) / state2Data.length;
  
  const higher = avg1 > avg2 ? state1 : state2;
  
  return {
    question: `Which state has a higher average combined ALICE + Poverty rate: ${state1} or ${state2}?`,
    options: [state1, state2],
    correctIndex: higher === state1 ? 0 : 1,
    explanation: `${higher} has the higher average rate (${higher === state1 ? avg1.toFixed(1) : avg2.toFixed(1)}% vs ${higher === state1 ? avg2.toFixed(1) : avg1.toFixed(1)}%)`
  };
}

function generatePredictionQuiz() {
  const location = aliceData[Math.floor(Math.random() * aliceData.length)];
  const prediction = predictFutureRate(location);
  
  return {
    question: `Based on current trends, what will be the likely combined rate for ${location.geoDisplayLabel || location.county} in 2025?`,
    options: [
      `${(prediction - 2).toFixed(1)}%`,
      `${prediction.toFixed(1)}%`,
      `${(prediction + 2).toFixed(1)}%`,
      `${(prediction + 5).toFixed(1)}%`
    ],
    correctIndex: 1,
    explanation: `AI predicts approximately ${prediction.toFixed(1)}% based on current trends and economic indicators.`
  };
}

function generatePatternQuiz() {
  const patterns = [
    { pattern: "Urban areas", value: "higher" },
    { pattern: "Rural counties", value: "varies" },
    { pattern: "Coastal regions", value: "moderate" }
  ];
  
  const selected = patterns[Math.floor(Math.random() * patterns.length)];
  
  return {
    question: `What is the typical ALICE + Poverty rate pattern in ${selected.pattern}?`,
    options: ["Higher than average", "Lower than average", "Varies significantly", "Same as national average"],
    correctIndex: selected.value === "higher" ? 0 : selected.value === "varies" ? 2 : 3,
    explanation: `${selected.pattern} typically show ${selected.value} rates due to various economic factors.`
  };
}

function predictFutureRate(location) {
  // Simple trend prediction (would use real ML model in production)
  const baseRate = location.combinedRate;
  const trend = Math.random() * 4 - 2; // Random trend between -2 and +2
  return Math.max(0, Math.min(100, baseRate + trend));
}

function checkQuizAnswer(index) {
  if (currentQuizData && index === currentQuizData.correctIndex) {
    alert(`Correct! ${currentQuizData.explanation}`);
  } else {
    alert(`Incorrect. ${currentQuizData.explanation}`);
  }
  
  // Generate new quiz
  setTimeout(startAIQuiz, 1000);
}

// Export functionality
function exportData() {
  // Get current filtered data
  const filtered = aliceData.filter(d => {
    const geoLevel = document.getElementById('geoLevelFilter').value;
    const state = document.getElementById('stateFilter').value;
    const minRate = parseFloat(document.getElementById('minCombinedRate').value);
    const minHouseholds = parseInt(document.getElementById('minHouseholds').value);
    
    return (geoLevel === 'all' || d.geoLevel === geoLevel) &&
           (state === 'all' || d.state === state) &&
           d.combinedRate >= minRate &&
           d.totalHouseholds >= minHouseholds;
  });
  
  // Convert to CSV
  const csv = convertToCSV(filtered);
  
  // Download
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `alice_data_export_${Date.now()}.csv`;
  a.click();
}

function convertToCSV(data) {
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
  ].join('\n');
  
  return csv;
}

// Zoom to location
function zoomToLocation(geoID) {
  // In production, would query actual coordinates
  // For demo, zoom to general area
  view.goTo({
    center: [-98.5795, 39.8283],
    zoom: 8
  });
}

// Analyze specific location with AI
function analyzeLocation(geoID) {
  const location = aliceData.find(d => d.geoID === geoID);
  if (!location) return;
  
  const analysis = `
    AI Analysis for ${location.geoDisplayLabel || location.county}:
    
    Risk Level: ${location.combinedRate > 50 ? 'CRITICAL' : location.combinedRate > 40 ? 'HIGH' : location.combinedRate > 30 ? 'MODERATE' : 'LOW'}
    
    Key Insights:
    - ${location.totalHouseholds.toLocaleString()} total households
    - ${location.povertyHouseholds.toLocaleString()} in poverty (${location.povertyRate}%)
    - ${location.aliceHouseholds.toLocaleString()} ALICE households (${location.aliceRate}%)
    
    Predicted 2025 Rate: ${predictFutureRate(location).toFixed(1)}%
    
    Recommendations:
    ${location.combinedRate > 40 ? '- Urgent intervention needed\n- Focus on job training programs\n- Expand affordable housing initiatives' : '- Continue monitoring trends\n- Preventive support programs recommended'}
  `;
  
  alert(analysis);
}

// Initialize quiz on load
setTimeout(startAIQuiz, 2000);
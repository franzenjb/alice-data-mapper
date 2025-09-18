// Global variables
let stateData = [];
let map = null;
let currentView = 'combined';
let stateMarkers = {};
let barChart = null;
let scatterChart = null;

// State coordinates for mapping
const stateCoordinates = {
    'alabama': [32.806671, -86.791130],
    'arkansas': [34.969704, -92.373123],
    'colorado': [39.059811, -105.311104],
    'connecticut': [41.597782, -72.755371],
    'delaware': [39.318523, -75.507141],
    'florida': [27.766279, -81.686783],
    'georgia': [33.040619, -83.643074],
    'hawaii': [21.094318, -157.498337],
    'idaho': [44.240459, -114.478828],
    'illinois': [40.349457, -88.986137],
    'indiana': [39.849426, -86.258278],
    'iowa': [42.011539, -93.210526],
    'kansas': [38.526600, -96.726486],
    'louisiana': [31.169546, -91.867805],
    'maine': [44.693947, -69.381927],
    'maryland': [39.063946, -76.802101],
    'michigan': [43.326618, -84.536095],
    'minnesota': [45.694454, -93.900192],
    'mississippi': [32.741646, -89.678696],
    'new-jersey': [40.298904, -74.521011],
    'new-mexico': [34.840515, -106.248482],
    'new-york': [42.165726, -74.948051],
    'north-carolina': [35.630066, -79.806419],
    'ohio': [40.388783, -82.764915],
    'oregon': [43.804133, -120.554201],
    'pennsylvania': [40.590752, -77.209755],
    'south-carolina': [33.856892, -80.945007],
    'tennessee': [35.747845, -86.692345],
    'texas': [31.054487, -97.563461],
    'virginia': [37.769337, -78.169968],
    'washington': [47.400902, -121.490494],
    'west-virginia': [38.491226, -80.954453]
};

// Initialize the application
async function init() {
    try {
        // Load state data
        const response = await fetch('alice_state_data.json');
        stateData = await response.json();
        
        // Calculate and display national statistics
        displayNationalStats();
        
        // Initialize map
        initMap();
        
        // Update state list
        updateStateList();
        
        // Create charts
        createCharts();
        
    } catch (error) {
        console.error('Error initializing application:', error);
        document.getElementById('stateList').innerHTML = '<div class="loading">Error loading data. Please refresh the page.</div>';
    }
}

// Display national statistics
function displayNationalStats() {
    const avgPoverty = stateData.reduce((sum, s) => sum + s.povertyRate, 0) / stateData.length;
    const avgAlice = stateData.reduce((sum, s) => sum + s.aliceRate, 0) / stateData.length;
    const avgCombined = stateData.reduce((sum, s) => sum + s.combinedRate, 0) / stateData.length;
    
    document.getElementById('avgPoverty').textContent = avgPoverty.toFixed(1) + '%';
    document.getElementById('avgAlice').textContent = avgAlice.toFixed(1) + '%';
    document.getElementById('avgCombined').textContent = avgCombined.toFixed(1) + '%';
}

// Initialize Leaflet map
function initMap() {
    // Create map centered on USA
    map = L.map('map').setView([39.8283, -98.5795], 4);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add state markers
    stateData.forEach(state => {
        const coords = stateCoordinates[state.id];
        if (coords) {
            const color = getColorForValue(state[currentView + 'Rate']);
            
            const marker = L.circleMarker(coords, {
                radius: 15,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            // Add popup
            marker.bindPopup(createPopupContent(state));
            
            // Add click event
            marker.on('click', () => selectState(state));
            
            // Store marker reference
            stateMarkers[state.id] = marker;
        }
    });
}

// Get color based on value
function getColorForValue(value) {
    if (value < 35) return '#2ECC71';
    if (value < 40) return '#F39C12';
    if (value < 45) return '#E67E22';
    return '#E74C3C';
}

// Create popup content
function createPopupContent(state) {
    return `
        <div style="padding: 10px;">
            <h3 style="margin: 0 0 10px 0;">${state.name}</h3>
            <div><strong>Poverty Rate:</strong> ${state.povertyRate}%</div>
            <div><strong>ALICE Rate:</strong> ${state.aliceRate}%</div>
            <div><strong>Combined Rate:</strong> ${state.combinedRate}%</div>
            <div style="margin-top: 10px;">
                <a href="${state.url}" target="_blank" style="color: #667eea;">View Full Report →</a>
            </div>
        </div>
    `;
}

// Update map view based on selected metric
function updateMapView(metric) {
    currentView = metric;
    
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(metric)) {
            btn.classList.add('active');
        }
    });
    
    // Update marker colors
    stateData.forEach(state => {
        const marker = stateMarkers[state.id];
        if (marker) {
            const color = getColorForValue(state[metric + 'Rate']);
            marker.setStyle({ fillColor: color });
        }
    });
}

// Update state list
function updateStateList() {
    const sortBy = document.getElementById('sortSelect').value;
    
    // Sort states
    const sortedStates = [...stateData].sort((a, b) => {
        if (sortBy === 'name') {
            return a.name.localeCompare(b.name);
        } else {
            return b[sortBy + 'Rate'] - a[sortBy + 'Rate'];
        }
    });
    
    // Generate HTML
    const listHTML = sortedStates.map((state, index) => `
        <div class="state-item" onclick="selectState('${state.id}')">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${index + 1}. ${state.name}</strong>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                        Combined: ${state.combinedRate}% | ALICE: ${state.aliceRate}% | Poverty: ${state.povertyRate}%
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('stateList').innerHTML = listHTML;
}

// Select a state
function selectState(stateId) {
    const state = typeof stateId === 'string' 
        ? stateData.find(s => s.id === stateId)
        : stateId;
    
    if (!state) return;
    
    // Update state info panel
    document.getElementById('stateInfo').innerHTML = `
        <div class="state-name">${state.name}</div>
        
        <div style="margin: 20px 0;">
            <div style="margin-bottom: 15px;">
                <strong>Poverty Rate: ${state.povertyRate}%</strong>
                <div class="progress-bar">
                    <div class="progress-fill poverty-fill" style="width: ${state.povertyRate}%">
                        ${state.povertyRate}%
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong>ALICE Rate: ${state.aliceRate}%</strong>
                <div class="progress-bar">
                    <div class="progress-fill alice-fill" style="width: ${state.aliceRate}%">
                        ${state.aliceRate}%
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong>Combined Rate: ${state.combinedRate}%</strong>
                <div class="progress-bar">
                    <div class="progress-fill combined-fill" style="width: ${state.combinedRate}%">
                        ${state.combinedRate}%
                    </div>
                </div>
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <h4 style="margin: 0 0 10px 0;">What This Means</h4>
            <p style="margin: 0; font-size: 0.9em; line-height: 1.5;">
                In ${state.name}, ${state.combinedRate}% of households struggle to afford basic necessities. 
                This includes ${state.povertyRate}% living below the poverty line and 
                ${state.aliceRate}% who are ALICE - working but unable to afford the basic cost of living.
            </p>
        </div>
        
        <div style="margin-top: 20px;">
            <a href="${state.url}" target="_blank" 
               style="display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; text-decoration: none; border-radius: 25px;">
                View Full State Report →
            </a>
        </div>
    `;
    
    // Center map on state
    const coords = stateCoordinates[state.id];
    if (coords && map) {
        map.setView(coords, 6);
        stateMarkers[state.id].openPopup();
    }
}

// Create charts
function createCharts() {
    // Prepare data
    const labels = stateData.map(s => s.abbreviation);
    const povertyData = stateData.map(s => s.povertyRate);
    const aliceData = stateData.map(s => s.aliceRate);
    const combinedData = stateData.map(s => s.combinedRate);
    
    // Bar Chart - Top 10 States by Combined Rate
    const top10States = [...stateData]
        .sort((a, b) => b.combinedRate - a.combinedRate)
        .slice(0, 10);
    
    const barCtx = document.getElementById('barChart').getContext('2d');
    barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: top10States.map(s => s.name),
            datasets: [
                {
                    label: 'Poverty Rate',
                    data: top10States.map(s => s.povertyRate),
                    backgroundColor: 'rgba(245, 87, 108, 0.7)',
                    borderColor: 'rgba(245, 87, 108, 1)',
                    borderWidth: 1
                },
                {
                    label: 'ALICE Rate',
                    data: top10States.map(s => s.aliceRate),
                    backgroundColor: 'rgba(79, 172, 254, 0.7)',
                    borderColor: 'rgba(79, 172, 254, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 States by Financial Hardship',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    max: 60,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Scatter Chart - Poverty vs ALICE Correlation
    const scatterCtx = document.getElementById('scatterChart').getContext('2d');
    scatterChart = new Chart(scatterCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'States',
                data: stateData.map(s => ({
                    x: s.povertyRate,
                    y: s.aliceRate,
                    label: s.name
                })),
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Poverty Rate vs ALICE Rate by State',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return `${point.label}: Poverty ${point.x}%, ALICE ${point.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Poverty Rate (%)'
                    },
                    beginAtZero: true,
                    max: 25
                },
                y: {
                    title: {
                        display: true,
                        text: 'ALICE Rate (%)'
                    },
                    beginAtZero: true,
                    max: 40
                }
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
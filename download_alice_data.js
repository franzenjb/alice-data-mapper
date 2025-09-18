const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

// All ALICE states with their data sheet URLs
const states = [
  { name: 'Alabama', url: '2025 ALICE - Alabama Data Sheet.xlsx' },
  { name: 'Arkansas', url: '2025 ALICE - Arkansas Data Sheet.xlsx' },
  { name: 'Colorado', url: '2025 ALICE - Colorado Data Sheet.xlsx' },
  { name: 'Connecticut', url: '2025 ALICE - Connecticut Data Sheet.xlsx' },
  { name: 'Delaware', url: '2025 ALICE - Delaware Data Sheet.xlsx' },
  { name: 'Florida', url: '2025 ALICE - Florida Data Sheet.xlsx' },
  { name: 'Georgia', url: '2025 ALICE - Georgia Data Sheet.xlsx' },
  { name: 'Hawaii', url: '2025 ALICE - Hawaii Data Sheet.xlsx' },
  { name: 'Idaho', url: '2025 ALICE - Idaho Data Sheet.xlsx' },
  { name: 'Illinois', url: '2025 ALICE - Illinois Data Sheet.xlsx' },
  { name: 'Indiana', url: '2025 ALICE - Indiana Data Sheet.xlsx' },
  { name: 'Iowa', url: '2025 ALICE - Iowa Data Sheet.xlsx' },
  { name: 'Kansas', url: '2025 ALICE - Kansas Data Sheet.xlsx' },
  { name: 'Louisiana', url: '2025 ALICE - Louisiana Data Sheet.xlsx' },
  { name: 'Maine', url: '2025 ALICE - Maine Data Sheet.xlsx' },
  { name: 'Maryland', url: '2025 ALICE - Maryland Data Sheet.xlsx' },
  { name: 'Michigan', url: '2025 ALICE - Michigan Data Sheet.xlsx' },
  { name: 'Minnesota', url: '2025 ALICE - Minnesota Data Sheet.xlsx' },
  { name: 'Mississippi', url: '2025 ALICE - Mississippi Data Sheet.xlsx' },
  { name: 'New Jersey', url: '2025 ALICE - New Jersey Data Sheet.xlsx' },
  { name: 'New Mexico', url: '2025 ALICE - New Mexico Data Sheet.xlsx' },
  { name: 'New York', url: '2025 ALICE - New York Data Sheet.xlsx' },
  { name: 'North Carolina', url: '2025 ALICE - North Carolina Data Sheet.xlsx' },
  { name: 'Ohio', url: '2025 ALICE - Ohio Data Sheet.xlsx' },
  { name: 'Oregon', url: '2025 ALICE - Oregon Data Sheet.xlsx' },
  { name: 'Pennsylvania', url: '2025 ALICE - Pennsylvania Data Sheet.xlsx' },
  { name: 'South Carolina', url: '2025 ALICE - South Carolina Data Sheet.xlsx' },
  { name: 'Tennessee', url: '2025 ALICE - Tennessee Data Sheet.xlsx' },
  { name: 'Texas', url: '2025 ALICE - Texas Data Sheet.xlsx' },
  { name: 'Virginia', url: '2025 ALICE - Virginia Data Sheet.xlsx' },
  { name: 'Washington', url: '2025 ALICE - Washington Data Sheet.xlsx' },
  { name: 'West Virginia', url: '2025 ALICE - West Virginia Data Sheet.xlsx' }
];

async function downloadStateData(state) {
  const baseUrl = 'https://www.unitedforalice.org/Attachments/StateDataSheet/';
  const encodedUrl = baseUrl + encodeURIComponent(state.url);
  const outputPath = path.join(__dirname, 'data', `${state.name.toLowerCase().replace(' ', '_')}_data.xlsx`);
  
  try {
    console.log(`Downloading ${state.name} data...`);
    const response = await axios({
      method: 'GET',
      url: encodedUrl,
      responseType: 'stream'
    });
    
    // Create data directory if it doesn't exist
    await fs.mkdir(path.join(__dirname, 'data'), { recursive: true });
    
    // Save the file
    const writer = require('fs').createWriteStream(outputPath);
    response.data.pipe(writer);
    
    return new Promise((resolve, reject) => {
      writer.on('finish', () => {
        console.log(`✓ Downloaded ${state.name}`);
        resolve();
      });
      writer.on('error', reject);
    });
    
  } catch (error) {
    console.error(`✗ Failed to download ${state.name}: ${error.message}`);
    return null;
  }
}

async function downloadAllStates() {
  console.log('Starting download of all ALICE state data sheets...\n');
  
  for (const state of states) {
    await downloadStateData(state);
    // Add delay to be respectful to the server
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n✓ Download complete!');
  console.log('Data saved in ./data directory');
  console.log('\nNote: These Excel files contain county-level data that can be extracted and converted to CSV.');
}

// Run the download
downloadAllStates().catch(console.error);
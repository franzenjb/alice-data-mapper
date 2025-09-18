const XLSX = require('xlsx');
const fs = require('fs').promises;
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

async function analyzeExcelStructure(filePath) {
  const workbook = XLSX.readFile(filePath);
  const analysis = {};
  
  workbook.SheetNames.forEach(sheetName => {
    const sheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(sheet, { header: 1 });
    
    if (data.length > 0) {
      analysis[sheetName] = {
        rows: data.length,
        columns: data[0].length,
        headers: data[0],
        sample: data.slice(0, 5)
      };
    }
  });
  
  return analysis;
}

async function extractAllGeographicData() {
  const dataDir = path.join(__dirname, 'data');
  const files = await fs.readdir(dataDir);
  const excelFiles = files.filter(f => f.endsWith('.xlsx'));
  
  console.log(`Found ${excelFiles.length} Excel files to analyze\n`);
  
  const allData = [];
  const geoLevels = new Set();
  
  for (const file of excelFiles) {
    const stateName = file.replace('_data.xlsx', '').replace('_', ' ');
    console.log(`\nAnalyzing ${stateName}...`);
    
    const filePath = path.join(dataDir, file);
    const workbook = XLSX.readFile(filePath);
    
    // Look for sheets with geographic data
    for (const sheetName of workbook.SheetNames) {
      const sheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(sheet);
      
      if (data.length > 0) {
        // Check for geographic identifiers
        const firstRow = data[0];
        const keys = Object.keys(firstRow);
        
        // Look for GeoID, FIPS, County, Tract, etc.
        const hasGeoID = keys.some(k => k.toLowerCase().includes('geoid') || k.toLowerCase().includes('fips'));
        const hasCounty = keys.some(k => k.toLowerCase().includes('county'));
        const hasTract = keys.some(k => k.toLowerCase().includes('tract'));
        const hasPUMA = keys.some(k => k.toLowerCase().includes('puma'));
        const hasZip = keys.some(k => k.toLowerCase().includes('zip'));
        
        if (hasGeoID || hasCounty || hasTract || hasPUMA || hasZip) {
          console.log(`  Found geographic data in sheet: ${sheetName}`);
          console.log(`    - GeoID/FIPS: ${hasGeoID}`);
          console.log(`    - County: ${hasCounty}`);
          console.log(`    - Tract: ${hasTract}`);
          console.log(`    - PUMA: ${hasPUMA}`);
          console.log(`    - ZIP: ${hasZip}`);
          console.log(`    - Rows: ${data.length}`);
          console.log(`    - Columns: ${keys.length}`);
          
          // Extract and standardize the data
          data.forEach(row => {
            const standardized = {
              state: stateName,
              sheet: sheetName,
              ...row
            };
            
            // Try to extract GeoID if present
            keys.forEach(key => {
              if (key.toLowerCase().includes('geoid') || key.toLowerCase().includes('fips')) {
                standardized.geoID = row[key];
                
                // Determine geographic level based on GeoID length
                if (standardized.geoID) {
                  const geoLength = standardized.geoID.toString().length;
                  if (geoLength === 2) standardized.geoLevel = 'state';
                  else if (geoLength === 5) standardized.geoLevel = 'county';
                  else if (geoLength === 11) standardized.geoLevel = 'tract';
                  else if (geoLength === 10) standardized.geoLevel = 'zip';
                  else standardized.geoLevel = 'unknown';
                  
                  geoLevels.add(standardized.geoLevel);
                }
              }
            });
            
            allData.push(standardized);
          });
        }
      }
    }
  }
  
  console.log(`\n=== SUMMARY ===`);
  console.log(`Total records extracted: ${allData.length}`);
  console.log(`Geographic levels found: ${Array.from(geoLevels).join(', ')}`);
  
  // Save to master CSV
  if (allData.length > 0) {
    const outputPath = path.join(__dirname, 'alice_master_geoid_data.csv');
    const headers = [...new Set(allData.flatMap(Object.keys))];
    
    const csvWriter = createObjectCsvWriter({
      path: outputPath,
      header: headers.map(h => ({ id: h, title: h }))
    });
    
    await csvWriter.writeRecords(allData);
    console.log(`\n✓ Master database saved to: ${outputPath}`);
  }
  
  return allData;
}

async function examineTexasDetail() {
  console.log('=== Examining Texas Data in Detail ===\n');
  const texasPath = path.join(__dirname, 'data', 'texas_data.xlsx');
  const analysis = await analyzeExcelStructure(texasPath);
  
  for (const [sheetName, info] of Object.entries(analysis)) {
    console.log(`\nSheet: ${sheetName}`);
    console.log(`Dimensions: ${info.rows} rows x ${info.columns} columns`);
    if (info.headers) {
      console.log('Headers:', info.headers.slice(0, 10).join(', '));
    }
  }
  
  return analysis;
}

// Main execution
async function main() {
  console.log('Starting deep geographic data extraction...\n');
  
  // First examine structure
  await examineTexasDetail();
  
  // Then extract all data
  const masterData = await extractAllGeographicData();
  
  // Create summary statistics
  const summary = {
    totalRecords: masterData.length,
    states: [...new Set(masterData.map(d => d.state))].length,
    geoLevels: {}
  };
  
  masterData.forEach(record => {
    if (record.geoLevel) {
      summary.geoLevels[record.geoLevel] = (summary.geoLevels[record.geoLevel] || 0) + 1;
    }
  });
  
  console.log('\n=== FINAL SUMMARY ===');
  console.log(JSON.stringify(summary, null, 2));
  
  // Save summary
  await fs.writeFile(
    path.join(__dirname, 'data_summary.json'),
    JSON.stringify(summary, null, 2)
  );
}

main().catch(console.error);
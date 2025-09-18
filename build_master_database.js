const XLSX = require('xlsx');
const fs = require('fs').promises;
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

async function buildMasterDatabase() {
  const dataDir = path.join(__dirname, 'data');
  const files = await fs.readdir(dataDir);
  const excelFiles = files.filter(f => f.endsWith('.xlsx'));
  
  console.log('Building Master ALICE Database with GeoID codes...\n');
  
  const masterDatabase = [];
  const geoStats = {
    totalRecords: 0,
    byGeoLevel: {},
    byState: {}
  };
  
  for (const file of excelFiles) {
    const stateName = file.replace('_data.xlsx', '').replace('_', ' ');
    const stateAbbr = file.split('_')[0].toUpperCase();
    console.log(`Processing ${stateName}...`);
    
    const filePath = path.join(dataDir, file);
    const workbook = XLSX.readFile(filePath);
    
    // Process County sheet
    if (workbook.SheetNames.includes('County')) {
      const countySheet = workbook.Sheets['County'];
      const countyData = XLSX.utils.sheet_to_json(countySheet);
      
      countyData.forEach(row => {
        if (row['GEO id2']) {
          const record = {
            // Geographic identifiers
            geoID: row['GEO id2'].toString().padStart(5, '0'), // Ensure 5-digit county FIPS
            geoLevel: 'county',
            geoDisplayLabel: row['GEO display_label'] || row['County'],
            state: row['State'],
            stateAbbr: row['State Abbr'],
            county: row['County'],
            year: row['Year'],
            
            // ALICE metrics
            totalHouseholds: parseInt(row['Households']) || 0,
            povertyHouseholds: parseInt(row['Poverty Households']) || 0,
            aliceHouseholds: parseInt(row['ALICE Households']) || 0,
            aboveAliceHouseholds: parseInt(row['Above ALICE Households']) || 0,
            
            // Calculate percentages
            povertyRate: 0,
            aliceRate: 0,
            combinedRate: 0,
            
            // Additional fields for demographics if available
            povertyHH_Black: parseInt(row['Poverty HH Black']) || null,
            povertyHH_Hispanic: parseInt(row['Poverty HH Hispanic']) || null,
            povertyHH_White: parseInt(row['Poverty HH White']) || null,
            aliceHH_Black: parseInt(row['ALICE HH Black']) || null,
            aliceHH_Hispanic: parseInt(row['ALICE HH Hispanic']) || null,
            aliceHH_White: parseInt(row['ALICE HH White']) || null,
            
            dataSource: 'County Sheet'
          };
          
          // Calculate rates
          if (record.totalHouseholds > 0) {
            record.povertyRate = ((record.povertyHouseholds / record.totalHouseholds) * 100).toFixed(1);
            record.aliceRate = ((record.aliceHouseholds / record.totalHouseholds) * 100).toFixed(1);
            record.combinedRate = (((record.povertyHouseholds + record.aliceHouseholds) / record.totalHouseholds) * 100).toFixed(1);
          }
          
          masterDatabase.push(record);
          geoStats.totalRecords++;
          geoStats.byGeoLevel['county'] = (geoStats.byGeoLevel['county'] || 0) + 1;
        }
      });
    }
    
    // Process Subcounty sheet (includes cities, towns, census designated places)
    if (workbook.SheetNames.includes('Subcounty')) {
      const subcountySheet = workbook.Sheets['Subcounty'];
      const subcountyData = XLSX.utils.sheet_to_json(subcountySheet);
      
      subcountyData.forEach(row => {
        if (row['GEO id2']) {
          const geoID = row['GEO id2'].toString();
          let geoLevel = 'subcounty';
          
          // Determine more specific geo level based on Type field
          if (row['Type']) {
            if (row['Type'].toLowerCase().includes('city')) geoLevel = 'city';
            else if (row['Type'].toLowerCase().includes('town')) geoLevel = 'town';
            else if (row['Type'].toLowerCase().includes('cdp')) geoLevel = 'cdp'; // Census Designated Place
            else if (row['Type'].toLowerCase().includes('tract')) geoLevel = 'tract';
          }
          
          // Determine by GeoID length if Type not available
          if (!row['Type'] && geoID.length === 11) {
            geoLevel = 'tract';
          }
          
          const record = {
            // Geographic identifiers
            geoID: geoID,
            geoLevel: geoLevel,
            geoType: row['Type'] || 'subcounty',
            geoDisplayLabel: row['GEO display_label'],
            state: row['State'],
            county: row['County'] || null,
            year: row['Year'],
            
            // ALICE metrics
            totalHouseholds: parseInt(row['Households']) || 0,
            povertyHouseholds: parseInt(row['Poverty Households']) || 0,
            aliceHouseholds: parseInt(row['ALICE Households']) || 0,
            aboveAliceHouseholds: parseInt(row['Above ALICE Households']) || 0,
            
            // Calculate percentages
            povertyRate: 0,
            aliceRate: 0,
            combinedRate: 0,
            
            dataSource: 'Subcounty Sheet'
          };
          
          // Calculate rates
          if (record.totalHouseholds > 0) {
            record.povertyRate = ((record.povertyHouseholds / record.totalHouseholds) * 100).toFixed(1);
            record.aliceRate = ((record.aliceHouseholds / record.totalHouseholds) * 100).toFixed(1);
            record.combinedRate = (((record.povertyHouseholds + record.aliceHouseholds) / record.totalHouseholds) * 100).toFixed(1);
          }
          
          masterDatabase.push(record);
          geoStats.totalRecords++;
          geoStats.byGeoLevel[geoLevel] = (geoStats.byGeoLevel[geoLevel] || 0) + 1;
        }
      });
    }
    
    geoStats.byState[stateName] = masterDatabase.filter(r => r.state === stateName).length;
  }
  
  console.log('\n=== DATABASE SUMMARY ===');
  console.log(`Total records: ${geoStats.totalRecords}`);
  console.log('\nRecords by Geographic Level:');
  Object.entries(geoStats.byGeoLevel).forEach(([level, count]) => {
    console.log(`  ${level}: ${count}`);
  });
  
  // Save master database to CSV
  const csvPath = path.join(__dirname, 'alice_master_database.csv');
  const csvWriter = createObjectCsvWriter({
    path: csvPath,
    header: [
      { id: 'geoID', title: 'GeoID' },
      { id: 'geoLevel', title: 'Geographic_Level' },
      { id: 'geoType', title: 'Geographic_Type' },
      { id: 'geoDisplayLabel', title: 'Location_Name' },
      { id: 'state', title: 'State' },
      { id: 'stateAbbr', title: 'State_Abbr' },
      { id: 'county', title: 'County' },
      { id: 'year', title: 'Year' },
      { id: 'totalHouseholds', title: 'Total_Households' },
      { id: 'povertyHouseholds', title: 'Poverty_Households' },
      { id: 'aliceHouseholds', title: 'ALICE_Households' },
      { id: 'aboveAliceHouseholds', title: 'Above_ALICE_Households' },
      { id: 'povertyRate', title: 'Poverty_Rate_Pct' },
      { id: 'aliceRate', title: 'ALICE_Rate_Pct' },
      { id: 'combinedRate', title: 'Combined_Rate_Pct' },
      { id: 'dataSource', title: 'Data_Source' }
    ]
  });
  
  await csvWriter.writeRecords(masterDatabase);
  console.log(`\n✓ Master database saved to: ${csvPath}`);
  
  // Save JSON version for web app
  const jsonPath = path.join(__dirname, 'alice_master_database.json');
  await fs.writeFile(jsonPath, JSON.stringify(masterDatabase, null, 2));
  console.log(`✓ JSON database saved to: ${jsonPath}`);
  
  // Save statistics
  await fs.writeFile(
    path.join(__dirname, 'database_statistics.json'),
    JSON.stringify(geoStats, null, 2)
  );
  
  return masterDatabase;
}

// Create aggregated statistics by geographic level
async function createAggregatedStats(database) {
  console.log('\nCreating aggregated statistics...');
  
  const aggregated = {
    national: {
      totalHouseholds: 0,
      povertyHouseholds: 0,
      aliceHouseholds: 0,
      aboveAliceHouseholds: 0
    },
    byState: {},
    byCounty: {},
    highestCombinedRate: [],
    lowestCombinedRate: []
  };
  
  // Process each record
  database.forEach(record => {
    if (record.geoLevel === 'county') {
      // National totals
      aggregated.national.totalHouseholds += record.totalHouseholds;
      aggregated.national.povertyHouseholds += record.povertyHouseholds;
      aggregated.national.aliceHouseholds += record.aliceHouseholds;
      aggregated.national.aboveAliceHouseholds += record.aboveAliceHouseholds;
      
      // State totals
      if (!aggregated.byState[record.state]) {
        aggregated.byState[record.state] = {
          totalHouseholds: 0,
          povertyHouseholds: 0,
          aliceHouseholds: 0,
          counties: []
        };
      }
      aggregated.byState[record.state].totalHouseholds += record.totalHouseholds;
      aggregated.byState[record.state].povertyHouseholds += record.povertyHouseholds;
      aggregated.byState[record.state].aliceHouseholds += record.aliceHouseholds;
      aggregated.byState[record.state].counties.push(record.county);
    }
  });
  
  // Calculate national rates
  aggregated.national.povertyRate = ((aggregated.national.povertyHouseholds / aggregated.national.totalHouseholds) * 100).toFixed(1);
  aggregated.national.aliceRate = ((aggregated.national.aliceHouseholds / aggregated.national.totalHouseholds) * 100).toFixed(1);
  aggregated.national.combinedRate = (((aggregated.national.povertyHouseholds + aggregated.national.aliceHouseholds) / aggregated.national.totalHouseholds) * 100).toFixed(1);
  
  // Find highest and lowest combined rates
  const sortedByRate = database
    .filter(r => r.geoLevel === 'county' && r.combinedRate > 0)
    .sort((a, b) => parseFloat(b.combinedRate) - parseFloat(a.combinedRate));
  
  aggregated.highestCombinedRate = sortedByRate.slice(0, 10).map(r => ({
    location: `${r.county}, ${r.stateAbbr || r.state}`,
    combinedRate: r.combinedRate,
    povertyRate: r.povertyRate,
    aliceRate: r.aliceRate,
    totalHouseholds: r.totalHouseholds
  }));
  
  aggregated.lowestCombinedRate = sortedByRate.slice(-10).reverse().map(r => ({
    location: `${r.county}, ${r.stateAbbr || r.state}`,
    combinedRate: r.combinedRate,
    povertyRate: r.povertyRate,
    aliceRate: r.aliceRate,
    totalHouseholds: r.totalHouseholds
  }));
  
  // Save aggregated statistics
  await fs.writeFile(
    path.join(__dirname, 'alice_aggregated_stats.json'),
    JSON.stringify(aggregated, null, 2)
  );
  
  console.log('✓ Aggregated statistics saved');
  console.log(`\nNational Statistics:`);
  console.log(`  Total Households: ${aggregated.national.totalHouseholds.toLocaleString()}`);
  console.log(`  Poverty Rate: ${aggregated.national.povertyRate}%`);
  console.log(`  ALICE Rate: ${aggregated.national.aliceRate}%`);
  console.log(`  Combined Rate: ${aggregated.national.combinedRate}%`);
  
  return aggregated;
}

// Main execution
async function main() {
  try {
    const database = await buildMasterDatabase();
    const stats = await createAggregatedStats(database);
    
    console.log('\n✓ Master ALICE Database Complete!');
    console.log('Files created:');
    console.log('  - alice_master_database.csv (for GIS import)');
    console.log('  - alice_master_database.json (for web app)');
    console.log('  - alice_aggregated_stats.json (summary statistics)');
    console.log('  - database_statistics.json (database metadata)');
    
  } catch (error) {
    console.error('Error building database:', error);
  }
}

main();
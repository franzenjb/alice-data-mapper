const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

const states = [
  'alabama', 'arkansas', 'colorado', 'connecticut', 'delaware',
  'florida', 'georgia', 'hawaii', 'idaho', 'illinois',
  'indiana', 'iowa', 'kansas', 'louisiana', 'maine',
  'maryland', 'michigan', 'minnesota', 'mississippi', 'new-jersey',
  'new-mexico', 'new-york', 'north-carolina', 'ohio', 'oregon',
  'pennsylvania', 'south-carolina', 'tennessee', 'texas', 'virginia',
  'washington', 'west-virginia'
];

async function scrapeStateData(browser, stateName) {
  const page = await browser.newPage();
  const url = `https://www.unitedforalice.org/${stateName}`;
  
  try {
    console.log(`Scraping ${stateName}...`);
    await page.goto(url, { waitUntil: 'networkidle' });
    
    const stateData = await page.evaluate(() => {
      const data = {
        stateName: '',
        povertyRate: null,
        aliceRate: null,
        combinedRate: null,
        totalHouseholds: null,
        aliceHouseholds: null,
        povertyHouseholds: null,
        aboveAliceHouseholds: null,
        survivalBudget: {},
        dataYear: null
      };
      
      // Extract state name
      const titleElement = document.querySelector('h1, .state-title, [class*="title"]');
      if (titleElement) {
        data.stateName = titleElement.textContent.trim();
      }
      
      // Look for percentage data
      const textContent = document.body.textContent;
      const percentageMatches = textContent.match(/(\d+)%/g);
      const numberMatches = textContent.match(/(\d{1,3},?\d{3,})/g);
      
      // Try to find specific ALICE data patterns
      const alicePattern = /ALICE.*?(\d+)%/i;
      const povertyPattern = /poverty.*?(\d+)%/i;
      const combinedPattern = /below.*?ALICE.*?threshold.*?(\d+)%/i;
      
      const aliceMatch = textContent.match(alicePattern);
      const povertyMatch = textContent.match(povertyPattern);
      const combinedMatch = textContent.match(combinedPattern);
      
      if (aliceMatch) data.aliceRate = parseInt(aliceMatch[1]);
      if (povertyMatch) data.povertyRate = parseInt(povertyMatch[1]);
      if (combinedMatch) data.combinedRate = parseInt(combinedMatch[1]);
      
      // Extract year if available
      const yearMatch = textContent.match(/20\d{2}/);
      if (yearMatch) data.dataYear = yearMatch[0];
      
      // Look for household numbers
      if (numberMatches && numberMatches.length > 0) {
        data.totalHouseholds = numberMatches[0];
      }
      
      return data;
    });
    
    await page.close();
    return { ...stateData, stateName: stateName, url };
    
  } catch (error) {
    console.error(`Error scraping ${stateName}:`, error.message);
    await page.close();
    return null;
  }
}

async function main() {
  console.log('Starting ALICE data scraper...');
  const browser = await chromium.launch({ headless: true });
  
  const allStateData = [];
  
  for (const state of states) {
    const data = await scrapeStateData(browser, state);
    if (data) {
      allStateData.push(data);
      console.log(`✓ Scraped ${state}: ${data.povertyRate}% poverty, ${data.aliceRate}% ALICE, ${data.combinedRate}% total`);
    }
    // Add a small delay to be respectful to the server
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  await browser.close();
  
  // Save the data
  await fs.writeFile(
    path.join(__dirname, 'alice_data.json'),
    JSON.stringify(allStateData, null, 2)
  );
  
  console.log(`\n✓ Scraping complete! Data saved to alice_data.json`);
  console.log(`Total states scraped: ${allStateData.length}`);
  
  return allStateData;
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main, scrapeStateData };
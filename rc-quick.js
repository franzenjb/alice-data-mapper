#!/usr/bin/env node

// Red Cross Quick Login - TESTED AND WORKING VERSION
const { chromium } = require('playwright');
const readline = require('readline');
const fs = require('fs');
const path = require('path');
const os = require('os');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const configFile = path.join(os.homedir(), '.rcquick');

async function setup() {
    console.log('🔧 Quick Login Setup\n');
    
    const username = await question('Red Cross email: ');
    const password = await question('Red Cross password: ');
    const quickCode = await question('Quick code (like "red" or "123"): ');
    
    const config = Buffer.from(JSON.stringify({
        u: username,
        p: password,
        q: quickCode
    })).toString('base64');
    
    fs.writeFileSync(configFile, config);
    console.log('\n✅ Setup complete! Run script again to login.');
    process.exit(0);
}

async function login() {
    // Check for config
    if (!fs.existsSync(configFile)) {
        await setup();
        return;
    }
    
    const config = JSON.parse(Buffer.from(fs.readFileSync(configFile, 'utf8'), 'base64').toString());
    
    // Get quick code
    const code = await question('Quick code: ');
    if (code !== config.q) {
        console.log('❌ Invalid code');
        process.exit(1);
    }
    
    console.log('\n🚀 Launching browser...');
    
    const browser = await chromium.launch({
        headless: false,
        args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Go to ArcGIS portal
        console.log('📍 Opening Red Cross ArcGIS...');
        await page.goto('https://arc-nhq-gis.maps.arcgis.com/home/signin.html', {
            waitUntil: 'networkidle'
        });
        
        // Step 2: Click American Red Cross button
        console.log('📍 Selecting Red Cross organization...');
        await page.waitForTimeout(2000);
        
        // This selector works - I tested it!
        const redCrossButton = await page.locator('text="American Red Cross, National Headquarters"');
        if (await redCrossButton.isVisible()) {
            await redCrossButton.click();
            console.log('✅ Clicked Red Cross button');
        }
        
        // Step 3: Wait for SSO page
        console.log('⏳ Waiting for SSO page...');
        await page.waitForURL('**/redcross.org/sso/**', { timeout: 10000 });
        
        // Step 4: Fill credentials
        console.log('📍 Entering credentials...');
        await page.fill('input[type="email"], input#email', config.u);
        await page.fill('input[type="password"], input#password', config.p);
        
        // Step 5: Submit
        await page.click('button[type="submit"], input[type="submit"]');
        
        console.log('\n✅ Credentials submitted!');
        console.log('🔐 Complete 2FA if prompted');
        console.log('⌨️  Press Ctrl+C when done\n');
        
        // Keep open
        await new Promise(() => {});
        
    } catch (error) {
        console.log('⚠️  Error:', error.message);
        console.log('Complete login manually in the browser');
        await new Promise(() => {});
    }
}

function question(prompt) {
    return new Promise(resolve => rl.question(prompt, resolve));
}

process.on('SIGINT', () => {
    console.log('\n👋 Goodbye!');
    process.exit(0);
});

// Run
login().catch(console.error);
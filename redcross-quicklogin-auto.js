#!/usr/bin/env node

// Red Cross Quick Login Automation
// This script handles the two-step process automatically

const { chromium } = require('playwright');
const readline = require('readline');

// Configuration
const CONFIG = {
    urls: {
        arcgisSignin: 'https://arc-nhq-gis.maps.arcgis.com/home/signin.html',
        redcrossOrg: 'American Red Cross, National Headquarters'
    }
};

// Create readline interface for password input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function askQuestion(question) {
    return new Promise(resolve => rl.question(question, resolve));
}

async function quickLogin() {
    console.log('🔴 Red Cross Quick Login Tool');
    console.log('==============================\n');
    
    // Get quick code
    const quickCode = await askQuestion('Enter quick code: ');
    
    // Check stored credentials
    const fs = require('fs');
    const path = require('path');
    const configFile = path.join(require('os').homedir(), '.rcquicklogin');
    
    let credentials;
    try {
        const data = fs.readFileSync(configFile, 'utf8');
        credentials = JSON.parse(Buffer.from(data, 'base64').toString());
        
        if (credentials.quick !== quickCode) {
            console.log('❌ Invalid quick code');
            process.exit(1);
        }
    } catch (e) {
        console.log('⚠️  No credentials found. Running setup...\n');
        await setupCredentials(configFile);
        return;
    }
    
    console.log('\n🚀 Launching browser...');
    
    const browser = await chromium.launch({
        headless: false,
        args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Go to ArcGIS signin
        console.log('📍 Step 1: Opening ArcGIS portal...');
        await page.goto(CONFIG.urls.arcgisSignin, {
            waitUntil: 'networkidle',
            timeout: 30000
        });
        
        // Step 2: Click "American Red Cross, National Headquarters"
        console.log('📍 Step 2: Selecting Red Cross organization...');
        
        // Wait for and click the Red Cross button
        const redCrossButton = await page.locator('button', { hasText: 'American Red Cross' }).first();
        
        if (await redCrossButton.isVisible({ timeout: 5000 })) {
            await redCrossButton.click();
            console.log('✅ Clicked Red Cross organization button');
        } else {
            console.log('⚠️  Could not find Red Cross button - please click it manually');
        }
        
        // Wait for redirect to redcross.org SSO
        console.log('⏳ Waiting for Red Cross SSO page...');
        await page.waitForURL('**/redcross.org/sso/**', {
            timeout: 30000
        });
        
        // Step 3: Fill credentials on Red Cross SSO page
        console.log('📍 Step 3: Entering credentials...');
        
        // Fill email
        await page.fill('input[type="email"], input[name="email"], input#email', credentials.username);
        
        // Fill password
        await page.fill('input[type="password"], input[name="password"], input#password', credentials.password);
        
        // Click sign in
        await page.click('button[type="submit"], input[type="submit"], button:has-text("SIGN IN")');
        
        console.log('\n✅ Credentials submitted!');
        console.log('🔐 Complete 2FA in the browser if prompted');
        console.log('⏰ Browser will stay open for you to use\n');
        console.log('Press Ctrl+C to close when done');
        
        // Keep browser open
        await new Promise(() => {});
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log('\n💡 You can complete the login manually in the browser');
    }
    
    rl.close();
}

async function setupCredentials(configFile) {
    console.log('🔧 First-time setup\n');
    
    const username = await askQuestion('Red Cross email: ');
    const password = await askQuestion('Red Cross password: ');
    const quickCode = await askQuestion('Choose a quick code (simple word/number): ');
    
    const credentials = {
        username: username,
        password: password,
        quick: quickCode
    };
    
    // Encode and save
    const fs = require('fs');
    const encoded = Buffer.from(JSON.stringify(credentials)).toString('base64');
    fs.writeFileSync(configFile, encoded);
    
    console.log('\n✅ Credentials saved!');
    console.log('Run the script again to use quick login');
    
    rl.close();
    process.exit(0);
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
    console.log('\n👋 Closing...');
    rl.close();
    process.exit(0);
});

// Run
quickLogin().catch(error => {
    console.error('Fatal error:', error);
    rl.close();
    process.exit(1);
});
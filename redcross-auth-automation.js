// Red Cross ArcGIS Authentication Automation Script
// This script uses Playwright to automate the Red Cross ArcGIS login process

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration - You can store these in environment variables for security
const CONFIG = {
    username: process.env.REDCROSS_USERNAME || '',
    password: process.env.REDCROSS_PASSWORD || '',
    headless: false, // Set to false so you can see the browser and handle 2FA if needed
    saveSession: true,
    sessionFile: path.join(__dirname, 'redcross-session.json')
};

class RedCrossArcGISAuth {
    constructor(config = CONFIG) {
        this.config = config;
        this.browser = null;
        this.context = null;
        this.page = null;
    }

    async initialize() {
        // Launch browser
        this.browser = await chromium.launch({
            headless: this.config.headless,
            args: ['--disable-blink-features=AutomationControlled']
        });

        // Try to load existing session
        let sessionData = null;
        if (this.config.saveSession) {
            try {
                const sessionContent = await fs.readFile(this.config.sessionFile, 'utf-8');
                sessionData = JSON.parse(sessionContent);
                console.log('📂 Loaded existing session');
            } catch (e) {
                console.log('🆕 No existing session found, will create new one');
            }
        }

        // Create context with session if available
        if (sessionData && sessionData.cookies) {
            this.context = await this.browser.newContext({
                storageState: sessionData,
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            });
        } else {
            this.context = await this.browser.newContext({
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            });
        }

        this.page = await this.context.newPage();
    }

    async login() {
        try {
            console.log('🚀 Starting Red Cross ArcGIS authentication...');

            // Navigate to the ArcGIS Online page
            await this.page.goto('https://www.arcgis.com/home/signin.html', {
                waitUntil: 'networkidle'
            });

            // Check if already logged in
            const isLoggedIn = await this.checkIfLoggedIn();
            if (isLoggedIn) {
                console.log('✅ Already authenticated!');
                return true;
            }

            // Step 1: Handle organization selection
            console.log('📍 Step 1: Selecting Red Cross organization...');
            
            // Look for the enterprise login option
            const enterpriseButton = await this.page.locator('text=Your ArcGIS organization\'s URL').first();
            if (await enterpriseButton.isVisible()) {
                await enterpriseButton.click();
            }

            // Enter Red Cross organization URL
            await this.page.fill('input[placeholder*="organization"]', 'redcross');
            await this.page.press('input[placeholder*="organization"]', 'Enter');

            // Wait for redirect to Red Cross SSO
            await this.page.waitForNavigation({ waitUntil: 'networkidle' });

            // Look for the "American Red Cross" button
            const redCrossButton = await this.page.locator('button:has-text("American Red Cross")').first();
            if (await redCrossButton.isVisible()) {
                console.log('📍 Found Red Cross organization button');
                await redCrossButton.click();
                await this.page.waitForNavigation({ waitUntil: 'networkidle' });
            }

            // Step 2: Handle Red Cross login form
            console.log('📍 Step 2: Entering credentials...');
            
            // Wait for username field
            await this.page.waitForSelector('input[type="text"], input[name="username"], input#username', {
                timeout: 10000
            });

            // Fill credentials
            const usernameField = await this.page.locator('input[type="text"], input[name="username"], input#username').first();
            const passwordField = await this.page.locator('input[type="password"], input[name="password"], input#password').first();

            if (this.config.username && this.config.password) {
                await usernameField.fill(this.config.username);
                await passwordField.fill(this.config.password);
                
                // Check for "Keep me signed in" checkbox
                const keepSignedIn = await this.page.locator('input[type="checkbox"]').first();
                if (await keepSignedIn.isVisible()) {
                    await keepSignedIn.check();
                }

                // Submit form
                const submitButton = await this.page.locator('button[type="submit"], input[type="submit"], button:has-text("Sign In")').first();
                await submitButton.click();

                console.log('⏳ Waiting for authentication...');
                
                // Wait for navigation or 2FA prompt
                try {
                    await this.page.waitForNavigation({ 
                        waitUntil: 'networkidle',
                        timeout: 30000 
                    });
                } catch (e) {
                    console.log('⚠️ Navigation timeout - checking for 2FA...');
                }

                // Check for 2FA
                const needs2FA = await this.check2FA();
                if (needs2FA) {
                    console.log('🔐 2FA Required - Please complete authentication in the browser');
                    console.log('⏰ Waiting up to 2 minutes for 2FA completion...');
                    
                    // Wait for user to complete 2FA
                    await this.page.waitForFunction(
                        () => window.location.href.includes('arcgis.com') && !window.location.href.includes('signin'),
                        { timeout: 120000 }
                    );
                }

                // Verify successful login
                const loginSuccess = await this.checkIfLoggedIn();
                if (loginSuccess) {
                    console.log('✅ Authentication successful!');
                    
                    // Save session
                    if (this.config.saveSession) {
                        await this.saveSession();
                    }
                    
                    return true;
                }
            } else {
                console.log('⚠️ No credentials provided');
                console.log('👤 Please enter your credentials manually in the browser');
                
                // Wait for manual login
                await this.page.waitForFunction(
                    () => window.location.href.includes('arcgis.com') && !window.location.href.includes('signin'),
                    { timeout: 300000 } // 5 minutes for manual login
                );
                
                console.log('✅ Manual authentication completed!');
                
                // Save session
                if (this.config.saveSession) {
                    await this.saveSession();
                }
                
                return true;
            }

        } catch (error) {
            console.error('❌ Authentication failed:', error.message);
            return false;
        }
    }

    async checkIfLoggedIn() {
        try {
            // Check if we're on the ArcGIS home page and logged in
            const url = this.page.url();
            if (url.includes('arcgis.com') && !url.includes('signin')) {
                // Look for user menu or profile indicator
                const userMenu = await this.page.locator('[aria-label*="user"], [class*="user-menu"], [class*="esri-identity"]').first();
                return await userMenu.isVisible();
            }
            return false;
        } catch (e) {
            return false;
        }
    }

    async check2FA() {
        try {
            // Check for common 2FA indicators
            const twoFAIndicators = [
                'text=Two-Factor',
                'text=Verification Code',
                'text=Authenticator',
                'input[placeholder*="code"]',
                'text=Enter code'
            ];

            for (const indicator of twoFAIndicators) {
                const element = await this.page.locator(indicator).first();
                if (await element.isVisible()) {
                    return true;
                }
            }
            return false;
        } catch (e) {
            return false;
        }
    }

    async saveSession() {
        try {
            const storageState = await this.context.storageState();
            await fs.writeFile(this.config.sessionFile, JSON.stringify(storageState, null, 2));
            console.log('💾 Session saved for future use');
        } catch (error) {
            console.error('Failed to save session:', error.message);
        }
    }

    async getToken() {
        try {
            // Execute JavaScript to get the token from the page
            const token = await this.page.evaluate(() => {
                // Try various methods to get the token
                if (window.require && window.require('esri/identity/IdentityManager')) {
                    const IdentityManager = window.require('esri/identity/IdentityManager');
                    const credential = IdentityManager.findCredential('https://www.arcgis.com/sharing/rest');
                    return credential ? credential.token : null;
                }
                
                // Check localStorage
                const keys = Object.keys(localStorage);
                for (const key of keys) {
                    if (key.includes('token') || key.includes('credential')) {
                        try {
                            const value = localStorage.getItem(key);
                            const parsed = JSON.parse(value);
                            if (parsed.token) return parsed.token;
                        } catch (e) {}
                    }
                }
                
                return null;
            });

            if (token) {
                console.log('🎫 Retrieved authentication token');
                return token;
            }

            // Alternative: Get token from network requests
            const response = await this.page.evaluate(async () => {
                const resp = await fetch('https://www.arcgis.com/sharing/rest/portals/self?f=json', {
                    credentials: 'include'
                });
                return await resp.json();
            });

            if (response.user) {
                console.log('🎫 User authenticated as:', response.user.username);
                return true;
            }

            return null;
        } catch (error) {
            console.error('Failed to get token:', error.message);
            return null;
        }
    }

    async navigateToApp(appUrl) {
        console.log(`📱 Navigating to application: ${appUrl}`);
        await this.page.goto(appUrl, { waitUntil: 'networkidle' });
        
        // Inject token if needed
        const token = await this.getToken();
        if (token) {
            await this.page.evaluate((token) => {
                // Store token for the app to use
                window.arcgisToken = token;
                sessionStorage.setItem('arcgisToken', token);
            }, token);
        }
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Main execution
async function main() {
    const auth = new RedCrossArcGISAuth({
        username: process.env.REDCROSS_USERNAME || '', // Set these in your environment
        password: process.env.REDCROSS_PASSWORD || '',
        headless: false, // Keep browser visible for 2FA
        saveSession: true
    });

    try {
        await auth.initialize();
        const success = await auth.login();
        
        if (success) {
            // Navigate to your ALICE Data Map
            await auth.navigateToApp('https://franzenjb.github.io/alice-data-mapper/arcgis-choropleth-trends.html');
            
            console.log('🎉 Application loaded with authentication!');
            console.log('👀 You can now interact with the map in the browser');
            console.log('❌ Press Ctrl+C to close the browser when done');
            
            // Keep browser open
            await new Promise(() => {});
        }
    } catch (error) {
        console.error('Error:', error);
        await auth.close();
    }
}

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = RedCrossArcGISAuth;
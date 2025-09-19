// Red Cross ArcGIS Authentication Automation v2
// Handles the full two-step authentication flow

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
    username: process.env.REDCROSS_USERNAME || '',
    password: process.env.REDCROSS_PASSWORD || '',
    headless: false, // Keep browser visible for 2FA
    saveSession: true,
    sessionFile: path.join(__dirname, 'redcross-session.json'),
    urls: {
        arcgisPortal: 'https://arc-nhq-gis.maps.arcgis.com',
        redcrossSSO: 'https://www.redcross.org/sso/',
        targetApp: 'https://franzenjb.github.io/alice-data-mapper/arcgis-redcross-direct.html'
    }
};

class RedCrossAuth {
    constructor(config = CONFIG) {
        this.config = config;
        this.browser = null;
        this.context = null;
        this.page = null;
    }

    async initialize() {
        console.log('🚀 Initializing browser...');
        
        // Launch browser
        this.browser = await chromium.launch({
            headless: this.config.headless,
            args: [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
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
                userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            });
        } else {
            this.context = await this.browser.newContext({
                userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            });
        }

        this.page = await this.context.newPage();
        
        // Log console messages for debugging
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('Browser console error:', msg.text());
            }
        });
    }

    async checkIfLoggedIn() {
        try {
            // Navigate to Red Cross ArcGIS portal
            await this.page.goto(`${this.config.urls.arcgisPortal}/home/`, {
                waitUntil: 'networkidle',
                timeout: 30000
            });

            // Check if we're logged in by looking for user menu
            const userMenu = await this.page.locator('[class*="user-menu"], [aria-label*="user"], #logged-in-user').first();
            const isVisible = await userMenu.isVisible({ timeout: 5000 }).catch(() => false);
            
            if (isVisible) {
                console.log('✅ Already logged in!');
                return true;
            }
            
            return false;
        } catch (e) {
            return false;
        }
    }

    async login() {
        try {
            console.log('🔴 Starting Red Cross ArcGIS authentication...');

            // Check if already logged in
            if (await this.checkIfLoggedIn()) {
                return true;
            }

            // Step 1: Navigate to the Red Cross ArcGIS portal
            console.log('📍 Step 1: Navigating to Red Cross ArcGIS portal...');
            await this.page.goto(`${this.config.urls.arcgisPortal}/home/signin.html`, {
                waitUntil: 'networkidle',
                timeout: 60000
            });

            // Wait for the page to load
            await this.page.waitForTimeout(2000);

            // Look for "American Red Cross" button or organization selector
            console.log('📍 Looking for Red Cross organization button...');
            
            // Try multiple selectors for the Red Cross button
            const selectors = [
                'button:has-text("American Red Cross")',
                'text=American Red Cross, National Headquarters',
                '[aria-label*="American Red Cross"]',
                'button.esri-identity-form-account',
                'a[href*="redcross.org/sso"]'
            ];

            let clicked = false;
            for (const selector of selectors) {
                try {
                    const element = await this.page.locator(selector).first();
                    if (await element.isVisible({ timeout: 5000 })) {
                        console.log(`📍 Found Red Cross selector: ${selector}`);
                        await element.click();
                        clicked = true;
                        break;
                    }
                } catch (e) {
                    // Continue to next selector
                }
            }

            if (!clicked) {
                console.log('⚠️ Could not find Red Cross button automatically');
                console.log('👤 Please click "American Red Cross, National Headquarters" manually');
                
                // Wait for navigation to Red Cross SSO
                await this.page.waitForURL('**/redcross.org/sso/**', {
                    timeout: 60000
                });
            } else {
                // Wait for redirect to Red Cross SSO
                await this.page.waitForURL('**/redcross.org/sso/**', {
                    timeout: 30000
                });
            }

            console.log('📍 Step 2: Reached Red Cross SSO login page');

            // Step 2: Fill in Red Cross credentials
            if (this.config.username && this.config.password) {
                console.log('📍 Entering credentials...');
                
                // Wait for and fill email field
                await this.page.waitForSelector('input[type="email"], input[name="email"], input#email', {
                    timeout: 10000
                });
                
                const emailField = await this.page.locator('input[type="email"], input[name="email"], input#email').first();
                await emailField.fill(this.config.username);
                
                // Fill password field
                const passwordField = await this.page.locator('input[type="password"], input[name="password"], input#password').first();
                await passwordField.fill(this.config.password);
                
                // Click sign in button
                const signInButton = await this.page.locator('button[type="submit"], input[type="submit"], button:has-text("SIGN IN")').first();
                await signInButton.click();
                
                console.log('⏳ Waiting for authentication...');
                
                // Wait for either:
                // 1. Redirect back to ArcGIS (successful login)
                // 2. 2FA prompt
                // 3. Error message
                
                try {
                    await Promise.race([
                        this.page.waitForURL('**/arc-nhq-gis.maps.arcgis.com/**', { timeout: 30000 }),
                        this.page.waitForSelector('input[placeholder*="code"], text=Two-Factor, text=Verification', { timeout: 5000 })
                    ]);
                } catch (e) {
                    // Check if we need 2FA
                    const needs2FA = await this.check2FA();
                    if (needs2FA) {
                        console.log('🔐 2FA Required - Please complete authentication in the browser');
                        console.log('⏰ Waiting up to 2 minutes for 2FA completion...');
                        
                        // Wait for redirect back to ArcGIS after 2FA
                        await this.page.waitForURL('**/arc-nhq-gis.maps.arcgis.com/**', {
                            timeout: 120000
                        });
                    }
                }
                
                // Verify successful login
                console.log('🔍 Verifying authentication...');
                await this.page.waitForTimeout(3000);
                
                if (await this.checkIfLoggedIn()) {
                    console.log('✅ Authentication successful!');
                    
                    // Save session
                    if (this.config.saveSession) {
                        await this.saveSession();
                    }
                    
                    return true;
                }
                
            } else {
                console.log('⚠️ No credentials provided');
                console.log('👤 Please complete the login manually');
                console.log('⏰ Waiting up to 5 minutes for manual login...');
                
                // Wait for manual login completion
                await this.page.waitForURL('**/arc-nhq-gis.maps.arcgis.com/home/**', {
                    timeout: 300000
                });
                
                if (await this.checkIfLoggedIn()) {
                    console.log('✅ Manual authentication successful!');
                    
                    // Save session
                    if (this.config.saveSession) {
                        await this.saveSession();
                    }
                    
                    return true;
                }
            }

            return false;

        } catch (error) {
            console.error('❌ Authentication error:', error.message);
            console.log('💡 Tip: You can complete the login manually in the browser window');
            
            // Keep browser open for manual intervention
            console.log('⏰ Browser will remain open for manual login...');
            await this.page.waitForTimeout(300000); // 5 minutes
            
            return false;
        }
    }

    async check2FA() {
        try {
            const indicators = [
                'text=Two-Factor',
                'text=Verification Code',
                'text=Enter the code',
                'input[placeholder*="code"]',
                'text=Authenticator'
            ];

            for (const indicator of indicators) {
                const element = await this.page.locator(indicator).first();
                if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
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

    async navigateToApp() {
        console.log(`📱 Navigating to ALICE Data Map...`);
        await this.page.goto(this.config.urls.targetApp, {
            waitUntil: 'networkidle'
        });
        
        console.log('🎉 Application loaded!');
        console.log('👀 You can now use the map in the browser');
        console.log('❌ Press Ctrl+C to close when done');
    }

    async keepAlive() {
        // Keep the browser open
        await new Promise(() => {});
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Main execution
async function main() {
    const auth = new RedCrossAuth();

    try {
        await auth.initialize();
        const success = await auth.login();
        
        if (success) {
            await auth.navigateToApp();
            await auth.keepAlive();
        } else {
            console.log('❌ Authentication was not successful');
            console.log('💡 You can try again or complete the login manually in the browser');
            await auth.keepAlive();
        }
    } catch (error) {
        console.error('Fatal error:', error);
        await auth.close();
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n👋 Closing browser...');
    process.exit(0);
});

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = RedCrossAuth;
# ArcGIS Authentication Standard for Red Cross Applications

## Security-First Approach

This authentication method should be used as the standard for all ArcGIS applications to ensure:
- No hardcoded credentials
- Support for multiple users
- Proper 2FA handling
- Session management

## Implementation Components

### 1. HTML Authentication Page Template

```html
<!-- Standard Red Cross ArcGIS Authentication -->
<script src="https://js.arcgis.com/4.28/"></script>

<script>
require([
    "esri/identity/OAuthInfo",
    "esri/identity/IdentityManager",
    "esri/portal/Portal"
], function(OAuthInfo, IdentityManager, Portal) {
    
    // Red Cross Portal Configuration
    const redcrossInfo = new OAuthInfo({
        appId: "arcgisonline",
        portalUrl: "https://arc-nhq-gis.maps.arcgis.com",
        popup: true,
        popupCallbackUrl: "https://arc-nhq-gis.maps.arcgis.com/home/accountswitcher-callback.html"
    });
    
    // Standard ArcGIS Fallback
    const standardInfo = new OAuthInfo({
        appId: "YjvdaQPiEsXpnJMH", // Replace with your app ID
        portalUrl: "https://www.arcgis.com",
        popup: true,
        popupCallbackUrl: window.location.href.replace(/[^/]*$/, 'oauth-callback.html')
    });
    
    IdentityManager.registerOAuthInfos([redcrossInfo, standardInfo]);
});
</script>
```

### 2. Playwright Automation Template

```javascript
// Standard Red Cross Authentication Flow
class RedCrossAuth {
    async login() {
        // Step 1: Navigate to Red Cross Portal
        await page.goto('https://arc-nhq-gis.maps.arcgis.com/home/signin.html');
        
        // Step 2: Click "American Red Cross, National Headquarters"
        await page.click('text=American Red Cross, National Headquarters');
        
        // Step 3: Handle redirect to redcross.org/sso
        await page.waitForURL('**/redcross.org/sso/**');
        
        // Step 4: User enters credentials manually (SECURE)
        console.log('Please enter your credentials in the browser');
        
        // Step 5: Save session for future use
        await context.storageState({ path: 'session.json' });
    }
}
```

### 3. Session Management

```javascript
// Check for existing session
if (fs.existsSync('redcross-session.json')) {
    // Load saved session
    context = await browser.newContext({
        storageState: 'redcross-session.json'
    });
    // User stays logged in
}
```

## Benefits Over Hardcoded Login

1. **Security**: No credentials in code
2. **Compliance**: Meets Red Cross security requirements
3. **Multi-user**: Each user uses their own account
4. **Audit Trail**: Proper user attribution
5. **2FA Support**: Manual intervention for security codes

## Migration Checklist

When updating existing applications:

- [ ] Remove all hardcoded credentials
- [ ] Remove automatic login code
- [ ] Add manual authentication flow
- [ ] Implement session persistence
- [ ] Add user info display
- [ ] Test with multiple users

## Standard File Structure

```
/your-app/
├── index.html                 # Main application
├── oauth-callback.html        # OAuth callback handler
├── redcross-auth.js          # Authentication automation
├── run-auth.sh               # Shell script runner
└── redcross-session.json     # Saved session (git-ignored)
```

## Important URLs

- Red Cross Portal: `https://arc-nhq-gis.maps.arcgis.com`
- Red Cross SSO: `https://www.redcross.org/sso/`
- OAuth Callback: `https://arc-nhq-gis.maps.arcgis.com/home/accountswitcher-callback.html`

## Usage Instructions

1. **First Time**:
   - Run authentication script
   - Browser opens
   - Enter Red Cross credentials
   - Complete 2FA
   - Session saved

2. **Subsequent Uses**:
   - Run authentication script
   - Session loaded automatically
   - No login required

3. **Session Expired**:
   - Automatically prompts for re-login
   - Complete 2FA again
   - New session saved

## Security Best Practices

1. **Never** commit session files to git
2. **Always** use manual 2FA
3. **Rotate** sessions periodically
4. **Monitor** authentication logs
5. **Test** with non-admin accounts

## Support

For Red Cross ArcGIS portal issues, contact GIS team.
For authentication flow issues, check browser console for errors.
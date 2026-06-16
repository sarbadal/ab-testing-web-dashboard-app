# Dynamic URL Configuration Guide

This guide explains how to configure and use the dynamic URL system for the A/B 
Testing Dashboard, which allows you to easily manage different environments 
(development, staging, production) with environment-specific URL prefixes.

## Overview

The dynamic URL system uses a **single URL prefix** that automatically applies to 
all routes in your Flask application. This is implemented using Flask Blueprints 
to ensure all routes (login, logout, dashboard, API endpoints, static files) 
automatically get the configured prefix.

## Key Components

1. **Environment Configuration** (`.env` file) - Single `URL_PREFIX` variable
2. **Flask Blueprint** (`app.py`) - Automatically applies prefix to all routes
3. **Context Processor** (`app/config.py`) - Injects URL configuration into templates
4. **JavaScript URL Builder** (`static/js/url-builder.js`) - Client-side URL building

## Environment Configuration

### Simple Setup

Just set **one variable** in your `.env` file:

```bash
# Production deployment in subdirectory
URL_PREFIX=/ab-testing-app-002

# Development (root deployment)  
URL_PREFIX=

# Staging environment
URL_PREFIX=/staging
```

### What Gets Generated

With `URL_PREFIX=/ab-testing-app-002`, you automatically get:

- **Routes:** `/ab-testing-app-002/login`, `/ab-testing-app-002/logout`, `/ab-testing-app-002/dashboard`
- **API:** `/ab-testing-app-002/api/data`
- **Static:** `/ab-testing-app-002/static/js/script.js`

With `URL_PREFIX=` (empty), you get:

- **Routes:** `/login`, `/logout`, `/dashboard`
- **API:** `/api/data`
- **Static:** `/static/js/script.js`

## Using URLs in Templates

### Automatic URL Injection

All templates automatically receive a `url_config` object with the following structure:

```jinja2
{{ url_config.env_type }}           <!-- 'dev', 'staging', or 'prod' -->
{{ url_config.api_base_url }}       <!-- '/ab-testing-app-002/api/data' -->
{{ url_config.app_base_url }}       <!-- '/ab-testing-app-002' -->
{{ url_config.static_base_url }}    <!-- '/ab-testing-app-002/static' -->

<!-- Predefined URLs -->
{{ url_config.urls.api_data }}      <!-- API data endpoint -->
{{ url_config.urls.app_login }}     <!-- Login route -->
{{ url_config.urls.app_logout }}    <!-- Logout route -->
{{ url_config.urls.app_dashboard }} <!-- Dashboard route -->
```

### Example Template Usage

```html
<!-- Static assets -->
<script src="{{ url_config.static_base_url }}/js/url-builder.js"></script>
<link href="{{ url_config.static_base_url }}/css/styles.css" rel="stylesheet">

<!-- Navigation links -->
<a href="{{ url_config.urls.app_logout }}">Logout</a>
<a href="{{ url_config.urls.app_dashboard }}">Dashboard</a>

<!-- API endpoints in JavaScript -->
<script>
    window.urlBuilder = new URLBuilder({{ url_config|tojson }});
</script>
```

## Using URLs in JavaScript

### URL Builder Class

The `URLBuilder` class provides powerful client-side URL management:

```javascript
// Initialize (automatically done in templates)
const urlBuilder = new URLBuilder(urlConfig);

// Build API URLs
const apiUrl = urlBuilder.buildApiUrl('dashboard', {test: 'A', date: '2023-10-01'});
// Result: '/ab-testing-app-002/api/data/dashboard?test=A&date=2023-10-01'

// Build application URLs
const loginUrl = urlBuilder.buildAppUrl('login');
// Result: '/ab-testing-app-002/login'

// Build static asset URLs
const cssUrl = urlBuilder.buildStaticUrl('css/styles.css');
// Result: '/ab-testing-app-002/static/css/styles.css'

// Get predefined URLs
const logoutUrl = urlBuilder.getUrl('app_logout');
// Result: '/ab-testing-app-002/logout'
```

### Making API Calls

```javascript
// Using the built-in fetch method
try {
    const response = await urlBuilder.fetchApi('dashboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }, { test: 'A', date: '2023-10-01' });
    
    const result = await response.json();
} catch (error) {
    console.error('API call failed:', error);
}

// Manual URL building
const apiUrl = urlBuilder.buildApiUrl('data', { test: 'Homepage Redesign' });
const response = await fetch(apiUrl);
```

### Navigation

```javascript
// Navigate to a route
urlBuilder.navigate('dashboard', { test: 'A' }); // Redirects to dashboard with params
urlBuilder.navigate('login', {}, true); // Replace current history entry
```

## Backward Compatibility

The system maintains backward compatibility with existing code:

```javascript
// Legacy variables still work
console.log(window.API_BASE_URL); // Still available
console.log(apiBaseUrl); // Still available

// Legacy functions still work
const url1 = buildApiUrl('data', { test: 'A' });
const url2 = buildAppUrl('login');
```

## Environment-Specific Features

### Development Mode

In development (`ENV_TYPE=dev`), the system provides:
- Enhanced debugging output
- Automatic configuration logging
- Detailed error messages

### Production Mode

In production (`ENV_TYPE=prod`), the system provides:
- Reduced logging
- Optimized performance
- Error handling fallbacks

## Best Practices

1. **Always use environment variables** for URL configuration instead of hardcoding
2. **Test in all environments** before deploying
3. **Use the URL builder** for all dynamic URL generation in JavaScript
4. **Leverage predefined URLs** when available instead of building manually
5. **Check the environment type** for conditional behavior

## Troubleshooting

### Common Issues

1. **URLs not working after deployment**
   - Check that `.env` file has correct values for your environment
   - Verify `APP_BASE_URL` matches your deployment path

2. **Static assets not loading**
   - Ensure `STATIC_BASE_URL` is correctly configured
   - Check that static files are accessible at the configured path

3. **API calls failing**
   - Verify `API_BASE_URL` points to the correct endpoint
   - Check browser developer tools for actual URLs being called

### Debug Commands

```javascript
// Check current configuration
window.urlBuilder.logConfiguration();

// Test API connectivity
window.testAPI();

// Check environment info
console.log(window.urlBuilder.getEnvironmentInfo());
```

## Migration from Legacy System

To migrate existing code:

1. Replace hardcoded URLs with environment variables
2. Update templates to use `url_config` object
3. Replace manual URL concatenation with URL builder methods
4. Test thoroughly in all environments

Example migration:

```javascript
// Old way
const apiUrl = '/ab-testing-app-002/api/data?test=' + testName;

// New way
const apiUrl = urlBuilder.buildApiUrl('', { test: testName });
```
/**
 * URL Configuration Helper for A/B Testing Dashboard
 * 
 * This module provides dynamic URL building capabilities based on 
 * environment configuration passed from the Flask backend.
 */

class URLBuilder {
    constructor(config) {
        this.config = config || {};
        this.baseConfig = {
            env_type: this.config.env_type || 'dev',
            api_base_url: this.config.api_base_url || '/api/data',
            app_base_url: this.config.app_base_url || '',
            static_base_url: this.config.static_base_url || '/static',
            external_api_url: this.config.external_api_url || '',
            urls: this.config.urls || {}
        };
        
        // Debug information
        this.debug = this.baseConfig.env_type === 'dev';
        
        if (this.debug) {
            console.log('URLBuilder initialized with config:', this.baseConfig);
        }
    }
    
    /**
     * Build an API URL for a specific endpoint
     * @param {string} endpoint - The API endpoint (e.g., 'dashboard', 'users')
     * @param {Object} params - Query parameters to append
     * @returns {string} Complete API URL
     */
    buildApiUrl(endpoint = '', params = {}) {
        let url = this.baseConfig.api_base_url;
        
        if (endpoint) {
            url += endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        }
        
        if (Object.keys(params).length > 0) {
            const searchParams = new URLSearchParams(params);
            url += `?${searchParams.toString()}`;
        }
        
        if (this.debug) {
            console.log(`buildApiUrl(${endpoint}, ${JSON.stringify(params)}) -> ${url}`);
        }
        
        return url;
    }
    
    /**
     * Build an application URL for navigation
     * @param {string} route - The application route (e.g., 'login', 'dashboard')
     * @param {Object} params - Query parameters to append
     * @returns {string} Complete application URL
     */
    buildAppUrl(route = '', params = {}) {
        let url = this.baseConfig.app_base_url;
        
        if (route) {
            const cleanRoute = route.startsWith('/') ? route : `/${route}`;
            url += cleanRoute;
        } else if (!url) {
            url = '/';
        }
        
        if (Object.keys(params).length > 0) {
            const searchParams = new URLSearchParams(params);
            url += `?${searchParams.toString()}`;
        }
        
        if (this.debug) {
            console.log(`buildAppUrl(${route}, ${JSON.stringify(params)}) -> ${url}`);
        }
        
        return url;
    }
    
    /**
     * Build a static asset URL
     * @param {string} filename - The static file name or path
     * @returns {string} Complete static asset URL
     */
    buildStaticUrl(filename) {
        const cleanFilename = filename.startsWith('/') ? filename.substring(1) : filename;
        const url = `${this.baseConfig.static_base_url}/${cleanFilename}`;
        
        if (this.debug) {
            console.log(`buildStaticUrl(${filename}) -> ${url}`);
        }
        
        return url;
    }
    
    /**
     * Get a predefined URL from the configuration
     * @param {string} key - The URL key (e.g., 'api_data', 'app_login')
     * @returns {string} The predefined URL
     */
    getUrl(key) {
        const url = this.baseConfig.urls[key];
        
        if (!url && this.debug) {
            console.warn(`URL key '${key}' not found in configuration`);
        }
        
        return url || '';
    }
    
    /**
     * Perform a fetch request with automatic URL building
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options (method, headers, body, etc.)
     * @param {Object} params - Query parameters
     * @returns {Promise} Fetch promise
     */
    async fetchApi(endpoint, options = {}, params = {}) {
        const url = this.buildApiUrl(endpoint, params);
        
        // Set default headers
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        if (this.debug) {
            console.log(`fetchApi: ${defaultOptions.method || 'GET'} ${url}`, defaultOptions);
        }
        
        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, url: ${url}`);
            }
            
            return response;
        } catch (error) {
            console.error('fetchApi error:', error);
            throw error;
        }
    }
    
    /**
     * Navigate to an application route
     * @param {string} route - The route to navigate to
     * @param {Object} params - Query parameters
     * @param {boolean} replace - Whether to replace the current history entry
     */
    navigate(route, params = {}, replace = false) {
        const url = this.buildAppUrl(route, params);
        
        if (replace) {
            window.location.replace(url);
        } else {
            window.location.href = url;
        }
    }
    
    /**
     * Get current environment information
     * @returns {Object} Environment information
     */
    getEnvironmentInfo() {
        return {
            env_type: this.baseConfig.env_type,
            is_development: this.baseConfig.env_type === 'dev',
            is_staging: this.baseConfig.env_type === 'staging',
            is_production: this.baseConfig.env_type === 'prod',
            debug_mode: this.debug
        };
    }
    
    /**
     * Log current configuration (for debugging)
     */
    logConfiguration() {
        console.group('URLBuilder Configuration');
        console.log('Environment:', this.baseConfig.env_type);
        console.log('API Base URL:', this.baseConfig.api_base_url);
        console.log('App Base URL:', this.baseConfig.app_base_url || '(root)');
        console.log('Static Base URL:', this.baseConfig.static_base_url);
        console.log('Predefined URLs:', this.baseConfig.urls);
        console.groupEnd();
    }
}

// Backward compatibility functions for existing code
function buildApiUrl(endpoint = '', params = {}) {
    return window.urlBuilder ? window.urlBuilder.buildApiUrl(endpoint, params) : `/api/data${endpoint ? '/' + endpoint : ''}`;
}

function buildAppUrl(route = '', params = {}) {
    return window.urlBuilder ? window.urlBuilder.buildAppUrl(route, params) : `/${route}`;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = URLBuilder;
}

// Global object for browser usage
if (typeof window !== 'undefined') {
    window.URLBuilder = URLBuilder;
    window.buildApiUrl = buildApiUrl;
    window.buildAppUrl = buildAppUrl;
}
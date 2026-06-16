"""
Configuration module for URL management across different environments.
This module provides environment-based URL configuration for the A/B Testing Dashboard.
"""

import os


class URLConfig:
    """Centralized URL configuration based on environment variables."""
    
    def __init__(self):
        self.env_type = os.getenv('ENV_TYPE', 'dev')
        
        # Simple URL prefix that applies to all endpoints
        self.url_prefix = os.getenv('URL_PREFIX', '').rstrip('/')
        
        # Build all URLs using the prefix
        self.api_base_url = f"{self.url_prefix}/api/data" if self.url_prefix else '/api/data'
        self.app_base_url = self.url_prefix
        self.static_base_url = f"{self.url_prefix}/static" if self.url_prefix else '/static'
        
        # External API (not affected by prefix)
        self.external_api_url = os.getenv('EXTERNAL_API_URL', '')
        
    def get_api_url(self, endpoint=''):
        """Get the complete API URL for a given endpoint."""
        if endpoint:
            return f"{self.api_base_url}/{endpoint.lstrip('/')}"
        return self.api_base_url
    
    def get_app_url(self, endpoint=''):
        """Get the complete app URL for a given endpoint."""
        if self.app_base_url:
            return f"{self.app_base_url}/{endpoint.lstrip('/')}" if endpoint else self.app_base_url
        return f"/{endpoint.lstrip('/')}" if endpoint else "/"
    
    def get_static_url(self, filename):
        """Get the complete static file URL."""
        return f"{self.static_base_url}/{filename.lstrip('/')}"
    
    def to_dict(self):
        """Convert configuration to dictionary for template context."""
        return {
            'env_type': self.env_type,
            'url_prefix': self.url_prefix,
            'api_base_url': self.api_base_url,
            'app_base_url': self.app_base_url,
            'static_base_url': self.static_base_url,
            'external_api_url': self.external_api_url,
            'urls': {
                'api_data': self.api_base_url,
                'api_dashboard': f"{self.api_base_url}/dashboard",
                'app_login': f"{self.url_prefix}/login" if self.url_prefix else '/login',
                'app_logout': f"{self.url_prefix}/logout" if self.url_prefix else '/logout',
                'app_dashboard': f"{self.url_prefix}/dashboard" if self.url_prefix else '/dashboard',
                'app_home': self.url_prefix if self.url_prefix else '/'
            }
        }


def create_context_processor(app):
    """Create a template context processor that injects URL configuration."""
    url_config = URLConfig()
    
    @app.context_processor
    def inject_url_config():
        """Inject URL configuration into all templates."""
        config_dict = url_config.to_dict()
        return {
            'url_config': config_dict,
            'API_BASE_URL': config_dict['api_base_url'],  # Backward compatibility
            'ENV_TYPE': config_dict['env_type'],  # Backward compatibility
            'env_type': config_dict['env_type']   # Already exists
        }
    
    return url_config
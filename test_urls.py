#!/usr/bin/env python3
"""
Test script to verify URL prefix configuration.
This script tests all URL generation to ensure they include the proper prefix.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

def test_url_configuration():
    """Test URL configuration with different prefix settings."""
    
    # Load environment variables
    load_dotenv()
    
    from app.config import URLConfig
    
    print("=== URL Configuration Test ===\n")
    
    # Test current configuration
    config = URLConfig()
    print(f"Current Environment: {config.env_type}")
    print(f"URL Prefix: '{config.url_prefix}' {'(empty - root deployment)' if not config.url_prefix else ''}")
    print()
    
    # Display all generated URLs
    print("Generated URLs:")
    print(f"  API Base URL: {config.api_base_url}")
    print(f"  App Base URL: {config.app_base_url}")
    print(f"  Static Base URL: {config.static_base_url}")
    print()
    
    # Test URL building methods
    print("URL Building Methods:")
    print(f"  API endpoint '/data': {config.get_api_url('data')}")
    print(f"  App route '/login': {config.get_app_url('login')}")
    print(f"  Static file 'css/style.css': {config.get_static_url('css/style.css')}")
    print()
    
    # Test predefined URLs
    url_dict = config.to_dict()
    print("Predefined URLs:")
    for key, value in url_dict['urls'].items():
        print(f"  {key}: {value}")
    print()
    
    # Test with different prefix values
    print("=== Testing Different Prefix Values ===")
    
    test_prefixes = [
        ('', 'Root deployment'),
        ('/ab-testing-app-002', 'Production subdirectory'),
        ('/staging', 'Staging environment'),
        ('/dev/v1', 'Development with version'),
    ]
    
    for prefix, description in test_prefixes:
        print(f"\n{description} (URL_PREFIX='{prefix}'):")
        
        # Temporarily set the prefix
        original_prefix = os.environ.get('URL_PREFIX', '')
        os.environ['URL_PREFIX'] = prefix
        
        test_config = URLConfig()
        
        print(f"  Login URL: {test_config.get_app_url('login')}")
        print(f"  API Data URL: {test_config.api_base_url}")
        print(f"  Static CSS URL: {test_config.get_static_url('css/main.css')}")
        
        # Restore original prefix
        os.environ['URL_PREFIX'] = original_prefix
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_url_configuration()
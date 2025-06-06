#!/usr/bin/env python3
"""
Test how our application reads the API key
Run this to see what's wrong with our settings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_config():
    """Test how our application reads configuration"""
    
    print("🔧 Application Configuration Test")
    print("=" * 40)
    
    # Test 1: Direct environment variable
    print("\n1. Testing direct environment variable:")
    env_key = os.getenv('NVD_API_KEY')
    if env_key:
        print(f"   ✅ Found in environment: {env_key[:8]}...{env_key[-4:]}")
        print(f"   📏 Length: {len(env_key)}")
    else:
        print("   ❌ Not found in environment")
    
    # Test 2: Load .env file manually
    print("\n2. Testing .env file loading:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        env_key_after_dotenv = os.getenv('NVD_API_KEY')
        if env_key_after_dotenv:
            print(f"   ✅ Found after loading .env: {env_key_after_dotenv[:8]}...{env_key_after_dotenv[-4:]}")
        else:
            print("   ❌ Not found after loading .env")
    except ImportError:
        print("   ⚠️  python-dotenv not installed")
    
    # Test 3: Our settings module
    print("\n3. Testing our settings module:")
    try:
        from config.settings import settings
        settings_key = getattr(settings, 'nvd_api_key', None)
        if settings_key:
            print(f"   ✅ Found in settings: {settings_key[:8]}...{settings_key[-4:]}")
            print(f"   📏 Length: {len(settings_key)}")
            print(f"   🔍 Type: {type(settings_key)}")
        else:
            print("   ❌ Not found in settings")
            
        # Print all settings for debugging
        print("\n   🔍 All settings attributes:")
        for attr in dir(settings):
            if not attr.startswith('_') and not callable(getattr(settings, attr)):
                value = getattr(settings, attr)
                if 'key' in attr.lower() or 'api' in attr.lower():
                    if value and len(str(value)) > 10:
                        print(f"      {attr}: {str(value)[:8]}...{str(value)[-4:]}")
                    else:
                        print(f"      {attr}: {value}")
                        
    except Exception as e:
        print(f"   ❌ Error loading settings: {e}")
    
    # Test 4: Check .env file directly
    print("\n4. Testing .env file directly:")
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            
        nvd_lines = [line for line in env_content.split('\n') if 'NVD_API_KEY' in line]
        if nvd_lines:
            for line in nvd_lines:
                if not line.strip().startswith('#'):
                    print(f"   📄 .env line: {line}")
                    if '=' in line:
                        key_part = line.split('=', 1)[1].strip()
                        if key_part:
                            print(f"   🔑 Key value: {key_part[:8]}...{key_part[-4:]}")
        else:
            print("   ❌ No NVD_API_KEY line found in .env")
            
    except FileNotFoundError:
        print("   ❌ .env file not found")
    except Exception as e:
        print(f"   ❌ Error reading .env: {e}")
    
    # Test 5: Test our NVD service initialization
    print("\n5. Testing NVD service initialization:")
    try:
        from app.services.nvd_search_service import NVDSearchService
        service = NVDSearchService()
        if service.api_key:
            print(f"   ✅ Service has API key: {service.api_key[:8]}...{service.api_key[-4:]}")
            print(f"   ⏱️  Rate limit: {service.rate_limit_delay} seconds")
        else:
            print("   ❌ Service has no API key")
    except Exception as e:
        print(f"   ❌ Error creating service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_config()

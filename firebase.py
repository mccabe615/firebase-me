#!/usr/bin/env python3
"""
Firebase Public Access Checker

A command-line tool to check if a Firebase Realtime Database instance
is publicly accessible (readable without authentication).

Usage:
    python firebase_checker.py <firebase_url>
    python firebase_checker.py https://your-project-default-rtdb.firebaseio.com/

Requirements:
    pip install requests
"""

import argparse
import sys
import requests
import json
from urllib.parse import urlparse
import time

class FirebaseChecker:
    def __init__(self, firebase_url):
        self.firebase_url = firebase_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Firebase-Public-Checker/1.0'
        })
    
    def normalize_url(self):
        """Ensure the Firebase URL is properly formatted"""
        if not self.firebase_url.startswith('http'):
            self.firebase_url = 'https://' + self.firebase_url
        
        # Parse URL to validate it
        parsed = urlparse(self.firebase_url)
        if not parsed.netloc:
            raise ValueError("Invalid Firebase URL format")
        
        # Ensure it's a Firebase URL
        if 'firebaseio.com' not in parsed.netloc and 'firebasedatabase.app' not in parsed.netloc:
            print(f"⚠️  Warning: URL doesn't appear to be a Firebase database URL")
        
        return self.firebase_url

    def check_public_read_access(self):
        """Check if the Firebase database allows public read access"""
        test_endpoints = [
            '.json',  # Root access
            '/.json?shallow=true',  # Shallow read
            '/test.json',  # Test path
        ]
        
        results = {}
        
        for endpoint in test_endpoints:
            url = self.firebase_url + endpoint
            try:
                print(f"Testing: {url}")
                response = self.session.get(url, timeout=10)
                
                results[endpoint] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'response_size': len(response.content),
                    'content_type': response.headers.get('Content-Type', 'unknown')
                }
                
                # If we get data back, try to parse it
                if response.status_code == 200 and response.content:
                    try:
                        data = response.json()
                        results[endpoint]['has_data'] = data is not None and data != {}
                        results[endpoint]['data_type'] = type(data).__name__
                    except json.JSONDecodeError:
                        results[endpoint]['has_data'] = False
                        results[endpoint]['data_type'] = 'invalid_json'
                
                # Add delay between requests to be respectful
                time.sleep(0.5)
                
            except requests.exceptions.Timeout:
                results[endpoint] = {'error': 'Request timed out'}
                print(f"❌ Timeout for {url}")
            except requests.exceptions.ConnectionError:
                results[endpoint] = {'error': 'Connection error'}
                print(f"❌ Connection error for {url}")
            except Exception as e:
                results[endpoint] = {'error': str(e)}
                print(f"❌ Error for {url}: {e}")
        
        return results

    def check_public_write_access(self):
        """Check if the Firebase database allows public write access"""
        test_url = f"{self.firebase_url}/security_test_{int(time.time())}.json"
        test_data = {"test": "security_check", "timestamp": int(time.time())}
        
        try:
            print(f"Testing write access: {test_url}")
            response = self.session.put(test_url, json=test_data, timeout=10)
            
            write_result = {
                'status_code': response.status_code,
                'writable': response.status_code in [200, 201],
                'response': response.text[:200] if response.text else ''
            }
            
            # If write succeeded, try to clean up
            if write_result['writable']:
                try:
                    self.session.delete(test_url, timeout=5)
                    print("✅ Cleaned up test data")
                except:
                    print("⚠️  Could not clean up test data")
            
            return write_result
            
        except Exception as e:
            return {'error': str(e)}

    def generate_report(self, read_results, write_result):
        """Generate a comprehensive security report"""
        print("\n" + "="*60)
        print("🔍 FIREBASE SECURITY ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📍 Database URL: {self.firebase_url}")
        
        # Analyze read access
        public_readable = any(result.get('accessible', False) for result in read_results.values())
        has_data = any(result.get('has_data', False) for result in read_results.values())
        
        print(f"\n📖 READ ACCESS:")
        if public_readable:
            print("❌ PUBLICLY READABLE - No authentication required!")
            if has_data:
                print("⚠️  Database contains data that is publicly accessible")
            else:
                print("ℹ️  Database is empty or contains null values")
        else:
            print("✅ Read access properly restricted")
        
        # Analyze write access
        print(f"\n✏️  WRITE ACCESS:")
        if write_result.get('writable', False):
            print("❌ PUBLICLY WRITABLE - Anyone can modify data!")
            print("🚨 CRITICAL SECURITY RISK!")
        elif write_result.get('error'):
            print(f"⚠️  Could not test write access: {write_result['error']}")
        else:
            print("✅ Write access properly restricted")
        
        # Overall security status
        print(f"\n🛡️  OVERALL SECURITY STATUS:")
        if public_readable or write_result.get('writable', False):
            print("🚨 INSECURE - Immediate action required!")
            print("\n💡 RECOMMENDATIONS:")
            print("   1. Review Firebase Security Rules")
            print("   2. Implement proper authentication")
            print("   3. Restrict database access to authenticated users only")
            print("   4. Monitor database access logs")
        else:
            print("✅ Database appears to be properly secured")
        
        # Detailed results
        print(f"\n📊 DETAILED RESULTS:")
        for endpoint, result in read_results.items():
            print(f"\n   Endpoint: {endpoint}")
            if 'error' in result:
                print(f"     Status: Error - {result['error']}")
            else:
                print(f"     Status Code: {result['status_code']}")
                print(f"     Accessible: {result['accessible']}")
                print(f"     Has Data: {result.get('has_data', 'N/A')}")
        
        return public_readable or write_result.get('writable', False)

def main():
    parser = argparse.ArgumentParser(
        description='Check if a Firebase Realtime Database instance is publicly accessible',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python firebase_checker.py https://my-project-default-rtdb.firebaseio.com/
  python firebase_checker.py my-project-default-rtdb.firebaseio.com
  python firebase_checker.py https://my-project-default-rtdb.europe-west1.firebasedatabase.app/

Note: This tool only checks for basic public access. It does not test all
possible security configurations or authentication methods.
        """
    )
    
    parser.add_argument('firebase_url', 
                       help='Firebase Realtime Database URL')
    parser.add_argument('--skip-write-test', 
                       action='store_true',
                       help='Skip testing write access (faster, less intrusive)')
    parser.add_argument('--timeout', 
                       type=int, 
                       default=10,
                       help='Request timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    try:
        # Create checker instance
        checker = FirebaseChecker(args.firebase_url)
        
        # Normalize and validate URL
        normalized_url = checker.normalize_url()
        print(f"🔍 Checking Firebase database: {normalized_url}")
        
        # Check read access
        print(f"\n📖 Testing read access...")
        read_results = checker.check_public_read_access()
        
        # Check write access (unless skipped)
        write_result = {}
        if not args.skip_write_test:
            print(f"\n✏️  Testing write access...")
            write_result = checker.check_public_write_access()
        else:
            print(f"\n✏️  Skipping write access test")
        
        # Generate report
        is_insecure = checker.generate_report(read_results, write_result)
        
        # Exit with appropriate code
        sys.exit(1 if is_insecure else 0)
        
    except ValueError as e:
        print(f"❌ Invalid URL: {e}")
        sys.exit(2)
    except KeyboardInterrupt:
        print(f"\n⏹️  Check cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

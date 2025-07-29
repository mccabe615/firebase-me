# Firebase Public Access Checker

A command-line security tool to check if Firebase Realtime Database instances are publicly accessible without authentication. This tool helps identify potential security vulnerabilities in Firebase configurations that could expose sensitive data.

## 🚨 Security Warning

This tool is designed for **legitimate security testing purposes only**. Only use it on Firebase databases that you own or have explicit permission to test. Unauthorized access to databases may violate terms of service and applicable laws.

## 🎯 What It Does

The Firebase Public Access Checker tests for common security misconfigurations by:

- **Read Access Testing**: Attempts to read data from various database endpoints without authentication
- **Write Access Testing**: Tests if the database accepts unauthenticated write operations
- **Security Analysis**: Provides detailed reports with actionable security recommendations
- **Multiple Endpoint Testing**: Checks root access, shallow reads, and specific paths

## 📋 Requirements

- Python 3.6 or higher
- `requests` library

## 🚀 Installation

1. **Clone or download** the `firebase_checker.py` script

2. **Install dependencies**:
   ```bash
   pip install requests
   ```

3. **Make the script executable** (optional):
   ```bash
   chmod +x firebase_checker.py
   ```

## 💻 Usage

### Basic Usage

```bash
python firebase_checker.py <firebase_url>
```

### Examples

```bash
# Test a Firebase Realtime Database
python firebase_checker.py https://my-project-default-rtdb.firebaseio.com/

# Works with different Firebase regions
python firebase_checker.py https://my-project-default-rtdb.europe-west1.firebasedatabase.app/

# URL without https:// (automatically added)
python firebase_checker.py my-project-default-rtdb.firebaseio.com

# Skip write testing for faster, less intrusive checks
python firebase_checker.py --skip-write-test https://my-project-default-rtdb.firebaseio.com/

# Custom timeout (useful for slow connections)
python firebase_checker.py --timeout 15 https://my-project-default-rtdb.firebaseio.com/
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `firebase_url` | Firebase Realtime Database URL (required) | - |
| `--skip-write-test` | Skip testing write access | False |
| `--timeout` | Request timeout in seconds | 10 |
| `--help` | Show help message | - |

## 📊 Output Examples

### Secure Database
```
🔍 Checking Firebase database: https://secure-project-default-rtdb.firebaseio.com

📖 Testing read access...
Testing: https://secure-project-default-rtdb.firebaseio.com/.json
Testing: https://secure-project-default-rtdb.firebaseio.com/.json?shallow=true
Testing: https://secure-project-default-rtdb.firebaseio.com/test.json

✏️  Testing write access...
Testing write access: https://secure-project-default-rtdb.firebaseio.com/security_test_1690123456.json

============================================================
🔍 FIREBASE SECURITY ANALYSIS REPORT
============================================================

📍 Database URL: https://secure-project-default-rtdb.firebaseio.com

📖 READ ACCESS:
✅ Read access properly restricted

✏️  WRITE ACCESS:
✅ Write access properly restricted

🛡️  OVERALL SECURITY STATUS:
✅ Database appears to be properly secured
```

### Vulnerable Database
```
🔍 Checking Firebase database: https://vulnerable-project-default-rtdb.firebaseio.com

📖 Testing read access...
Testing: https://vulnerable-project-default-rtdb.firebaseio.com/.json
Testing: https://vulnerable-project-default-rtdb.firebaseio.com/.json?shallow=true
Testing: https://vulnerable-project-default-rtdb.firebaseio.com/test.json

✏️  Testing write access...
Testing write access: https://vulnerable-project-default-rtdb.firebaseio.com/security_test_1690123456.json

============================================================
🔍 FIREBASE SECURITY ANALYSIS REPORT
============================================================

📍 Database URL: https://vulnerable-project-default-rtdb.firebaseio.com

📖 READ ACCESS:
❌ PUBLICLY READABLE - No authentication required!
⚠️  Database contains data that is publicly accessible

✏️  WRITE ACCESS:
❌ PUBLICLY WRITABLE - Anyone can modify data!
🚨 CRITICAL SECURITY RISK!

🛡️  OVERALL SECURITY STATUS:
🚨 INSECURE - Immediate action required!

💡 RECOMMENDATIONS:
   1. Review Firebase Security Rules
   2. Implement proper authentication
   3. Restrict database access to authenticated users only
   4. Monitor database access logs
```

## 🔧 Exit Codes

The tool returns different exit codes for automation and scripting:

| Exit Code | Meaning |
|-----------|---------|
| `0` | Database appears secure |
| `1` | Security vulnerabilities found |
| `2` | Invalid URL or configuration error |
| `130` | User cancelled (Ctrl+C) |

### Example in Scripts

```bash
#!/bin/bash
python firebase_checker.py https://my-project-default-rtdb.firebaseio.com/

if [ $? -eq 1 ]; then
    echo "⚠️  Security issues detected! Check the report above."
    # Send alert, log incident, etc.
fi
```

## 🔍 What Gets Tested

### Read Access Tests
- **Root Access** (`/.json`): Can the entire database be read?
- **Shallow Reads** (`/.json?shallow=true`): Can database structure be enumerated?
- **Arbitrary Paths** (`/test.json`): Can specific paths be accessed?

### Write Access Tests
- **Data Creation**: Can new data be written without authentication?
- **Data Modification**: Can existing data be overwritten?

### Security Analysis
- Identifies public read access vulnerabilities
- Detects public write access risks
- Analyzes data exposure levels
- Provides specific security recommendations

## 🛡️ Security Best Practices

If the tool finds vulnerabilities, here's how to secure your Firebase database:

### 1. Configure Firebase Security Rules

Replace default rules with restrictive ones:

```javascript
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null"
  }
}
```

### 2. Implement Authentication

Ensure your app uses Firebase Authentication:
- Set up authentication providers
- Require user login before database access
- Use security rules to verify authenticated users

### 3. Use Granular Rules

Create specific rules for different data structures:

```javascript
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    },
    "public_data": {
      ".read": true,
      ".write": false
    }
  }
}
```

### 4. Regular Security Audits

- Run this tool regularly against your databases
- Monitor Firebase console for security warnings
- Review access logs for suspicious activity
- Keep Firebase SDK and rules updated

## 🔧 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Firebase Security Check

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM
  workflow_dispatch:

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: pip install requests
        
      - name: Run Firebase security check
        run: |
          python firebase_checker.py ${{ secrets.FIREBASE_DB_URL }}
          
      - name: Notify on failure
        if: failure()
        run: echo "Security vulnerabilities detected!"
```

## 🚫 Limitations

- **Realtime Database Only**: This tool is designed for Firebase Realtime Database, not Firestore
- **Basic Testing**: Only tests common public access patterns
- **No Authentication Testing**: Doesn't test authenticated access patterns
- **Rate Limiting**: May be subject to Firebase rate limits on repeated requests

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Support for Firestore security testing
- Additional security rule patterns
- Integration with security scanning platforms
- Performance optimizations
- Additional output formats (JSON, XML, etc.)

## 📄 License

This tool is provided as-is for educational and legitimate security testing purposes. Users are responsible for ensuring they have proper authorization before testing any Firebase database.

## 🆘 Support

If you encounter issues:

1. **Check Firebase URL format**: Ensure it's a valid Firebase Realtime Database URL
2. **Verify network connectivity**: Test basic internet access
3. **Review Firebase console**: Check for any service outages or restrictions
4. **Check rate limits**: Firebase may limit requests from the same IP

For bugs or feature requests, please create an issue with:
- Python version
- Complete error messages
- Firebase URL format (without sensitive details)
- Steps to reproduce the issue

## 🔗 Related Resources

- [Firebase Security Rules Documentation](https://firebase.google.com/docs/database/security)
- [Firebase Authentication Guide](https://firebase.google.com/docs/auth)
- [Firebase Security Best Practices](https://firebase.google.com/docs/database/security/securing-data)
- [OWASP Firebase Security Guide](https://owasp.org/www-project-web-security-testing-guide/)

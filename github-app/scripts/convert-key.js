/**
 * Helper script to convert GitHub App private key to .env format
 * 
 * Usage: node convert-key.js path/to/private-key.pem
 */

const fs = require('fs');
const path = require('path');

const keyPath = process.argv[2];

if (!keyPath) {
  console.error('Usage: node convert-key.js path/to/private-key.pem');
  process.exit(1);
}

if (!fs.existsSync(keyPath)) {
  console.error(`Error: File not found: ${keyPath}`);
  process.exit(1);
}

try {
  const key = fs.readFileSync(keyPath, 'utf8');
  const convertedKey = key.replace(/\n/g, '\\n');
  
  console.log('\n✅ Converted private key for .env file:\n');
  console.log('GITHUB_APP_PRIVATE_KEY=' + convertedKey);
  console.log('\n📋 Copy the line above to your .env file\n');
} catch (error) {
  console.error('Error reading key file:', error.message);
  process.exit(1);
}

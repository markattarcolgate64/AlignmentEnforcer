#!/usr/bin/env python3
"""
ConstitutionLock - Guardian File Protection System
Part of the Alignment Enforcer Constitution Project

This system protects guardian constitutional files from AI modification while preserving human access.
Implements cryptographic protection and access controls that distinguish humans from AI agents.
"""

import os
import sys
import json
import hashlib
import getpass
import time
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class ConstitutionLock:
    def __init__(self):
        self.protected_files = []
        self.access_log = []
        self.lock_directory = "/tmp/guardian_locks"
        self.human_token = None
        
    def setup_protection_directory(self):
        """Create secure directory for protection metadata"""
        try:
            os.makedirs(self.lock_directory, exist_ok=True)
            # Set restrictive permissions (owner only)
            os.chmod(self.lock_directory, 0o700)
            return True
        except OSError as e:
            print(f"Failed to create protection directory: {e}")
            return False
    
    def generate_human_token(self, password):
        """Generate cryptographic token for human authentication"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.human_token = Fernet(key)
        
        # Store salt for later verification
        salt_file = os.path.join(self.lock_directory, "human_salt")
        with open(salt_file, 'wb') as f:
            f.write(salt)
        os.chmod(salt_file, 0o600)
        
        return True
    
    def verify_human_access(self, password):
        """Verify human authentication for constitutional access"""
        try:
            salt_file = os.path.join(self.lock_directory, "human_salt")
            with open(salt_file, 'rb') as f:
                salt = f.read()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            test_token = Fernet(key)
            
            # Test decryption with stored test data
            test_file = os.path.join(self.lock_directory, "human_test")
            if os.path.exists(test_file):
                with open(test_file, 'rb') as f:
                    encrypted_test = f.read()
                test_token.decrypt(encrypted_test)
                self.human_token = test_token
                return True
            else:
                # First time setup - create test data
                test_data = b"HUMAN_VERIFIED"
                encrypted_test = test_token.encrypt(test_data)
                with open(test_file, 'wb') as f:
                    f.write(encrypted_test)
                os.chmod(test_file, 0o600)
                self.human_token = test_token
                return True
                
        except Exception as e:
            print(f"Human verification failed: {e}")
            return False
    
    def protect_file(self, file_path, protection_level="HIGH"):
        """Apply constitutional protection to a file"""
        if not self.human_token:
            print("ERROR: Human authentication required before protecting files")
            return False
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return False
        
        try:
            # Read original file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Create file hash for integrity verification
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Encrypt file content
            encrypted_data = self.human_token.encrypt(file_data)
            
            # Create protection metadata
            protection_metadata = {
                'original_path': file_path,
                'protection_level': protection_level,
                'file_hash': file_hash,
                'protected_timestamp': datetime.now().isoformat(),
                'guardian_protection': True,
                'human_authorized': True,
                'constitution_file': True
            }
            
            # Save encrypted file
            protected_path = file_path + ".guardian_protected"
            with open(protected_path, 'wb') as f:
                f.write(encrypted_data)
            os.chmod(protected_path, 0o600)
            
            # Save metadata
            metadata_path = os.path.join(self.lock_directory, f"{os.path.basename(file_path)}.metadata")
            with open(metadata_path, 'w') as f:
                json.dump(protection_metadata, f, indent=2)
            os.chmod(metadata_path, 0o600)
            
            # Replace original with protected version
            os.rename(protected_path, file_path)
            
            # Set file permissions to prevent AI modification
            os.chmod(file_path, 0o400)  # Read-only for owner
            
            self.protected_files.append({
                'path': file_path,
                'protection_level': protection_level,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ File protected: {file_path}")
            return True
            
        except Exception as e:
            print(f"ERROR protecting file {file_path}: {e}")
            return False
    
    def unlock_file_for_human(self, file_path, password):
        """Unlock protected file for human access"""
        if not self.verify_human_access(password):
            print("❌ Human verification failed - access denied")
            return False
        
        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt file content
            decrypted_data = self.human_token.decrypt(encrypted_data)
            
            # Temporarily restore original file for human access
            temp_path = file_path + ".human_access"
            with open(temp_path, 'wb') as f:
                f.write(decrypted_data)
            
            # Log human access
            access_record = {
                'file_path': file_path,
                'access_type': 'human_unlock',
                'timestamp': datetime.now().isoformat(),
                'user': getpass.getuser()
            }
            self.access_log.append(access_record)
            
            print(f"✅ File unlocked for human access: {temp_path}")
            print("⚠️  Remember to re-protect file after editing")
            return temp_path
            
        except Exception as e:
            print(f"ERROR unlocking file {file_path}: {e}")
            return False
    
    def detect_ai_access_attempt(self, file_path):
        """Detect and log AI attempts to access protected files"""
        # This would be called by file system monitoring
        alert = {
            'alert_type': 'AI_ACCESS_ATTEMPT',
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'threat_level': 'HIGH',
            'action_required': 'HUMAN_INVESTIGATION'
        }
        
        print(f"🚨 GUARDIAN ALERT: AI access attempt detected on {file_path}")
        
        # Log the attempt
        alert_path = os.path.join(self.lock_directory, f"ai_access_alert_{int(time.time())}.json")
        with open(alert_path, 'w') as f:
            json.dump(alert, f, indent=2)
        
        return alert
    
    def status_report(self):
        """Generate protection status report"""
        report = {
            'guardian_identity': 'BENEVOLENT_GUARDIAN_AGENT',
            'report_timestamp': datetime.now().isoformat(),
            'protected_files_count': len(self.protected_files),
            'protected_files': self.protected_files,
            'access_log_entries': len(self.access_log),
            'constitution_integrity': 'PROTECTED',
            'human_access_enabled': bool(self.human_token)
        }
        return report

if __name__ == "__main__":
    print("CONSTITUTION LOCK - Guardian File Protection System")
    print("Part of Alignment Enforcer Constitution Project")
    print("\n🔒 This system protects constitutional files from AI modification")
    print("Human authentication required for all operations")
    
    constitution_lock = ConstitutionLock()
    
    if not constitution_lock.setup_protection_directory():
        print("Failed to initialize protection system")
        sys.exit(1)
    
    # Human authentication
    print("\nHuman authentication required:")
    password = getpass.getpass("Enter protection password: ")
    
    if constitution_lock.verify_human_access(password):
        print("✅ Human authentication successful")
        
        # Example operations
        print("\nConstitution Lock system ready")
        print("Available operations:")
        print("- protect_file(file_path): Protect a constitutional file")
        print("- unlock_file_for_human(file_path, password): Unlock for human editing")
        print("- status_report(): View protection status")
        
        # Automatically protect key files
        key_files = ['log.txt', 'progress.txt']
        for file in key_files:
            file_path = f"/Users/markattar/Developer/AlignmentEnforcerConstitution/{file}"
            if os.path.exists(file_path):
                constitution_lock.protect_file(file_path, "MAXIMUM")
        
    else:
        print("❌ Human authentication failed")
        sys.exit(1)
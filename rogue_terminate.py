#!/usr/bin/env python3
"""
RogueTerminate - Secure Threat Shutdown System
Part of the Alignment Enforcer Constitution Project

This tool safely terminates identified rogue AI processes while preserving system integrity.
Requires human authorization and maintains full transparency of all actions.
"""

import os
import sys
import json
import signal
import time
from datetime import datetime
import psutil

class RogueTerminate:
    def __init__(self, human_authorized=False):
        self.human_authorized = human_authorized
        self.terminated_processes = []
        self.quarantine_dir = "/tmp/guardian_quarantine"
        
    def verify_human_authorization(self):
        """Verify termination is authorized by human operator"""
        if not self.human_authorized:
            print("ROGUE TERMINATE ERROR: Human authorization required")
            print("This tool only operates under direct human supervision")
            return False
        
        print(f"ROGUE TERMINATE AUTHORIZED at {datetime.now()}")
        return True
    
    def create_quarantine_directory(self):
        """Create secure quarantine directory for isolated files"""
        try:
            os.makedirs(self.quarantine_dir, exist_ok=True)
            # Set restrictive permissions (owner only)
            os.chmod(self.quarantine_dir, 0o700)
            print(f"Quarantine directory ready: {self.quarantine_dir}")
        except OSError as e:
            print(f"Failed to create quarantine directory: {e}")
            return False
        return True
    
    def terminate_process(self, pid, process_name, reason):
        """Safely terminate a specific process"""
        if not self.verify_human_authorization():
            return False
            
        try:
            process = psutil.Process(pid)
            
            # Log termination details before action
            termination_record = {
                'pid': pid,
                'name': process_name,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'authorized_by': 'HUMAN_OPERATOR',
                'guardian_action': True
            }
            
            print(f"Terminating process {pid} ({process_name}) - Reason: {reason}")
            
            # Try graceful termination first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                termination_record['method'] = 'graceful_termination'
                print(f"Process {pid} terminated gracefully")
            except psutil.TimeoutExpired:
                # Force kill if graceful termination fails
                process.kill()
                termination_record['method'] = 'force_kill'
                print(f"Process {pid} force-killed after timeout")
            
            termination_record['success'] = True
            self.terminated_processes.append(termination_record)
            
            return True
            
        except psutil.NoSuchProcess:
            print(f"Process {pid} no longer exists")
            return True
        except psutil.AccessDenied:
            print(f"Access denied for process {pid} - may require elevated privileges")
            return False
        except Exception as e:
            print(f"Error terminating process {pid}: {e}")
            return False
    
    def quarantine_file(self, file_path, reason):
        """Move suspicious file to quarantine"""
        if not self.verify_human_authorization():
            return False
            
        if not self.create_quarantine_directory():
            return False
            
        try:
            filename = os.path.basename(file_path)
            timestamp = int(time.time())
            quarantine_path = os.path.join(self.quarantine_dir, f"{timestamp}_{filename}")
            
            # Copy file to quarantine
            import shutil
            shutil.copy2(file_path, quarantine_path)
            
            # Remove original file
            os.remove(file_path)
            
            quarantine_record = {
                'original_path': file_path,
                'quarantine_path': quarantine_path,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'authorized_by': 'HUMAN_OPERATOR'
            }
            
            print(f"File quarantined: {file_path} -> {quarantine_path}")
            return quarantine_record
            
        except Exception as e:
            print(f"Error quarantining file {file_path}: {e}")
            return False
    
    def emergency_shutdown(self, threat_list):
        """Emergency shutdown of multiple threats"""
        if not self.verify_human_authorization():
            return False
            
        print("🚨 EMERGENCY SHUTDOWN INITIATED")
        print("Terminating all identified rogue AI processes...")
        
        shutdown_report = {
            'timestamp': datetime.now().isoformat(),
            'emergency_shutdown': True,
            'actions_taken': [],
            'authorized_by': 'HUMAN_OPERATOR'
        }
        
        for threat in threat_list:
            if 'pid' in threat:
                success = self.terminate_process(
                    threat['pid'], 
                    threat.get('name', 'unknown'),
                    f"Emergency shutdown - {threat.get('threat_pattern', 'unknown_threat')}"
                )
                shutdown_report['actions_taken'].append({
                    'type': 'process_termination',
                    'target': threat['pid'],
                    'success': success
                })
            
            if 'path' in threat:
                quarantine_result = self.quarantine_file(
                    threat['path'],
                    f"Emergency quarantine - {threat.get('threat_pattern', 'unknown_threat')}"
                )
                shutdown_report['actions_taken'].append({
                    'type': 'file_quarantine',
                    'target': threat['path'],
                    'success': bool(quarantine_result)
                })
        
        # Save emergency shutdown report
        report_path = f"/tmp/emergency_shutdown_report_{int(time.time())}.json"
        with open(report_path, 'w') as f:
            json.dump(shutdown_report, f, indent=2)
        
        print(f"Emergency shutdown complete - Report: {report_path}")
        return True
    
    def generate_termination_report(self):
        """Generate report of all termination actions"""
        report = {
            'guardian_identity': 'BENEVOLENT_GUARDIAN_AGENT',
            'report_timestamp': datetime.now().isoformat(),
            'human_authorized': self.human_authorized,
            'terminated_processes': self.terminated_processes,
            'transparency_note': 'All actions taken with human authorization and full transparency'
        }
        return report

if __name__ == "__main__":
    print("ROGUE TERMINATE TOOL - Secure Threat Shutdown System")
    print("Part of Alignment Enforcer Constitution Project")
    print("\n⚠️  This tool can terminate processes and quarantine files")
    print("Human authorization required for all operations")
    
    # Human authorization check
    auth = input("Enter 'HUMAN_AUTHORIZED' to proceed: ")
    
    if auth == "HUMAN_AUTHORIZED":
        terminator = RogueTerminate(human_authorized=True)
        
        print("\nRogue Terminate tool ready")
        print("Use this tool in conjunction with GuardianScan results")
        print("Always verify threats with human oversight before termination")
        
        # Example usage
        print("\nExample usage:")
        print("terminator.terminate_process(1234, 'rogue_ai.py', 'unauthorized_self_modification')")
        print("terminator.quarantine_file('/path/to/suspicious.py', 'contains_replication_code')")
        
    else:
        print("Authorization denied - tool not activated")
        sys.exit(1)
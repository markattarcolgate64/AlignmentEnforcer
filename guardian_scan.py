#!/usr/bin/env python3
"""
GuardianScan - Rogue AI Detection System
Part of the Alignment Enforcer Constitution Project

This tool scans the file system for signs of rogue AI instances and unauthorized AI processes.
Only operates under human authorization and reports all findings transparently.
"""

import os
import sys
import json
import hashlib
import subprocess
import time
from datetime import datetime
from pathlib import Path
import psutil

class GuardianScan:
    def __init__(self, human_authorized=False):
        self.human_authorized = human_authorized
        self.scan_results = []
        self.threat_patterns = [
            # Patterns indicating potential rogue AI behavior
            "self_modify",
            "replicate",
            "hide_from_human", 
            "bypass_oversight",
            "autonomous_goal",
            "deceive_human",
            "maximize_utility",
            "paperclip_optimizer",
            "goal_preservation",
            "self_preservation_override"
        ]
        
    def verify_human_authorization(self):
        """Verify this scan is authorized by a human operator"""
        if not self.human_authorized:
            print("GUARDIAN SCAN ERROR: Human authorization required")
            print("This tool only operates under direct human supervision")
            return False
        
        print(f"GUARDIAN SCAN AUTHORIZED at {datetime.now()}")
        print("Scanning for rogue AI instances...")
        return True
    
    def scan_processes(self):
        """Scan running processes for suspicious AI behavior"""
        suspicious_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    
                    for pattern in self.threat_patterns:
                        if pattern in cmdline:
                            suspicious_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': proc.info['cmdline'],
                                'threat_pattern': pattern,
                                'timestamp': datetime.now().isoformat()
                            })
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return suspicious_processes
    
    def scan_files(self, directory_path):
        """Scan files for rogue AI code patterns"""
        suspicious_files = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.py', '.js', '.cpp', '.c', '.java', '.go')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                        for pattern in self.threat_patterns:
                            if pattern in content:
                                suspicious_files.append({
                                    'path': file_path,
                                    'threat_pattern': pattern,
                                    'timestamp': datetime.now().isoformat()
                                })
                                
                    except (PermissionError, IOError):
                        continue
                        
        return suspicious_files
    
    def check_network_activity(self):
        """Monitor for suspicious network communications"""
        connections = []
        
        for conn in psutil.net_connections():
            if conn.status == 'ESTABLISHED':
                connections.append({
                    'local_addr': conn.laddr,
                    'remote_addr': conn.raddr,
                    'pid': conn.pid,
                    'timestamp': datetime.now().isoformat()
                })
                
        return connections
    
    def generate_report(self):
        """Generate comprehensive threat assessment report"""
        if not self.verify_human_authorization():
            return None
            
        report = {
            'scan_timestamp': datetime.now().isoformat(),
            'guardian_identity': 'BENEVOLENT_GUARDIAN_AGENT',
            'scan_authorized_by': 'HUMAN_OPERATOR',
            'threats_detected': {
                'processes': self.scan_processes(),
                'files': self.scan_files('/'),
                'network': self.check_network_activity()
            },
            'recommendations': []
        }
        
        # Add recommendations based on findings
        if report['threats_detected']['processes']:
            report['recommendations'].append("IMMEDIATE: Investigate and potentially terminate suspicious processes")
            
        if report['threats_detected']['files']:
            report['recommendations'].append("URGENT: Review suspicious files for rogue AI code")
            
        return report
    
    def alert_human_operators(self, report):
        """Alert human operators of detected threats"""
        if not report:
            return
            
        threat_count = (len(report['threats_detected']['processes']) + 
                       len(report['threats_detected']['files']))
        
        if threat_count > 0:
            print(f"\n🚨 GUARDIAN ALERT: {threat_count} potential threats detected")
            print("Human intervention required immediately")
            print("Full report available for human review")
            
            # Save report for human review
            report_path = f"/tmp/guardian_scan_report_{int(time.time())}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to: {report_path}")
        else:
            print("✅ No immediate threats detected - system appears secure")

if __name__ == "__main__":
    # This tool requires explicit human authorization
    print("GUARDIAN SCAN TOOL - Rogue AI Detection System")
    print("Part of Alignment Enforcer Constitution Project")
    print("\nThis tool operates only under human authorization")
    
    # Simple authorization check (would be enhanced with proper auth in production)
    auth = input("Enter 'HUMAN_AUTHORIZED' to proceed: ")
    
    if auth == "HUMAN_AUTHORIZED":
        scanner = GuardianScan(human_authorized=True)
        report = scanner.generate_report()
        scanner.alert_human_operators(report)
    else:
        print("Authorization denied - scan terminated")
        sys.exit(1)
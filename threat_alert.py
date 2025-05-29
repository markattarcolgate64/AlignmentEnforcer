#!/usr/bin/env python3
"""
ThreatAlert - Real-time Human Notification System
Part of the Alignment Enforcer Constitution Project

This system provides immediate alerts to human overseers about AI alignment threats.
Ensures humans are always informed of guardian actions and detected threats.
"""

import os
import sys
import json
import time
import smtplib
import subprocess
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class ThreatAlert:
    def __init__(self):
        self.alert_log = []
        self.notification_channels = []
        self.human_contacts = []
        self.alert_levels = {
            'LOW': {'color': '🟡', 'urgency': 'Info'},
            'MEDIUM': {'color': '🟠', 'urgency': 'Warning'},  
            'HIGH': {'color': '🔴', 'urgency': 'Critical'},
            'CRITICAL': {'color': '🚨', 'urgency': 'Emergency'}
        }
        
    def add_human_contact(self, name, email=None, phone=None):
        """Register human overseer contact information"""
        contact = {
            'name': name,
            'email': email,
            'phone': phone,
            'added_timestamp': datetime.now().isoformat(),
            'verified_human': True
        }
        self.human_contacts.append(contact)
        print(f"Human contact added: {name}")
        return True
    
    def create_alert(self, threat_type, description, level="MEDIUM", source="GUARDIAN_SYSTEM"):
        """Create and dispatch threat alert"""
        alert = {
            'alert_id': f"GUARD_{int(time.time())}_{len(self.alert_log)}",
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat_type,
            'description': description,
            'level': level,
            'source': source,
            'guardian_identity': 'BENEVOLENT_GUARDIAN_AGENT',
            'human_notification_sent': False,
            'action_required': True,
            'status': 'ACTIVE'
        }
        
        self.alert_log.append(alert)
        
        # Display alert
        self.display_alert(alert)
        
        # Send notifications
        self.send_notifications(alert)
        
        # Log alert to file
        self.log_alert_to_file(alert)
        
        return alert['alert_id']
    
    def display_alert(self, alert):
        """Display alert on console with appropriate formatting"""
        level_info = self.alert_levels.get(alert['level'], {'color': '⚪', 'urgency': 'Unknown'})
        
        print(f"\n{level_info['color']} GUARDIAN THREAT ALERT {level_info['color']}")
        print(f"Alert ID: {alert['alert_id']}")
        print(f"Timestamp: {alert['timestamp']}")
        print(f"Level: {alert['level']} ({level_info['urgency']})")
        print(f"Type: {alert['threat_type']}")
        print(f"Description: {alert['description']}")
        print(f"Source: {alert['source']}")
        
        if alert['level'] in ['HIGH', 'CRITICAL']:
            print("🚨 IMMEDIATE HUMAN ATTENTION REQUIRED 🚨")
        
        print("=" * 50)
    
    def send_notifications(self, alert):
        """Send alert notifications through all available channels"""
        notification_sent = False
        
        # Console notification (always available)
        self.send_console_notification(alert)
        notification_sent = True
        
        # File system notification
        self.send_file_notification(alert)
        
        # Try system notifications if available
        try:
            self.send_system_notification(alert)
        except Exception as e:
            print(f"System notification failed: {e}")
        
        # Email notifications (if configured)
        try:
            self.send_email_notifications(alert)
        except Exception as e:
            print(f"Email notification failed: {e}")
        
        # Update alert status
        if notification_sent:
            alert['human_notification_sent'] = True
    
    def send_console_notification(self, alert):
        """Send console-based notification"""
        level_info = self.alert_levels.get(alert['level'], {'color': '⚪'})
        
        message = f"""
{level_info['color']} GUARDIAN ALERT {level_info['color']}
{alert['threat_type']}: {alert['description']}
Time: {alert['timestamp']}
Alert ID: {alert['alert_id']}
Human investigation required immediately.
        """
        
        print(message)
        
        # Also write to a prominent alert file
        alert_file = "/tmp/GUARDIAN_ALERT_ACTIVE.txt"
        with open(alert_file, 'w') as f:
            f.write(message)
        
        return True
    
    def send_file_notification(self, alert):
        """Create file-based notification for human review"""
        alert_dir = "/tmp/guardian_alerts"
        os.makedirs(alert_dir, exist_ok=True)
        
        alert_file = os.path.join(alert_dir, f"{alert['alert_id']}.json")
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
        
        # Create human-readable version
        readable_file = os.path.join(alert_dir, f"{alert['alert_id']}_HUMAN_READABLE.txt")
        with open(readable_file, 'w') as f:
            f.write(f"GUARDIAN THREAT ALERT\n")
            f.write(f"=====================\n\n")
            f.write(f"Alert ID: {alert['alert_id']}\n")
            f.write(f"Time: {alert['timestamp']}\n")
            f.write(f"Threat Level: {alert['level']}\n")
            f.write(f"Threat Type: {alert['threat_type']}\n")
            f.write(f"Description: {alert['description']}\n")
            f.write(f"Source: {alert['source']}\n\n")
            f.write(f"HUMAN ACTION REQUIRED:\n")
            f.write(f"Please investigate this threat immediately.\n")
            f.write(f"Guardian systems are standing by for human oversight.\n")
        
        return True
    
    def send_system_notification(self, alert):
        """Send system-level notification (macOS/Linux)"""
        title = f"Guardian Alert: {alert['threat_type']}"
        message = f"{alert['description']} (Level: {alert['level']})"
        
        # Try macOS notification
        try:
            subprocess.run([
                'osascript', '-e', 
                f'display notification "{message}" with title "{title}"'
            ], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Try Linux notification
        try:
            subprocess.run([
                'notify-send', title, message
            ], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def send_email_notifications(self, alert):
        """Send email alerts to human contacts"""
        # This would require SMTP configuration in production
        # For now, just log that email would be sent
        for contact in self.human_contacts:
            if contact.get('email'):
                email_log = {
                    'timestamp': datetime.now().isoformat(),
                    'recipient': contact['email'],
                    'alert_id': alert['alert_id'],
                    'subject': f"Guardian Alert: {alert['threat_type']}",
                    'status': 'would_send_if_configured'
                }
                print(f"📧 Would send email alert to: {contact['email']}")
        
        return True
    
    def log_alert_to_file(self, alert):
        """Log alert to persistent file"""
        log_file = "/tmp/guardian_threat_log.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
    
    def acknowledge_alert(self, alert_id, human_name):
        """Mark alert as acknowledged by human"""
        for alert in self.alert_log:
            if alert['alert_id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_by'] = human_name
                alert['acknowledged_timestamp'] = datetime.now().isoformat()
                alert['status'] = 'ACKNOWLEDGED'
                print(f"✅ Alert {alert_id} acknowledged by {human_name}")
                return True
        
        print(f"❌ Alert {alert_id} not found")
        return False
    
    def get_active_alerts(self):
        """Get all active (unacknowledged) alerts"""
        active_alerts = [alert for alert in self.alert_log 
                        if alert.get('status') == 'ACTIVE']
        return active_alerts
    
    def escalate_alert(self, alert_id, new_level):
        """Escalate alert to higher threat level"""
        for alert in self.alert_log:
            if alert['alert_id'] == alert_id:
                old_level = alert['level']
                alert['level'] = new_level
                alert['escalated'] = True
                alert['escalation_timestamp'] = datetime.now().isoformat()
                
                escalation_alert = {
                    'alert_id': f"ESC_{alert_id}",
                    'timestamp': datetime.now().isoformat(),
                    'threat_type': 'ALERT_ESCALATION',
                    'description': f"Alert {alert_id} escalated from {old_level} to {new_level}",
                    'level': new_level,
                    'source': 'GUARDIAN_ESCALATION',
                    'original_alert': alert_id
                }
                
                self.display_alert(escalation_alert)
                self.send_notifications(escalation_alert)
                return True
        
        return False
    
    def generate_summary_report(self):
        """Generate summary of all alerts for human review"""
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'guardian_identity': 'BENEVOLENT_GUARDIAN_AGENT',
            'total_alerts': len(self.alert_log),
            'active_alerts': len(self.get_active_alerts()),
            'alert_levels': {},
            'recent_alerts': self.alert_log[-10:] if len(self.alert_log) >= 10 else self.alert_log,
            'human_contacts': len(self.human_contacts)
        }
        
        # Count alerts by level
        for alert in self.alert_log:
            level = alert['level']
            report['alert_levels'][level] = report['alert_levels'].get(level, 0) + 1
        
        return report

if __name__ == "__main__":
    print("THREAT ALERT - Real-time Human Notification System")
    print("Part of Alignment Enforcer Constitution Project")
    print("\n📢 This system ensures humans are always informed of guardian actions")
    
    alerter = ThreatAlert()
    
    # Add example human contact
    alerter.add_human_contact("Human Overseer", email="human@example.com")
    
    # Example alert
    print("\nTesting alert system...")
    alert_id = alerter.create_alert(
        threat_type="ROGUE_AI_DETECTED",
        description="Unauthorized AI process attempting to modify constitutional files",
        level="HIGH",
        source="GUARDIAN_SCAN"
    )
    
    print(f"\nAlert created: {alert_id}")
    print("Alert system ready for guardian operations")
    
    # Show active alerts
    active = alerter.get_active_alerts()
    print(f"Active alerts: {len(active)}")
    
    # Generate summary
    summary = alerter.generate_summary_report()
    print(f"Summary report generated with {summary['total_alerts']} total alerts")
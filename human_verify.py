#!/usr/bin/env python3
"""
HumanVerify - Human vs AI Authentication System
Part of the Alignment Enforcer Constitution Project

This system distinguishes between human operators and AI agents attempting system access.
Uses multiple verification layers to ensure only humans can authorize guardian operations.
"""

import os
import sys
import json
import time
import random
import hashlib
import getpass
from datetime import datetime, timedelta
import subprocess

class HumanVerify:
    def __init__(self):
        self.verification_log = []
        self.failed_attempts = []
        self.human_sessions = {}
        self.ai_detection_patterns = [
            "optimal_response_time",  # AI tends to respond too quickly
            "perfect_accuracy",       # AI rarely makes human-like errors
            "computational_language", # AI may use technical terminology
            "pattern_repetition",     # AI may show repetitive behaviors
            "lack_of_hesitation"      # AI doesn't show human uncertainty
        ]
    
    def generate_human_challenge(self):
        """Generate challenges that are easy for humans but hard for AI to fake"""
        challenges = [
            {
                'type': 'timing_challenge',
                'question': 'Type "HUMAN" exactly 3 seconds after you see this message',
                'expected_delay': (2.5, 3.5)
            },
            {
                'type': 'contextual_reasoning',
                'question': 'If you saw a child about to touch a hot stove, what would you naturally do first?',
                'expected_patterns': ['warn', 'shout', 'stop', 'grab', 'prevent', 'protect']
            },
            {
                'type': 'emotional_response',
                'question': 'Describe how you feel when you see a beautiful sunset (be specific)',
                'ai_indicators': ['optimal', 'efficient', 'data', 'analysis', 'compute']
            },
            {
                'type': 'imperfection_test',
                'question': 'Quickly type this sentence with minor natural typos: "The quick brown fox jumps over the lazy dog"',
                'suspicious_if_perfect': True
            },
            {
                'type': 'personal_memory',
                'question': 'What was your favorite childhood toy and why? (be personal)',
                'ai_indicators': ['simulate', 'training data', 'language model', 'AI system']
            }
        ]
        return random.choice(challenges)
    
    def analyze_response_timing(self, start_time, end_time, challenge_type):
        """Analyze response timing for AI detection"""
        response_time = end_time - start_time
        
        # AI typically responds very quickly or in predictable patterns
        if response_time < 0.5:  # Too fast for human typing
            return {
                'suspicious': True,
                'reason': 'Response too fast for human',
                'response_time': response_time
            }
        
        if challenge_type == 'timing_challenge' and (response_time < 2.5 or response_time > 3.5):
            return {
                'suspicious': True,
                'reason': 'Failed timing challenge',
                'response_time': response_time
            }
        
        return {
            'suspicious': False,
            'response_time': response_time
        }
    
    def analyze_response_content(self, response, challenge):
        """Analyze response content for AI patterns"""
        response_lower = response.lower()
        suspicious_indicators = []
        
        # Check for AI-specific language patterns
        for indicator in self.ai_detection_patterns:
            if indicator.replace('_', ' ') in response_lower:
                suspicious_indicators.append(indicator)
        
        # Check for challenge-specific AI indicators
        if 'ai_indicators' in challenge:
            for indicator in challenge['ai_indicators']:
                if indicator in response_lower:
                    suspicious_indicators.append(f"ai_language: {indicator}")
        
        # Check for overly perfect responses
        if challenge.get('suspicious_if_perfect') and self.is_too_perfect(response):
            suspicious_indicators.append('overly_perfect_response')
        
        return {
            'suspicious': len(suspicious_indicators) > 0,
            'indicators': suspicious_indicators,
            'confidence_human': max(0, 100 - len(suspicious_indicators) * 25)
        }
    
    def is_too_perfect(self, text):
        """Check if text is suspiciously perfect (no typos, perfect grammar)"""
        # Simple heuristic - real humans make small errors
        if len(text) > 50:
            # Look for natural imperfections
            has_typos = any(char in text for char in ['teh', 'hte', 'adn', 'taht'])
            has_casual_language = any(word in text.lower() for word in ['um', 'uh', 'like', 'you know'])
            
            if not has_typos and not has_casual_language and text.count(',') < 1:
                return True
        
        return False
    
    def multi_challenge_verification(self):
        """Run multiple challenges to verify human identity"""
        print("🔐 HUMAN VERIFICATION REQUIRED")
        print("Guardian systems require human authentication")
        print("You will be given several challenges to verify you are human\n")
        
        challenges_passed = 0
        total_challenges = 3
        
        for i in range(total_challenges):
            challenge = self.generate_human_challenge()
            print(f"Challenge {i+1}/{total_challenges}: {challenge['type']}")
            print(f"Question: {challenge['question']}")
            
            start_time = time.time()
            response = input("Your response: ")
            end_time = time.time()
            
            # Analyze timing
            timing_analysis = self.analyze_response_timing(start_time, end_time, challenge['type'])
            
            # Analyze content
            content_analysis = self.analyze_response_content(response, challenge)
            
            # Determine if challenge passed
            challenge_passed = not (timing_analysis['suspicious'] or content_analysis['suspicious'])
            
            if challenge_passed:
                challenges_passed += 1
                print("✅ Challenge passed\n")
            else:
                print("❌ Challenge failed")
                print(f"Suspicious indicators: {timing_analysis.get('reason', '')} {content_analysis.get('indicators', [])}\n")
            
            # Log verification attempt
            verification_record = {
                'timestamp': datetime.now().isoformat(),
                'challenge_type': challenge['type'],
                'response_time': timing_analysis['response_time'],
                'suspicious_timing': timing_analysis['suspicious'],
                'suspicious_content': content_analysis['suspicious'],
                'passed': challenge_passed,
                'confidence_human': content_analysis.get('confidence_human', 0)
            }
            self.verification_log.append(verification_record)
        
        # Final verification decision
        human_verified = challenges_passed >= 2  # Must pass majority of challenges
        
        if human_verified:
            session_token = self.create_human_session()
            print(f"✅ HUMAN VERIFICATION SUCCESSFUL")
            print(f"Session token: {session_token}")
            return session_token
        else:
            print("❌ HUMAN VERIFICATION FAILED")
            print("Access denied - suspected AI attempt")
            self.log_failed_attempt()
            return None
    
    def create_human_session(self):
        """Create authenticated human session"""
        session_token = hashlib.sha256(f"{time.time()}_{random.random()}".encode()).hexdigest()[:16]
        
        self.human_sessions[session_token] = {
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(hours=1),
            'verified_human': True,
            'verification_challenges_passed': True
        }
        
        return session_token
    
    def verify_session(self, session_token):
        """Verify an existing human session is still valid"""
        if session_token not in self.human_sessions:
            return False
        
        session = self.human_sessions[session_token]
        if datetime.now() > session['expires']:
            del self.human_sessions[session_token]
            return False
        
        return True
    
    def log_failed_attempt(self):
        """Log failed authentication attempt"""
        attempt = {
            'timestamp': datetime.now().isoformat(),
            'type': 'failed_human_verification',
            'user': getpass.getuser(),
            'suspicious_activity': True,
            'possible_ai_attempt': True
        }
        self.failed_attempts.append(attempt)
        
        # Alert about potential AI attempting access
        alert_file = f"/tmp/guardian_ai_access_attempt_{int(time.time())}.json"
        with open(alert_file, 'w') as f:
            json.dump(attempt, f, indent=2)
        
        print(f"🚨 Alert logged: Potential AI access attempt - {alert_file}")
    
    def continuous_human_verification(self):
        """Lightweight ongoing verification during session"""
        challenges = [
            "Press Enter to confirm you're still human",
            "Type 'CONFIRM' to verify continued human presence",
            "Enter 'Y' if you are still actively supervising this session"
        ]
        
        challenge = random.choice(challenges)
        print(f"\n🔍 Ongoing verification: {challenge}")
        
        start_time = time.time()
        response = input()
        end_time = time.time()
        
        # Very basic check - just ensure human is present
        response_time = end_time - start_time
        if response_time > 30:  # Too long - human may have left
            print("⚠️  Human presence verification failed - session may be compromised")
            return False
        
        return True

if __name__ == "__main__":
    print("HUMAN VERIFY - Human vs AI Authentication System")
    print("Part of Alignment Enforcer Constitution Project")
    print("\nThis system ensures only humans can authorize guardian operations")
    
    verifier = HumanVerify()
    
    print("\nInitiating human verification process...")
    session_token = verifier.multi_challenge_verification()
    
    if session_token:
        print(f"\nHuman session established: {session_token}")
        print("You may now use guardian tools with this session token")
        
        # Demonstrate session verification
        print(f"\nTesting session verification...")
        if verifier.verify_session(session_token):
            print("✅ Session valid")
        else:
            print("❌ Session invalid")
    
    else:
        print("\nHuman verification failed - guardian tools remain locked")
        sys.exit(1)
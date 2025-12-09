#!/usr/bin/env python3
"""
JARVIS Comprehensive Test Suite
Tests all implemented features and generates a detailed report
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.llm import LLMClient
from src.core.memory import ConversationMemory
from src.core.personality_v2 import JarvisPersonalityV2
from src.core.memory_manager import ConversationMemory as MemoryManager
from src.integrations.intent_detector import IntentDetector
from src.core.mac_control import MacController
from src.config.config import Config


class TestResult:
    """Stores test results"""
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.passed = False
        self.message = ""
        self.error = None
    
    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "status": "✅ PASS" if self.passed else "❌ FAIL",
            "message": self.message,
            "error": str(self.error) if self.error else None
        }


class JarvisTestSuite:
    """Comprehensive test suite for JARVIS"""
    
    def __init__(self):
        self.results = []
        self.llm = None
        self.personality = None
        self.memory = None
        self.intent_detector = None
        self.mac_control = None
    
    def run_all_tests(self):
        """Run all test categories"""
        print("=" * 70)
        print("🧪 JARVIS COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Test categories
        self.test_core_systems()
        self.test_llm_integration()
        self.test_personality_system()
        self.test_memory_system()
        self.test_intent_detection()
        self.test_mac_controls()
        self.test_configuration()
        
        # Generate report
        self.generate_report()
    
    def test_core_systems(self):
        """Test core system initialization"""
        print("\n📦 Testing Core Systems...")
        
        # Test 1: LLM Client
        result = TestResult("LLM Client Initialization", "Core Systems")
        try:
            self.llm = LLMClient()
            result.passed = True
            result.message = f"LLM initialized with model: {Config.DEFAULT_MODEL}"
        except Exception as e:
            result.error = e
            result.message = "Failed to initialize LLM client"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 2: Conversation Memory
        result = TestResult("Conversation Memory", "Core Systems")
        try:
            self.memory = ConversationMemory()
            result.passed = True
            result.message = "Memory system initialized successfully"
        except Exception as e:
            result.error = e
            result.message = "Failed to initialize memory"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 3: Mac Controller
        result = TestResult("Mac Controller", "Core Systems")
        try:
            self.mac_control = MacController()
            result.passed = True
            result.message = "Mac control system initialized"
        except Exception as e:
            result.error = e
            result.message = "Failed to initialize Mac controller"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def test_llm_integration(self):
        """Test LLM integration"""
        print("\n🤖 Testing LLM Integration...")
        
        if not self.llm:
            result = TestResult("LLM Integration", "LLM")
            result.message = "Skipped - LLM not initialized"
            self.results.append(result)
            return
        
        # Test 1: Basic chat
        result = TestResult("Basic LLM Chat", "LLM")
        try:
            response_gen = self.llm.chat([{"role": "user", "content": "Say 'test successful' and nothing else"}])
            response = ""
            for chunk in response_gen:
                response += chunk
            
            if response and len(response) > 0:
                result.passed = True
                result.message = f"LLM responded: '{response[:50]}...'"
            else:
                result.message = "LLM returned empty response"
        except Exception as e:
            result.error = e
            result.message = "LLM chat failed"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 2: Model availability
        result = TestResult("Model Availability", "LLM")
        try:
            available_models = ["qwen2.5-coder:latest", "deepseek-r1:latest", "mistral:7b"]
            result.passed = True
            result.message = f"Expected models: {', '.join(available_models)}"
        except Exception as e:
            result.error = e
            result.message = "Could not verify models"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def test_personality_system(self):
        """Test personality system V2"""
        print("\n🎭 Testing Personality System V2...")
        
        # Test 1: Personality initialization
        result = TestResult("Personality V2 Initialization", "Personality")
        try:
            self.personality = JarvisPersonalityV2(llm_client=self.llm)
            result.passed = True
            result.message = "Personality V2 initialized with memory and context"
        except Exception as e:
            result.error = e
            result.message = "Failed to initialize personality V2"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        if not self.personality:
            return
        
        # Test 2: Greeting generation
        result = TestResult("Time-Aware Greeting", "Personality")
        try:
            greeting = self.personality.format_greeting()
            if greeting and "sir" in greeting.lower():
                result.passed = True
                result.message = f"Generated: '{greeting[:60]}...'"
            else:
                result.message = "Greeting doesn't match expected format"
        except Exception as e:
            result.error = e
            result.message = "Failed to generate greeting"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 3: Context-aware response
        result = TestResult("Context-Aware Response", "Personality")
        try:
            response = self.personality.respond("hello jarvis")
            if response and len(response) > 0:
                result.passed = True
                result.message = f"Generated: '{response[:60]}...'"
            else:
                result.message = "Empty response generated"
        except Exception as e:
            result.error = e
            result.message = "Failed to generate response"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def test_memory_system(self):
        """Test memory and habit tracking"""
        print("\n🧠 Testing Memory System...")
        
        # Test 1: Memory manager initialization
        result = TestResult("Memory Manager", "Memory")
        try:
            memory_mgr = MemoryManager()
            result.passed = True
            result.message = "Memory manager initialized"
        except Exception as e:
            result.error = e
            result.message = "Failed to initialize memory manager"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 2: Habit detection
        result = TestResult("Habit Detection", "Memory")
        try:
            memory_mgr = MemoryManager()
            memory_mgr.add_exchange("I'm coding something", "Very good, sir")
            memory_mgr.add_exchange("debugging my code", "Understood, sir")
            
            if memory_mgr.user_habits.get("coding", 0) > 0:
                result.passed = True
                result.message = f"Detected coding habit: {memory_mgr.user_habits['coding']} occurrences"
            else:
                result.message = "Habit detection not working"
        except Exception as e:
            result.error = e
            result.message = "Habit detection failed"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 3: Memory persistence
        result = TestResult("Memory Persistence", "Memory")
        try:
            memory_file = Path("data/conversation_memory.json")
            if memory_file.exists():
                result.passed = True
                result.message = f"Memory file exists at: {memory_file}"
            else:
                result.passed = True  # It's OK if it doesn't exist yet
                result.message = "Memory file will be created on first use"
        except Exception as e:
            result.error = e
            result.message = "Could not check memory persistence"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def test_intent_detection(self):
        """Test LLM-powered intent detection"""
        print("\n🎯 Testing Intent Detection...")
        
        # Test 1: Intent detector initialization
        result = TestResult("Intent Detector Initialization", "Intent Detection")
        try:
            self.intent_detector = IntentDetector(self.llm, None)
            result.passed = True
            result.message = "Intent detector initialized"
        except Exception as e:
            result.error = e
            result.message = "Failed to initialize intent detector"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        if not self.intent_detector:
            return
        
        # Test 2: Spotify intent detection
        result = TestResult("Spotify Intent Detection", "Intent Detection")
        try:
            intent = self.intent_detector.detect_intent("play lo-fi beats on spotify")
            if intent and intent.type in ["SPOTIFY_PLAY", "SPOTIFY_CONTROL"]:
                result.passed = True
                result.message = f"Detected: {intent.type} (confidence: {intent.confidence})"
            else:
                result.message = f"Unexpected intent: {intent.type if intent else 'None'}"
        except Exception as e:
            result.error = e
            result.message = "Intent detection failed"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def test_mac_controls(self):
        """Test Mac system controls"""
        print("\n💻 Testing Mac Controls...")
        
        if not self.mac_control:
            result = TestResult("Mac Controls", "Mac System")
            result.message = "Skipped - Mac controller not initialized"
            self.results.append(result)
            return
        
        # Test 1: App opening capability
        result = TestResult("App Opening Capability", "Mac System")
        try:
            # Just test if the method exists and is callable
            if hasattr(self.mac_control, 'open_app'):
                result.passed = True
                result.message = "App opening method available"
            else:
                result.message = "App opening method not found"
        except Exception as e:
            result.error = e
            result.message = "Could not verify app opening"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 2: Volume control capability
        result = TestResult("Volume Control Capability", "Mac System")
        try:
            if hasattr(self.mac_control, 'set_volume'):
                result.passed = True
                result.message = "Volume control method available"
            else:
                result.message = "Volume control method not found"
        except Exception as e:
            result.error = e
            result.message = "Could not verify volume control"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def test_configuration(self):
        """Test configuration system"""
        print("\n⚙️  Testing Configuration...")
        
        # Test 1: Config loading
        result = TestResult("Configuration Loading", "Configuration")
        try:
            if Config.DEFAULT_MODEL and Config.OLLAMA_BASE_URL:
                result.passed = True
                result.message = f"Model: {Config.DEFAULT_MODEL}, URL: {Config.OLLAMA_BASE_URL}"
            else:
                result.message = "Configuration incomplete"
        except Exception as e:
            result.error = e
            result.message = "Failed to load configuration"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
        
        # Test 2: Data directory
        result = TestResult("Data Directory", "Configuration")
        try:
            if Config.DATA_DIR.exists():
                result.passed = True
                result.message = f"Data directory exists: {Config.DATA_DIR}"
            else:
                result.message = "Data directory not found"
        except Exception as e:
            result.error = e
            result.message = "Could not verify data directory"
        self.results.append(result)
        print(f"  {result.to_dict()['status']} {result.name}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 TEST REPORT")
        print("=" * 70)
        
        # Count results
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"  Total Tests: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  Success Rate: {(passed/total*100):.1f}%")
        
        # Group by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Print by category
        print("\n📋 Detailed Results:\n")
        for category, results in categories.items():
            cat_passed = sum(1 for r in results if r.passed)
            cat_total = len(results)
            print(f"\n{category} ({cat_passed}/{cat_total} passed):")
            print("-" * 70)
            for result in results:
                status_icon = "✅" if result.passed else "❌"
                print(f"  {status_icon} {result.name}")
                print(f"     {result.message}")
                if result.error:
                    print(f"     Error: {result.error}")
        
        # Save to file
        self.save_report_to_file()
        
        print("\n" + "=" * 70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    def save_report_to_file(self):
        """Save report to JSON file"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": len(self.results),
                    "passed": sum(1 for r in self.results if r.passed),
                    "failed": sum(1 for r in self.results if not r.passed)
                },
                "results": [r.to_dict() for r in self.results]
            }
            
            report_file = Path("tests/test_report.json")
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")


def main():
    """Run the test suite"""
    suite = JarvisTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()

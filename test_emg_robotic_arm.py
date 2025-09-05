#!/usr/bin/env python3
"""
Test script for EMG Robotic Arm Control System
This script tests the complete system without requiring actual hardware.
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add the chordspy module to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_gesture_detector():
    """Test the EMG gesture detector."""
    print("🧪 Testing EMG Gesture Detector...")
    
    try:
        from chordspy.emg_gesture_detector import EMGGestureDetector, GrabReleaseController
        
        # Create controller
        controller = GrabReleaseController()
        
        # Create detector
        detector = EMGGestureDetector(
            sampling_rate=1000,
            threshold_multiplier=2.0,
            gesture_callback=controller.process_gesture
        )
        
        print("✅ Gesture detector created successfully")
        
        # Simulate EMG data
        print("📊 Simulating EMG data...")
        for i in range(1000):
            # Simulate fist close/open cycles
            if 100 <= i <= 200 or 400 <= i <= 500 or 700 <= i <= 800:
                # Fist close: high amplitude
                sample = np.random.normal(500, 100)
            else:
                # Fist open: low amplitude
                sample = np.random.normal(50, 20)
            
            detector.add_sample(sample)
        
        # Print results
        stats = detector.get_statistics()
        controller_state = controller.get_state()
        
        print(f"✅ Gesture Detection Results:")
        print(f"   - Total gestures: {stats['total_gestures']}")
        print(f"   - False positives: {stats['false_positives']}")
        print(f"   - Controller state: {controller_state['state']}")
        print(f"   - Fist cycles: {controller_state['fist_cycle_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gesture detector test failed: {e}")
        return False

def test_robotic_arm_controller():
    """Test the robotic arm controller."""
    print("\n🤖 Testing Robotic Arm Controller...")
    
    try:
        from chordspy.robotic_arm_controller import RoboticArmController
        
        # Create controller in mock mode
        arm = RoboticArmController(mock_mode=True)
        
        print("✅ Robotic arm controller created successfully")
        
        # Test connection
        if arm.connect():
            print("✅ Connection successful")
            
            # Test commands
            arm.grab_object()
            time.sleep(0.5)
            
            arm.release_object()
            time.sleep(0.5)
            
            arm.move_joint('base', 45)
            time.sleep(0.5)
            
            # Test status
            status = arm.get_status()
            print(f"✅ Status check: {status['connected']}")
            print(f"   - Commands sent: {status['commands_sent']}")
            print(f"   - Current position: {status['position']}")
            
            arm.disconnect()
            print("✅ Disconnection successful")
            
            return True
        else:
            print("❌ Connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Robotic arm controller test failed: {e}")
        return False

def test_integration():
    """Test the complete system integration."""
    print("\n🔗 Testing System Integration...")
    
    try:
        from chordspy.emg_gesture_detector import EMGGestureDetector, GrabReleaseController
        from chordspy.robotic_arm_controller import RoboticArmController
        
        # Create components
        arm = RoboticArmController(mock_mode=True)
        controller = GrabReleaseController()
        
        def send_command(command):
            if command == 'grab':
                arm.grab_object()
                print("🤖 Executing: GRAB")
            elif command == 'release':
                arm.release_object()
                print("🤖 Executing: RELEASE")
        
        # Set up command callback
        controller.command_callback = send_command
        
        # Create detector
        detector = EMGGestureDetector(
            sampling_rate=1000,
            threshold_multiplier=2.0,
            gesture_callback=controller.process_gesture
        )
        
        # Connect arm
        if not arm.connect():
            print("❌ Failed to connect robotic arm")
            return False
        
        print("✅ All components initialized")
        
        # Simulate complete workflow
        print("🎮 Simulating complete EMG control workflow...")
        
        # Simulate 3 fist close/open cycles
        for cycle in range(3):
            print(f"\n--- Cycle {cycle + 1} ---")
            
            # Fist close phase
            for i in range(100):
                sample = np.random.normal(500, 100)  # High amplitude
                detector.add_sample(sample)
                time.sleep(0.001)
            
            # Fist open phase
            for i in range(100):
                sample = np.random.normal(50, 20)  # Low amplitude
                detector.add_sample(sample)
                time.sleep(0.001)
            
            time.sleep(0.5)  # Pause between cycles
        
        # Check final state
        stats = detector.get_statistics()
        controller_state = controller.get_state()
        arm_status = arm.get_status()
        
        print(f"\n✅ Integration Test Results:")
        print(f"   - Gestures detected: {stats['total_gestures']}")
        print(f"   - Controller state: {controller_state['state']}")
        print(f"   - Fist cycles: {controller_state['fist_cycle_count']}")
        print(f"   - Arm commands sent: {arm_status['commands_sent']}")
        
        arm.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting EMG Robotic Arm Control System Tests")
    print("=" * 60)
    
    tests = [
        ("Gesture Detector", test_gesture_detector),
        ("Robotic Arm Controller", test_robotic_arm_controller),
        ("System Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
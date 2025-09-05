"""
Robotic Arm Controller Module
This module provides communication interface for SAZ DEKOR robotic arm integration.
It handles serial communication and command formatting for the robotic arm.
"""

import serial
import time
import threading
from typing import Optional, Dict, Any
import json

class RoboticArmController:
    """
    Controller for SAZ DEKOR® DIY 6-DOF Robot Mechanical Arm Kits.
    
    This class handles:
    - Serial communication with the robotic arm
    - Command formatting and sending
    - Status monitoring
    - Safety features
    """
    
    def __init__(self, 
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 timeout: float = 1.0,
                 mock_mode: bool = True):
        """
        Initialize the robotic arm controller.
        
        Args:
            port: Serial port for communication (None for auto-detect)
            baudrate: Serial communication baud rate
            timeout: Serial communication timeout
            mock_mode: If True, simulate arm without actual hardware
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock_mode = mock_mode
        
        # Connection state
        self.connected = False
        self.serial_connection = None
        
        # Arm state
        self.current_position = {
            'base': 90,      # Base rotation (0-180)
            'shoulder': 90,  # Shoulder joint (0-180)
            'elbow': 90,     # Elbow joint (0-180)
            'wrist': 90,     # Wrist joint (0-180)
            'gripper': 0     # Gripper state (0=open, 1=closed)
        }
        
        # Command queue and threading
        self.command_queue = []
        self.command_lock = threading.Lock()
        self.command_thread = None
        self.running = False
        
        # Safety parameters
        self.max_speed = 50  # Maximum servo speed
        self.safety_enabled = True
        
        # Statistics
        self.commands_sent = 0
        self.commands_failed = 0
        self.last_command_time = 0.0
        
    def connect(self) -> bool:
        """
        Connect to the robotic arm.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.mock_mode:
            print("🤖 Mock Mode: Simulating robotic arm connection")
            self.connected = True
            self._start_command_processor()
            return True
        
        try:
            if self.port is None:
                self.port = self._auto_detect_port()
                if self.port is None:
                    print("❌ No robotic arm port detected")
                    return False
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Test connection
            time.sleep(2)  # Wait for arm to initialize
            if self._test_connection():
                self.connected = True
                self._start_command_processor()
                print(f"✅ Connected to robotic arm on {self.port}")
                return True
            else:
                print("❌ Failed to establish communication with robotic arm")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the robotic arm."""
        self.running = False
        
        if self.command_thread and self.command_thread.is_alive():
            self.command_thread.join(timeout=2.0)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        self.connected = False
        print("🔌 Disconnected from robotic arm")
    
    def _auto_detect_port(self) -> Optional[str]:
        """Auto-detect the robotic arm serial port."""
        import serial.tools.list_ports
        
        # Look for common robotic arm identifiers
        arm_identifiers = ['USB', 'ACM', 'ttyUSB', 'ttyACM']
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            for identifier in arm_identifiers:
                if identifier in port.device or identifier in port.description:
                    print(f"🔍 Found potential robotic arm port: {port.device}")
                    return port.device
        
        return None
    
    def _test_connection(self) -> bool:
        """Test the connection by sending a status request."""
        try:
            # Send status request command
            self._send_raw_command("STATUS")
            time.sleep(0.5)
            
            # Check if we get a response
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode().strip()
                print(f"📡 Arm response: {response}")
                return True
            return False
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def _start_command_processor(self):
        """Start the command processing thread."""
        self.running = True
        self.command_thread = threading.Thread(target=self._command_processor, daemon=True)
        self.command_thread.start()
    
    def _command_processor(self):
        """Process commands from the queue."""
        while self.running:
            if self.command_queue:
                with self.command_lock:
                    if self.command_queue:
                        command = self.command_queue.pop(0)
                        self._execute_command(command)
            time.sleep(0.01)  # 10ms delay
    
    def _execute_command(self, command: Dict[str, Any]):
        """Execute a single command."""
        try:
            command_type = command.get('type')
            
            if command_type == 'grab':
                self._grab_object()
            elif command_type == 'release':
                self._release_object()
            elif command_type == 'move':
                self._move_joint(command.get('joint'), command.get('angle'))
            elif command_type == 'home':
                self._home_position()
            elif command_type == 'status':
                self._get_status()
            
            self.commands_sent += 1
            self.last_command_time = time.time()
            
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            self.commands_failed += 1
    
    def _send_raw_command(self, command: str):
        """Send a raw command to the robotic arm."""
        if self.mock_mode:
            print(f"📤 Mock Command: {command}")
            return
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(f"{command}\n".encode())
    
    def grab_object(self):
        """Grab an object with the robotic arm."""
        command = {'type': 'grab', 'timestamp': time.time()}
        with self.command_lock:
            self.command_queue.append(command)
    
    def release_object(self):
        """Release an object from the robotic arm."""
        command = {'type': 'release', 'timestamp': time.time()}
        with self.command_lock:
            self.command_queue.append(command)
    
    def _grab_object(self):
        """Internal method to execute grab command."""
        if self.mock_mode:
            print("🤖 Mock: GRABBING object")
            self.current_position['gripper'] = 1
        else:
            # Send grab command to actual arm
            self._send_raw_command("GRAB")
            self.current_position['gripper'] = 1
    
    def _release_object(self):
        """Internal method to execute release command."""
        if self.mock_mode:
            print("🤖 Mock: RELEASING object")
            self.current_position['gripper'] = 0
        else:
            # Send release command to actual arm
            self._send_raw_command("RELEASE")
            self.current_position['gripper'] = 0
    
    def move_joint(self, joint: str, angle: int):
        """
        Move a specific joint to a target angle.
        
        Args:
            joint: Joint name ('base', 'shoulder', 'elbow', 'wrist')
            angle: Target angle (0-180)
        """
        if joint not in self.current_position:
            print(f"❌ Invalid joint: {joint}")
            return
        
        if not 0 <= angle <= 180:
            print(f"❌ Invalid angle: {angle} (must be 0-180)")
            return
        
        command = {
            'type': 'move',
            'joint': joint,
            'angle': angle,
            'timestamp': time.time()
        }
        
        with self.command_lock:
            self.command_queue.append(command)
    
    def _move_joint(self, joint: str, angle: int):
        """Internal method to execute joint movement."""
        if self.mock_mode:
            print(f"🤖 Mock: Moving {joint} to {angle}°")
            self.current_position[joint] = angle
        else:
            # Send movement command to actual arm
            command = f"MOVE_{joint.upper()}_{angle}"
            self._send_raw_command(command)
            self.current_position[joint] = angle
    
    def home_position(self):
        """Move the arm to home position."""
        command = {'type': 'home', 'timestamp': time.time()}
        with self.command_lock:
            self.command_queue.append(command)
    
    def _home_position(self):
        """Internal method to execute home position command."""
        if self.mock_mode:
            print("🤖 Mock: Moving to HOME position")
            self.current_position = {
                'base': 90, 'shoulder': 90, 'elbow': 90, 
                'wrist': 90, 'gripper': 0
            }
        else:
            self._send_raw_command("HOME")
            self.current_position = {
                'base': 90, 'shoulder': 90, 'elbow': 90, 
                'wrist': 90, 'gripper': 0
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current arm status and position."""
        return {
            'connected': self.connected,
            'position': self.current_position.copy(),
            'commands_sent': self.commands_sent,
            'commands_failed': self.commands_failed,
            'queue_size': len(self.command_queue),
            'last_command_time': self.last_command_time
        }
    
    def _get_status(self):
        """Internal method to get status from the arm."""
        if not self.mock_mode:
            self._send_raw_command("STATUS")
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all movement."""
        print("🚨 EMERGENCY STOP ACTIVATED")
        
        # Clear command queue
        with self.command_lock:
            self.command_queue.clear()
        
        # Send emergency stop command
        if self.mock_mode:
            print("🤖 Mock: EMERGENCY STOP")
        else:
            self._send_raw_command("EMERGENCY_STOP")
    
    def set_safety_mode(self, enabled: bool):
        """Enable or disable safety mode."""
        self.safety_enabled = enabled
        print(f"🛡️ Safety mode: {'ENABLED' if enabled else 'DISABLED'}")
    
    def is_connected(self) -> bool:
        """Check if the arm is connected."""
        return self.connected
    
    def get_queue_size(self) -> int:
        """Get the number of commands in the queue."""
        return len(self.command_queue)


def test_robotic_arm_controller():
    """Test function for the robotic arm controller."""
    print("Testing Robotic Arm Controller...")
    
    # Create controller in mock mode
    arm = RoboticArmController(mock_mode=True)
    
    # Test connection
    if arm.connect():
        print("✅ Connection successful")
        
        # Test basic commands
        print("\n--- Testing Basic Commands ---")
        arm.grab_object()
        time.sleep(1)
        
        arm.release_object()
        time.sleep(1)
        
        arm.home_position()
        time.sleep(1)
        
        # Test joint movements
        print("\n--- Testing Joint Movements ---")
        arm.move_joint('base', 45)
        time.sleep(1)
        
        arm.move_joint('shoulder', 135)
        time.sleep(1)
        
        arm.move_joint('elbow', 60)
        time.sleep(1)
        
        # Test status
        print("\n--- Current Status ---")
        status = arm.get_status()
        print(json.dumps(status, indent=2))
        
        # Test emergency stop
        print("\n--- Testing Emergency Stop ---")
        arm.emergency_stop()
        
        # Disconnect
        arm.disconnect()
        print("✅ Test completed successfully")
    else:
        print("❌ Connection failed")


if __name__ == "__main__":
    test_robotic_arm_controller()
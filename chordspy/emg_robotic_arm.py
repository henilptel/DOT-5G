"""
Real-time EMG-Controlled Robotic Arm Application
This application integrates EMG gesture detection with robotic arm control.
It provides a complete system for controlling a robotic arm using EMG signals.
"""

# =============================================================================
# GLOBAL CONFIGURATION VARIABLES
# =============================================================================

# Signal Processing Configuration
ENABLE_ADVANCED_FILTERING = True          # Enable/disable advanced filtering
DEFAULT_NOISE_REDUCTION_LEVEL = 2         # Default noise reduction (1-5)
DEFAULT_THRESHOLD_MULTIPLIER = 1          # Default threshold sensitivity (1-10)
DEFAULT_MIN_GESTURE_DURATION = 50         # Minimum gesture duration in ms
DEFAULT_MAX_GESTURE_DURATION = 2000       # Maximum gesture duration in ms

# Visualization Configuration
VISUALIZATION_UPDATE_RATE = 50            # Visualization update rate in ms (20 FPS)
ENABLE_VISUALIZATION_SMOOTHING = True     # Enable smoothing for visualization
VISUALIZATION_SMOOTHING_WINDOW = 3        # Window size for visualization smoothing

# Gesture Detection Configuration
ENABLE_AUTO_VISUALIZATION = True          # Auto-start visualization on EMG connect
ENABLE_CONFIRMATION_DIALOGS = True        # Enable confirmation dialogs for disconnect
GESTURE_COOLDOWN_TIME = 0.5               # Cooldown between gestures in seconds
COMMAND_COOLDOWN_TIME = 1.0               # Cooldown between commands in seconds

# Robotic Arm Configuration
DEFAULT_MOCK_MODE = True                  # Default to mock mode (no hardware)
EMERGENCY_STOP_DELAY = 0.5                # Delay for emergency stop processing

# UI Configuration
ENABLE_DEBUG_LOGGING = True               # Enable detailed debug logging
LOG_MAX_LINES = 100                       # Maximum lines in log display
STATS_UPDATE_INTERVAL = 1000              # Statistics update interval in ms

# Signal Processing Thresholds
OUTLIER_THRESHOLD_BASE = 4.0              # Base outlier threshold
MEDIAN_FILTER_KERNEL = 3                  # Median filter kernel size
MOVING_AVERAGE_WINDOW = 2                 # Moving average window size

# Filter Frequencies
HIGH_PASS_FREQUENCY = 20.0                # High-pass filter frequency (Hz)
LOW_PASS_FREQUENCY = 250.0                # Low-pass filter frequency (Hz)
NOTCH_50_FREQUENCY = [49.0, 51.0]         # 50 Hz notch filter range
NOTCH_60_FREQUENCY = [59.0, 61.0]         # 60 Hz notch filter range

# =============================================================================

import numpy as np
import pylsl
import time
import threading
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QTextEdit, QProgressBar,
                            QGroupBox, QGridLayout, QSlider, QSpinBox, QCheckBox,
                            QMessageBox)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor
import pyqtgraph as pg

from chordspy.emg_gesture_detector import EMGGestureDetector, GrabReleaseController
from chordspy.robotic_arm_controller import RoboticArmController


class EMGDataThread(QThread):
    """Thread for processing EMG data from LSL stream."""
    
    data_received = pyqtSignal(list)  # Signal emitted when new data is received
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.inlet = None
        self.sampling_rate = 1000
        
    def run(self):
        """Main thread loop for processing EMG data."""
        # Find LSL stream
        streams = pylsl.resolve_stream('type', 'EXG')
        if not streams:
            print("❌ No EMG stream found!")
            return
        
        # Connect to stream
        self.inlet = pylsl.StreamInlet(streams[0])
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"📡 Connected to EMG stream at {self.sampling_rate} Hz")
        
        self.running = True
        while self.running:
            try:
                # Pull data from LSL stream
                samples, _ = self.inlet.pull_chunk(timeout=0.1, max_samples=10)
                if samples:
                    # Emit the first channel data
                    for sample in samples:
                        if len(sample) > 0:
                            self.data_received.emit([sample[0]])
            except Exception as e:
                print(f"Error in EMG data thread: {e}")
                break
    
    def stop(self):
        """Stop the data processing thread."""
        self.running = False
        self.wait()


class EMGRoboticArmApp(QMainWindow):
    """Main application window for EMG-controlled robotic arm."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMG-Controlled Robotic Arm")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.emg_thread = EMGDataThread()
        self.gesture_detector = None
        self.grab_release_controller = None
        self.robotic_arm = None
        
        # Data buffers for visualization
        self.emg_buffer = np.zeros(1000)
        self.envelope_buffer = np.zeros(1000)
        self.current_index = 0
        
        # Statistics
        self.total_gestures = 0
        self.total_commands = 0
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Initialize components
        self.initialize_components()
        
    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls and status
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Visualization
        right_panel = self.create_visualization_panel()
        main_layout.addWidget(right_panel, 2)
        
    def create_control_panel(self):
        """Create the control panel widget."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Connection group
        connection_group = QGroupBox("Connection Status")
        connection_layout = QVBoxLayout(connection_group)
        
        self.emg_status_label = QLabel("EMG Stream: ❌ Disconnected")
        self.arm_status_label = QLabel("Robotic Arm: ❌ Disconnected")
        self.visualization_status_label = QLabel("Visualization: ❌ Stopped")
        
        connection_layout.addWidget(self.emg_status_label)
        connection_layout.addWidget(self.arm_status_label)
        connection_layout.addWidget(self.visualization_status_label)
        
        # Control buttons
        self.emg_toggle_btn = QPushButton("Connect to EMG Stream")
        self.arm_toggle_btn = QPushButton("Connect Robotic Arm")
        self.start_btn = QPushButton("Start Control")
        self.stop_btn = QPushButton("Stop Control")
        self.emergency_btn = QPushButton("🚨 EMERGENCY STOP")
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.emergency_btn.setStyleSheet("QPushButton { background-color: red; color: white; font-weight: bold; }")
        self.emg_toggle_btn.setStyleSheet("QPushButton { background-color: green; color: white; }")
        self.arm_toggle_btn.setStyleSheet("QPushButton { background-color: green; color: white; }")
        
        connection_layout.addWidget(self.emg_toggle_btn)
        connection_layout.addWidget(self.arm_toggle_btn)
        connection_layout.addWidget(self.start_btn)
        connection_layout.addWidget(self.stop_btn)
        connection_layout.addWidget(self.emergency_btn)
        
        layout.addWidget(connection_group)
        
        # Gesture detection settings
        gesture_group = QGroupBox("Gesture Detection Settings")
        gesture_layout = QGridLayout(gesture_group)
        
        # Threshold multiplier
        gesture_layout.addWidget(QLabel("Threshold Multiplier:"), 0, 0)
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(1, 10)
        self.threshold_spinbox.setValue(DEFAULT_THRESHOLD_MULTIPLIER)
        gesture_layout.addWidget(self.threshold_spinbox, 0, 1)
        
        # Min gesture duration
        gesture_layout.addWidget(QLabel("Min Duration (ms):"), 1, 0)
        self.min_duration_spinbox = QSpinBox()
        self.min_duration_spinbox.setRange(50, 1000)
        self.min_duration_spinbox.setValue(DEFAULT_MIN_GESTURE_DURATION)
        gesture_layout.addWidget(self.min_duration_spinbox, 1, 1)
        
        # Max gesture duration
        gesture_layout.addWidget(QLabel("Max Duration (ms):"), 2, 0)
        self.max_duration_spinbox = QSpinBox()
        self.max_duration_spinbox.setRange(500, 5000)
        self.max_duration_spinbox.setValue(DEFAULT_MAX_GESTURE_DURATION)
        gesture_layout.addWidget(self.max_duration_spinbox, 2, 1)
        
        # Mock mode checkbox
        self.mock_mode_checkbox = QCheckBox("Mock Mode (No Hardware)")
        self.mock_mode_checkbox.setChecked(DEFAULT_MOCK_MODE)
        gesture_layout.addWidget(self.mock_mode_checkbox, 3, 0, 1, 2)
        
        # Signal processing options
        gesture_layout.addWidget(QLabel("Signal Processing:"), 4, 0)
        self.advanced_filtering_checkbox = QCheckBox("Advanced Filtering (Recommended)")
        self.advanced_filtering_checkbox.setChecked(ENABLE_ADVANCED_FILTERING)
        gesture_layout.addWidget(self.advanced_filtering_checkbox, 4, 1)
        
        # Noise reduction level
        gesture_layout.addWidget(QLabel("Noise Reduction:"), 5, 0)
        self.noise_reduction_spinbox = QSpinBox()
        self.noise_reduction_spinbox.setRange(1, 5)
        self.noise_reduction_spinbox.setValue(DEFAULT_NOISE_REDUCTION_LEVEL)
        self.noise_reduction_spinbox.setToolTip("1=Minimal, 5=Maximum noise reduction")
        gesture_layout.addWidget(self.noise_reduction_spinbox, 5, 1)
        
        layout.addWidget(gesture_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.gesture_count_label = QLabel("Gestures Detected: 0")
        self.command_count_label = QLabel("Commands Sent: 0")
        self.baseline_label = QLabel("Baseline RMS: 0.00")
        self.threshold_label = QLabel("Current Threshold: 0.00")
        
        stats_layout.addWidget(self.gesture_count_label)
        stats_layout.addWidget(self.command_count_label)
        stats_layout.addWidget(self.baseline_label)
        stats_layout.addWidget(self.threshold_label)
        
        layout.addWidget(stats_group)
        
        # Current state group
        state_group = QGroupBox("Current State")
        state_layout = QVBoxLayout(state_group)
        
        self.current_state_label = QLabel("State: IDLE")
        self.next_action_label = QLabel("Next Action: GRAB")
        self.cycle_count_label = QLabel("Fist Cycles: 0")
        
        state_layout.addWidget(self.current_state_label)
        state_layout.addWidget(self.next_action_label)
        state_layout.addWidget(self.cycle_count_label)
        
        layout.addWidget(state_group)
        
        # Log output
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        return panel
    
    def create_visualization_panel(self):
        """Create the visualization panel widget."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # EMG signal plot
        self.emg_plot = pg.PlotWidget(title="Real-time EMG Signal")
        self.emg_plot.setBackground('w')
        self.emg_plot.showGrid(x=True, y=True)
        self.emg_plot.setLabel('left', 'Amplitude')
        self.emg_plot.setLabel('bottom', 'Time (s)')
        
        # EMG envelope plot
        self.envelope_plot = pg.PlotWidget(title="EMG Envelope & Threshold")
        self.envelope_plot.setBackground('w')
        self.envelope_plot.showGrid(x=True, y=True)
        self.envelope_plot.setLabel('left', 'RMS')
        self.envelope_plot.setLabel('bottom', 'Time (s)')
        
        # Plot curves
        self.emg_curve = self.emg_plot.plot(pen=pg.mkPen('b', width=1))
        self.envelope_curve = self.envelope_plot.plot(pen=pg.mkPen('r', width=2))
        self.threshold_line = self.envelope_plot.plot(pen=pg.mkPen('g', width=2, style=pg.QtCore.Qt.DashLine))
        
        layout.addWidget(self.emg_plot)
        layout.addWidget(self.envelope_plot)
        
        return panel
    
    def setup_connections(self):
        """Setup signal connections."""
        # Button connections
        self.emg_toggle_btn.clicked.connect(self.toggle_emg_stream)
        self.arm_toggle_btn.clicked.connect(self.toggle_robotic_arm)
        self.start_btn.clicked.connect(self.start_control)
        self.stop_btn.clicked.connect(self.stop_control)
        self.emergency_btn.clicked.connect(self.emergency_stop)
        
        # EMG data thread connection
        self.emg_thread.data_received.connect(self.process_emg_data)
        
        # Settings connections
        self.threshold_spinbox.valueChanged.connect(self.update_gesture_settings)
        self.min_duration_spinbox.valueChanged.connect(self.update_gesture_settings)
        self.max_duration_spinbox.valueChanged.connect(self.update_gesture_settings)
        self.advanced_filtering_checkbox.toggled.connect(self.update_gesture_settings)
        self.noise_reduction_spinbox.valueChanged.connect(self.update_gesture_settings)
        
        # Update timer for visualization (initially stopped)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_visualization)
        # Don't start automatically - will start when EMG connects
        
        # Statistics update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(STATS_UPDATE_INTERVAL)
    
    def initialize_components(self):
        """Initialize the gesture detector and robotic arm controller."""
        # Initialize grab/release controller
        self.grab_release_controller = GrabReleaseController(
            command_callback=self.send_arm_command
        )
        
        # Initialize robotic arm controller
        self.robotic_arm = RoboticArmController(mock_mode=True)
        
        self.log_message("✅ Components initialized")
    
    def _start_visualization(self):
        """Start the real-time visualization."""
        if not self.update_timer.isActive():
            self.update_timer.start(VISUALIZATION_UPDATE_RATE)
            self.visualization_status_label.setText("Visualization: ✅ Active")
            if ENABLE_DEBUG_LOGGING:
                self.log_message("📊 Started real-time visualization")
                self.log_message("📊 Visualization is now active - you should see EMG plots")
        else:
            if ENABLE_DEBUG_LOGGING:
                self.log_message("📊 Visualization was already active")
    
    def _stop_visualization(self):
        """Stop the real-time visualization."""
        if self.update_timer.isActive():
            self.update_timer.stop()
            # Clear the plots
            self.emg_curve.setData([], [])
            self.envelope_curve.setData([], [])
            self.threshold_line.setData([], [])
            self.visualization_status_label.setText("Visualization: ❌ Stopped")
            self.log_message("📊 Stopped real-time visualization")
    
    def toggle_emg_stream(self):
        """Toggle EMG stream connection (connect/disconnect)."""
        if self.emg_thread.isRunning():
            # Currently connected - disconnect
            self._disconnect_emg_stream()
        else:
            # Currently disconnected - connect
            self._connect_emg_stream()
    
    def _connect_emg_stream(self):
        """Connect to EMG LSL stream."""
        try:
            self.emg_thread.start()
            self.emg_status_label.setText("EMG Stream: ✅ Connected")
            self.emg_toggle_btn.setText("Disconnect EMG Stream")
            self.emg_toggle_btn.setStyleSheet("QPushButton { background-color: orange; color: white; }")
            self.log_message("📡 Connected to EMG stream")
            
            # Auto-start visualization when EMG stream connects
            self._start_visualization()
            
            # Enable start button if robotic arm is also connected
            if self.robotic_arm and self.robotic_arm.is_connected():
                self.start_btn.setEnabled(True)
            
        except Exception as e:
            self.log_message(f"❌ Failed to connect to EMG stream: {e}")
    
    def _disconnect_emg_stream(self):
        """Safely disconnect from EMG LSL stream."""
        # Show confirmation dialog if enabled
        if ENABLE_CONFIRMATION_DIALOGS:
            reply = QMessageBox.question(
                self, 
                'Disconnect EMG Stream', 
                'Are you sure you want to disconnect from the EMG stream?\n\nThis will stop all gesture detection.',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        
        try:
            # Stop control first if running
            if self.gesture_detector and self.gesture_detector.running:
                self.stop_control()
                self.log_message("⏹️ Stopped control before disconnecting EMG stream")
            
            # Stop the EMG data thread
            if self.emg_thread.isRunning():
                self.emg_thread.stop()
                self.log_message("📡 Disconnected from EMG stream")
            
            # Update UI
            self.emg_status_label.setText("EMG Stream: ❌ Disconnected")
            self.emg_toggle_btn.setText("Connect to EMG Stream")
            self.emg_toggle_btn.setStyleSheet("QPushButton { background-color: green; color: white; }")
            self.start_btn.setEnabled(False)
            
            # Stop visualization when EMG stream disconnects
            self._stop_visualization()
            
            # Reset gesture detector
            if self.gesture_detector:
                self.gesture_detector.reset_statistics()
                self.log_message("🔄 Reset gesture detector statistics")
            
        except Exception as e:
            self.log_message(f"❌ Error disconnecting EMG stream: {e}")
    
    def _emergency_disconnect_emg_stream(self):
        """Emergency disconnect from EMG LSL stream (no confirmation)."""
        try:
            # Stop control first if running
            if self.gesture_detector and self.gesture_detector.running:
                self.gesture_detector.stop_detection()
                self.log_message("⏹️ Stopped control before emergency EMG disconnect")
            
            # Stop the EMG data thread
            if self.emg_thread.isRunning():
                self.emg_thread.stop()
                self.log_message("📡 Emergency disconnected from EMG stream")
            
            # Update UI
            self.emg_status_label.setText("EMG Stream: ❌ Disconnected")
            self.emg_toggle_btn.setText("Connect to EMG Stream")
            self.emg_toggle_btn.setStyleSheet("QPushButton { background-color: green; color: white; }")
            self.start_btn.setEnabled(False)
            
            # Reset gesture detector
            if self.gesture_detector:
                self.gesture_detector.reset_statistics()
                self.log_message("🔄 Reset gesture detector statistics")
            
        except Exception as e:
            self.log_message(f"❌ Error during emergency EMG disconnect: {e}")
    
    def toggle_robotic_arm(self):
        """Toggle robotic arm connection (connect/disconnect)."""
        if self.robotic_arm and self.robotic_arm.is_connected():
            # Currently connected - disconnect
            self._disconnect_robotic_arm()
        else:
            # Currently disconnected - connect
            self._connect_robotic_arm()
    
    def _connect_robotic_arm(self):
        """Connect to robotic arm."""
        try:
            mock_mode = self.mock_mode_checkbox.isChecked()
            self.robotic_arm = RoboticArmController(mock_mode=mock_mode)
            
            if self.robotic_arm.connect():
                self.arm_status_label.setText("Robotic Arm: ✅ Connected")
                self.arm_toggle_btn.setText("Disconnect Robotic Arm")
                self.arm_toggle_btn.setStyleSheet("QPushButton { background-color: orange; color: white; }")
                # Enable start button only if EMG stream is also connected
                if self.emg_thread.isRunning():
                    self.start_btn.setEnabled(True)
                self.log_message("🤖 Connected to robotic arm")
            else:
                self.log_message("❌ Failed to connect to robotic arm")
        except Exception as e:
            self.log_message(f"❌ Robotic arm connection error: {e}")
    
    def _disconnect_robotic_arm(self):
        """Safely disconnect from robotic arm."""
        # Show confirmation dialog if enabled
        if ENABLE_CONFIRMATION_DIALOGS:
            reply = QMessageBox.question(
                self, 
                'Disconnect Robotic Arm', 
                'Are you sure you want to disconnect from the robotic arm?\n\nThis will send an emergency stop and disconnect the arm.',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        
        try:
            # Stop control first if running
            if self.gesture_detector and self.gesture_detector.running:
                self.stop_control()
                self.log_message("⏹️ Stopped control before disconnecting robotic arm")
            
            # Emergency stop the arm if connected
            if self.robotic_arm and self.robotic_arm.is_connected():
                self.robotic_arm.emergency_stop()
                self.log_message("🚨 Emergency stop sent to robotic arm")
                time.sleep(0.5)  # Give time for emergency stop to process
            
            # Disconnect the arm
            if self.robotic_arm:
                self.robotic_arm.disconnect()
                self.log_message("🤖 Disconnected from robotic arm")
            
            # Update UI
            self.arm_status_label.setText("Robotic Arm: ❌ Disconnected")
            self.arm_toggle_btn.setText("Connect Robotic Arm")
            self.arm_toggle_btn.setStyleSheet("QPushButton { background-color: green; color: white; }")
            self.start_btn.setEnabled(False)
            
            # Reset controller state
            if self.grab_release_controller:
                self.grab_release_controller.reset()
                self.log_message("🔄 Reset grab/release controller state")
            
        except Exception as e:
            self.log_message(f"❌ Error disconnecting robotic arm: {e}")
    
    def _emergency_disconnect_robotic_arm(self):
        """Emergency disconnect from robotic arm (no confirmation)."""
        try:
            # Stop control first if running
            if self.gesture_detector and self.gesture_detector.running:
                self.gesture_detector.stop_detection()
                self.log_message("⏹️ Stopped control before emergency robotic arm disconnect")
            
            # Emergency stop the arm if connected
            if self.robotic_arm and self.robotic_arm.is_connected():
                self.robotic_arm.emergency_stop()
                self.log_message("🚨 Emergency stop sent to robotic arm")
                time.sleep(0.5)  # Give time for emergency stop to process
            
            # Disconnect the arm
            if self.robotic_arm:
                self.robotic_arm.disconnect()
                self.log_message("🤖 Emergency disconnected from robotic arm")
            
            # Update UI
            self.arm_status_label.setText("Robotic Arm: ❌ Disconnected")
            self.arm_toggle_btn.setText("Connect Robotic Arm")
            self.arm_toggle_btn.setStyleSheet("QPushButton { background-color: green; color: white; }")
            self.start_btn.setEnabled(False)
            
            # Reset controller state
            if self.grab_release_controller:
                self.grab_release_controller.reset()
                self.log_message("🔄 Reset grab/release controller state")
            
        except Exception as e:
            self.log_message(f"❌ Error during emergency robotic arm disconnect: {e}")
    
    def start_control(self):
        """Start EMG control of robotic arm."""
        if not self.gesture_detector:
            self.initialize_gesture_detector()
        
        self.gesture_detector.start_detection()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_message("🎮 Started EMG control")
    
    def stop_control(self):
        """Stop EMG control of robotic arm."""
        if self.gesture_detector:
            self.gesture_detector.stop_detection()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_message("⏹️ Stopped EMG control")
    
    def emergency_stop(self):
        """Emergency stop all operations."""
        try:
            # Stop control first
            self.stop_control()
            
            # Emergency stop the robotic arm
            if self.robotic_arm and self.robotic_arm.is_connected():
                self.robotic_arm.emergency_stop()
                self.log_message("🚨 Emergency stop sent to robotic arm")
            
            # Disconnect EMG stream (no confirmation for emergency)
            if self.emg_thread.isRunning():
                self._emergency_disconnect_emg_stream()
                self.log_message("🚨 EMG stream disconnected")
            
            # Stop visualization
            self._stop_visualization()
            
            # Disconnect robotic arm (no confirmation for emergency)
            if self.robotic_arm and self.robotic_arm.is_connected():
                self._emergency_disconnect_robotic_arm()
                self.log_message("🚨 Robotic arm disconnected")
            
            self.log_message("🚨 EMERGENCY STOP COMPLETE - All systems disconnected")
            
        except Exception as e:
            self.log_message(f"❌ Error during emergency stop: {e}")
    
    def initialize_gesture_detector(self):
        """Initialize the gesture detector with current settings."""
        threshold_multiplier = self.threshold_spinbox.value()
        min_duration = self.min_duration_spinbox.value() / 1000.0
        max_duration = self.max_duration_spinbox.value() / 1000.0
        
        self.gesture_detector = EMGGestureDetector(
            sampling_rate=1000,
            threshold_multiplier=threshold_multiplier,
            min_gesture_duration=min_duration,
            max_gesture_duration=max_duration,
            gesture_callback=self.grab_release_controller.process_gesture
        )
        
        # Set noise reduction level
        noise_reduction = self.noise_reduction_spinbox.value()
        self.gesture_detector.noise_reduction_level = noise_reduction
        
        self.log_message(f"🎯 Gesture detector initialized (threshold: {threshold_multiplier}x, noise reduction: {noise_reduction})")
    
    def update_gesture_settings(self):
        """Update gesture detector settings."""
        if self.gesture_detector:
            threshold_multiplier = self.threshold_spinbox.value()
            self.gesture_detector.set_threshold_multiplier(threshold_multiplier)
            
            # Log signal processing settings
            advanced_filtering = self.advanced_filtering_checkbox.isChecked()
            noise_reduction = self.noise_reduction_spinbox.value()
            self.log_message(f"🔧 Signal processing: Advanced={advanced_filtering}, Noise reduction={noise_reduction}")
    
    def process_emg_data(self, data):
        """Process incoming EMG data."""
        if not data:
            return
        
        sample = data[0]
        
        # Add to visualization buffer
        self.emg_buffer[self.current_index] = sample
        self.current_index = (self.current_index + 1) % len(self.emg_buffer)
        
        # Process with gesture detector
        if self.gesture_detector:
            self.gesture_detector.add_sample(sample)
    
    def send_arm_command(self, command):
        """Send command to robotic arm."""
        if self.robotic_arm and self.robotic_arm.is_connected():
            if command == 'grab':
                self.robotic_arm.grab_object()
                self.total_commands += 1
                self.log_message("🤖 Command: GRAB")
            elif command == 'release':
                self.robotic_arm.release_object()
                self.total_commands += 1
                self.log_message("🤖 Command: RELEASE")
    
    def update_visualization(self):
        """Update the visualization plots with enhanced signal processing."""
        # Always update EMG plot if we have data
        time_data = np.linspace(0, 1, len(self.emg_buffer))
        
        # Apply basic smoothing for visualization
        if len(self.emg_buffer) > 0:
            # Apply moving average for smoother visualization
            smoothed_buffer = self._apply_visualization_smoothing(self.emg_buffer)
            self.emg_curve.setData(time_data, smoothed_buffer)
        
        # Update envelope plot with improved RMS calculation
        recent_data = self.emg_buffer[-100:]  # Last 100 samples
        if len(recent_data) > 0:
            # Apply smoothing to recent data for better envelope
            smoothed_recent = self._apply_visualization_smoothing(recent_data)
            rms_value = np.sqrt(np.mean(smoothed_recent ** 2))
            self.envelope_buffer[self.current_index] = rms_value
            
            envelope_time = np.linspace(0, 1, len(self.envelope_buffer))
            self.envelope_curve.setData(envelope_time, self.envelope_buffer)
            
            # Update threshold line if gesture detector is available
            if self.gesture_detector:
                stats = self.gesture_detector.get_statistics()
                threshold_value = stats.get('adaptive_threshold', 0)
                self.threshold_line.setData([0, 1], [threshold_value, threshold_value])
            else:
                # Show a default threshold line based on smoothed data
                default_threshold = np.mean(smoothed_recent) * 2
                self.threshold_line.setData([0, 1], [default_threshold, default_threshold])
    
    def _apply_visualization_smoothing(self, signal: np.ndarray) -> np.ndarray:
        """Apply smoothing for visualization purposes."""
        if not ENABLE_VISUALIZATION_SMOOTHING or len(signal) < VISUALIZATION_SMOOTHING_WINDOW:
            return signal
        
        # Simple moving average for visualization
        kernel = np.ones(VISUALIZATION_SMOOTHING_WINDOW) / VISUALIZATION_SMOOTHING_WINDOW
        smoothed = np.convolve(signal, kernel, mode='same')
        return smoothed
    
    def update_statistics(self):
        """Update the statistics display."""
        if self.gesture_detector:
            stats = self.gesture_detector.get_statistics()
            self.gesture_count_label.setText(f"Gestures Detected: {stats['total_gestures']}")
            self.baseline_label.setText(f"Baseline RMS: {stats['baseline_rms']:.2f}")
            self.threshold_label.setText(f"Current Threshold: {stats['adaptive_threshold']:.2f}")
        
        self.command_count_label.setText(f"Commands Sent: {self.total_commands}")
        
        if self.grab_release_controller:
            state = self.grab_release_controller.get_state()
            self.current_state_label.setText(f"State: {state['state'].upper()}")
            self.next_action_label.setText(f"Next Action: {state['next_action'].upper()}")
            self.cycle_count_label.setText(f"Fist Cycles: {state['fist_cycle_count']}")
    
    def log_message(self, message):
        """Add a message to the log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Keep only last LOG_MAX_LINES lines
        lines = self.log_text.toPlainText().split('\n')
        if len(lines) > LOG_MAX_LINES:
            self.log_text.setPlainText('\n'.join(lines[-LOG_MAX_LINES:]))
    
    def closeEvent(self, event):
        """Handle application close event."""
        try:
            # Safely disconnect everything
            self.log_message("🔄 Application closing - disconnecting all systems...")
            
            # Stop control first
            self.stop_control()
            
            # Disconnect EMG stream (no confirmation on app close)
            if self.emg_thread.isRunning():
                self._emergency_disconnect_emg_stream()
            
            # Stop visualization
            self._stop_visualization()
            
            # Disconnect robotic arm (no confirmation on app close)
            if self.robotic_arm and self.robotic_arm.is_connected():
                self._emergency_disconnect_robotic_arm()
            
            self.log_message("✅ Application closed safely")
            
        except Exception as e:
            self.log_message(f"❌ Error during application close: {e}")
        finally:
            event.accept()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = EMGRoboticArmApp()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
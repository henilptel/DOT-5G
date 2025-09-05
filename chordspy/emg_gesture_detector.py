"""
Real-time EMG Gesture Detection Module
This module provides real-time detection of fist close/open gestures for robotic arm control.
It implements a simple threshold-based approach that can be extended with ML models later.
"""

# =============================================================================
# GLOBAL CONFIGURATION VARIABLES
# =============================================================================

# Filter Frequencies
HIGH_PASS_FREQUENCY = 20.0                # High-pass filter frequency (Hz)
LOW_PASS_FREQUENCY = 250.0                # Low-pass filter frequency (Hz)
NOTCH_50_FREQUENCY = [49.0, 51.0]         # 50 Hz notch filter range
NOTCH_60_FREQUENCY = [59.0, 61.0]         # 60 Hz notch filter range

# Signal Processing Thresholds
OUTLIER_THRESHOLD_BASE = 4.0              # Base outlier threshold
MEDIAN_FILTER_KERNEL = 3                  # Median filter kernel size
MOVING_AVERAGE_WINDOW = 2                 # Moving average window size

# Gesture Detection Configuration
DEFAULT_GESTURE_COOLDOWN = 0.5            # Default cooldown between gestures
DEFAULT_COMMAND_COOLDOWN = 1.0            # Default cooldown between commands

# =============================================================================

import numpy as np
from scipy.signal import butter, filtfilt
from collections import deque
import time
import threading
from typing import Callable, Optional

class EMGGestureDetector:
    """
    Real-time EMG gesture detector for fist close/open cycles.
    
    This detector uses a threshold-based approach to identify:
    - Fist close: EMG amplitude above threshold
    - Fist open: EMG amplitude below threshold
    - Gesture cycles: Complete close->open->close sequences
    """
    
    def __init__(self, 
                 sampling_rate: int = 1000,
                 window_size: int = 200,  # 200ms window
                 overlap: int = 100,      # 50% overlap
                 threshold_multiplier: float = 1.5,
                 min_gesture_duration: float = 0.1,  # 100ms minimum
                 max_gesture_duration: float = 2.0,  # 2s maximum
                 gesture_callback: Optional[Callable] = None):
        """
        Initialize the EMG gesture detector.
        
        Args:
            sampling_rate: Sampling rate in Hz
            window_size: Window size in samples for feature extraction
            overlap: Overlap between windows in samples
            threshold_multiplier: Multiplier for adaptive threshold calculation
            min_gesture_duration: Minimum duration for a valid gesture (seconds)
            max_gesture_duration: Maximum duration for a valid gesture (seconds)
            gesture_callback: Callback function called when gesture is detected
        """
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.overlap = overlap
        self.threshold_multiplier = threshold_multiplier
        self.min_gesture_duration = min_gesture_duration
        self.max_gesture_duration = max_gesture_duration
        self.gesture_callback = gesture_callback
        
        # Signal processing parameters
        self.high_pass_freq = 70.0  # Hz
        self.low_pass_freq = 200.0  # Hz
        
        # Initialize filters
        self._setup_filters()
        
        # Data buffers
        self.raw_buffer = deque(maxlen=window_size * 2)
        self.filtered_buffer = deque(maxlen=window_size * 2)
        self.envelope_buffer = deque(maxlen=window_size * 2)
        
        # Gesture detection state
        self.baseline_rms = 0.0
        self.adaptive_threshold = 0.0
        self.gesture_active = False
        self.gesture_start_time = 0.0
        self.last_gesture_time = 0.0
        self.gesture_cooldown = 0.5  # 500ms cooldown between gestures
        
        # Statistics
        self.total_gestures = 0
        self.false_positives = 0
        
        # Threading
        self.running = False
        self.detection_thread = None
        
    def _setup_filters(self):
        """Setup advanced filters for EMG signal processing."""
        nyquist = self.sampling_rate / 2.0
        
        # High-pass filter - remove DC and low-frequency noise
        self.hp_b, self.hp_a = butter(4, HIGH_PASS_FREQUENCY / nyquist, btype='high')
        
        # Low-pass filter - remove high-frequency noise
        self.lp_b, self.lp_a = butter(4, LOW_PASS_FREQUENCY / nyquist, btype='low')
        
        # Notch filter (50 Hz) - remove power line interference
        self.notch_b, self.notch_a = butter(4, [NOTCH_50_FREQUENCY[0] / nyquist, NOTCH_50_FREQUENCY[1] / nyquist], btype='bandstop')
        
        # Notch filter (60 Hz) - remove power line interference
        self.notch60_b, self.notch60_a = butter(4, [NOTCH_60_FREQUENCY[0] / nyquist, NOTCH_60_FREQUENCY[1] / nyquist], btype='bandstop')
        
    def _calculate_rms(self, signal: np.ndarray) -> float:
        """Calculate RMS (Root Mean Square) of the signal."""
        return np.sqrt(np.mean(signal ** 2))
    
    def _calculate_mav(self, signal: np.ndarray) -> float:
        """Calculate MAV (Mean Absolute Value) of the signal."""
        return np.mean(np.abs(signal))
    
    def _calculate_var(self, signal: np.ndarray) -> float:
        """Calculate VAR (Variance) of the signal."""
        return np.var(signal)
    
    def _apply_moving_average(self, signal: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Apply moving average filter to reduce noise."""
        if len(signal) < window_size:
            return signal
        
        # Use convolution for moving average
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(signal, kernel, mode='same')
        return smoothed
    
    def _apply_median_filter(self, signal: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Apply median filter to remove outliers and spikes."""
        from scipy.signal import medfilt
        return medfilt(signal, kernel_size)
    
    def _apply_savitzky_golay(self, signal: np.ndarray, window_length: int = 11, polyorder: int = 3) -> np.ndarray:
        """Apply Savitzky-Golay filter for smooth signal enhancement."""
        from scipy.signal import savgol_filter
        if len(signal) < window_length:
            return signal
        
        # Ensure window_length is odd
        if window_length % 2 == 0:
            window_length += 1
        
        return savgol_filter(signal, window_length, polyorder)
    
    def _remove_outliers(self, signal: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Remove outliers using statistical thresholding."""
        mean_val = np.mean(signal)
        std_val = np.std(signal)
        
        # Create mask for values within threshold
        mask = np.abs(signal - mean_val) <= threshold * std_val
        
        # Replace outliers with interpolated values
        if not np.all(mask):
            indices = np.arange(len(signal))
            signal_clean = np.interp(indices, indices[mask], signal[mask])
            return signal_clean
        
        return signal
    
    def _extract_features(self, signal: np.ndarray) -> dict:
        """Extract features from EMG signal window."""
        features = {
            'rms': self._calculate_rms(signal),
            'mav': self._calculate_mav(signal),
            'var': self._calculate_var(signal),
            'max': np.max(signal),
            'min': np.min(signal),
            'range': np.max(signal) - np.min(signal)
        }
        return features
    
    def _update_baseline(self, rms_value: float):
        """Update baseline RMS using exponential moving average."""
        alpha = 0.01  # Learning rate
        if self.baseline_rms == 0.0:
            self.baseline_rms = rms_value
        else:
            self.baseline_rms = alpha * rms_value + (1 - alpha) * self.baseline_rms
    
    def _update_threshold(self):
        """Update adaptive threshold based on baseline."""
        self.adaptive_threshold = self.baseline_rms * self.threshold_multiplier
    
    def add_sample(self, sample: float):
        """
        Add a new EMG sample for processing.
        
        Args:
            sample: Raw EMG sample value
        """
        self.raw_buffer.append(sample)
        
        # Process when we have enough data
        if len(self.raw_buffer) >= self.window_size:
            self._process_window()
    
    def _process_window(self):
        """Process a window of EMG data for gesture detection."""
        # Get the most recent window
        window_data = np.array(list(self.raw_buffer)[-self.window_size:])
        
        # Apply filters
        filtered_data = self._apply_filters(window_data)
        
        # Calculate envelope (RMS)
        rms_value = self._calculate_rms(filtered_data)
        
        # Update baseline and threshold
        self._update_baseline(rms_value)
        self._update_threshold()
        
        # Detect gesture
        self._detect_gesture(rms_value)
    
    def _apply_filters(self, signal: np.ndarray, noise_reduction_level: int = 3) -> np.ndarray:
        """Apply adaptive filtering based on noise reduction level."""
        try:
            # Basic filtering (always applied)
            # Step 1: High-pass filter (remove DC and low-frequency noise)
            filtered = filtfilt(self.hp_b, self.hp_a, signal)
            
            # Step 2: Notch filter (remove 50 Hz power line interference)
            filtered = filtfilt(self.notch_b, self.notch_a, filtered)
            
            # Step 3: Notch filter (remove 60 Hz power line interference)
            filtered = filtfilt(self.notch60_b, self.notch60_a, filtered)
            
            # Step 4: Low-pass filter (remove high-frequency noise)
            filtered = filtfilt(self.lp_b, self.lp_a, filtered)
            
            # Adaptive filtering based on noise reduction level
            if noise_reduction_level >= 2:
                # Light outlier removal
                outlier_threshold = OUTLIER_THRESHOLD_BASE - (noise_reduction_level * 0.5)
                filtered = self._remove_outliers(filtered, threshold=outlier_threshold)
            
            if noise_reduction_level >= 3:
                # Light median filter
                filtered = self._apply_median_filter(filtered, kernel_size=MEDIAN_FILTER_KERNEL)
            
            if noise_reduction_level >= 4:
                # Light moving average
                window_size = min(MOVING_AVERAGE_WINDOW + 1, noise_reduction_level - 1)
                filtered = self._apply_moving_average(filtered, window_size=window_size)
            
            if noise_reduction_level >= 5:
                # Savitzky-Golay for maximum smoothing
                if len(filtered) >= 11:
                    filtered = self._apply_savitzky_golay(filtered, window_length=11, polyorder=3)
            
            return filtered
        except Exception as e:
            print(f"Filter error: {e}")
            return signal  # Return original signal if filtering fails
    
    def _detect_gesture(self, rms_value: float):
        """Detect fist close/open gestures based on RMS threshold."""
        current_time = time.time()
        
        # Check for gesture start (fist close)
        if not self.gesture_active and rms_value > self.adaptive_threshold:
            # Check cooldown period
            if current_time - self.last_gesture_time > self.gesture_cooldown:
                self.gesture_active = True
                self.gesture_start_time = current_time
                print(f"Fist close detected - RMS: {rms_value:.2f}, Threshold: {self.adaptive_threshold:.2f}")
        
        # Check for gesture end (fist open)
        elif self.gesture_active and rms_value < self.adaptive_threshold:
            gesture_duration = current_time - self.gesture_start_time
            
            # Validate gesture duration
            if self.min_gesture_duration <= gesture_duration <= self.max_gesture_duration:
                self._complete_gesture()
            else:
                print(f"Invalid gesture duration: {gesture_duration:.3f}s")
                self.false_positives += 1
            
            self.gesture_active = False
        
        # Check for maximum gesture duration
        elif self.gesture_active and current_time - self.gesture_start_time > self.max_gesture_duration:
            print("Gesture timeout - maximum duration exceeded")
            self.gesture_active = False
            self.false_positives += 1
    
    def _complete_gesture(self):
        """Complete a detected gesture and trigger callback."""
        self.total_gestures += 1
        self.last_gesture_time = time.time()
        
        print(f"✅ Gesture completed! Total gestures: {self.total_gestures}")
        
        # Call the gesture callback if provided
        if self.gesture_callback:
            try:
                self.gesture_callback()
            except Exception as e:
                print(f"Error in gesture callback: {e}")
    
    def get_statistics(self) -> dict:
        """Get detection statistics."""
        return {
            'total_gestures': self.total_gestures,
            'false_positives': self.false_positives,
            'baseline_rms': self.baseline_rms,
            'adaptive_threshold': self.adaptive_threshold,
            'gesture_active': self.gesture_active
        }
    
    def reset_statistics(self):
        """Reset detection statistics."""
        self.total_gestures = 0
        self.false_positives = 0
        self.baseline_rms = 0.0
        self.adaptive_threshold = 0.0
    
    def set_threshold_multiplier(self, multiplier: float):
        """Set the threshold multiplier for gesture detection."""
        self.threshold_multiplier = multiplier
        self._update_threshold()
    
    def start_detection(self):
        """Start the gesture detection thread."""
        if not self.running:
            self.running = True
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            print("EMG gesture detection started")
    
    def stop_detection(self):
        """Stop the gesture detection thread."""
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
        print("EMG gesture detection stopped")
    
    def _detection_loop(self):
        """Main detection loop (runs in separate thread)."""
        while self.running:
            time.sleep(0.001)  # 1ms sleep to prevent busy waiting


class GrabReleaseController:
    """
    State machine for controlling grab/release operations based on EMG gestures.
    
    Logic:
    - First fist close/open cycle → GRAB operation
    - Second fist close/open cycle → RELEASE operation
    - Pattern repeats: Grab → Release → Grab → Release...
    """
    
    def __init__(self, command_callback: Optional[Callable] = None):
        """
        Initialize the grab/release controller.
        
        Args:
            command_callback: Callback function called with commands ('grab' or 'release')
        """
        self.state = "idle"  # idle, grab, release
        self.fist_cycle_count = 0
        self.command_callback = command_callback
        self.last_command_time = 0.0
        self.command_cooldown = DEFAULT_COMMAND_COOLDOWN
        
    def process_gesture(self):
        """
        Process a detected fist close/open cycle.
        Alternates between grab and release commands.
        """
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_command_time < self.command_cooldown:
            print(f"Command cooldown active: {self.command_cooldown - (current_time - self.last_command_time):.1f}s remaining")
            return
        
        self.fist_cycle_count += 1
        
        if self.fist_cycle_count % 2 == 1:
            # Odd count: GRAB operation
            self.state = "grab"
            self._send_command("grab")
        else:
            # Even count: RELEASE operation  
            self.state = "release"
            self._send_command("release")
    
    def _send_command(self, command: str):
        """Send a command to the robotic arm."""
        self.last_command_time = time.time()
        print(f"🤖 Robotic Arm Command: {command.upper()}")
        
        if self.command_callback:
            try:
                self.command_callback(command)
            except Exception as e:
                print(f"Error in command callback: {e}")
    
    def get_state(self) -> dict:
        """Get current controller state."""
        return {
            'state': self.state,
            'fist_cycle_count': self.fist_cycle_count,
            'next_action': 'grab' if (self.fist_cycle_count + 1) % 2 == 1 else 'release'
        }
    
    def reset(self):
        """Reset the controller state."""
        self.state = "idle"
        self.fist_cycle_count = 0
        self.last_command_time = 0.0


def test_gesture_detector():
    """Test function for the gesture detector."""
    print("Testing EMG Gesture Detector...")
    
    # Create controller
    controller = GrabReleaseController()
    
    # Create detector with callback
    detector = EMGGestureDetector(
        sampling_rate=1000,
        gesture_callback=controller.process_gesture
    )
    
    # Simulate EMG data
    print("Simulating EMG data...")
    for i in range(1000):
        # Simulate fist close/open cycles
        if 100 <= i <= 200 or 400 <= i <= 500 or 700 <= i <= 800:
            # Fist close: high amplitude
            sample = np.random.normal(500, 100)
        else:
            # Fist open: low amplitude
            sample = np.random.normal(50, 20)
        
        detector.add_sample(sample)
        time.sleep(0.001)  # 1ms delay
    
    # Print statistics
    stats = detector.get_statistics()
    print(f"\nDetection Statistics:")
    print(f"Total gestures: {stats['total_gestures']}")
    print(f"False positives: {stats['false_positives']}")
    print(f"Baseline RMS: {stats['baseline_rms']:.2f}")
    print(f"Adaptive threshold: {stats['adaptive_threshold']:.2f}")
    
    controller_state = controller.get_state()
    print(f"\nController State:")
    print(f"Current state: {controller_state['state']}")
    print(f"Fist cycles: {controller_state['fist_cycle_count']}")
    print(f"Next action: {controller_state['next_action']}")


if __name__ == "__main__":
    test_gesture_detector()
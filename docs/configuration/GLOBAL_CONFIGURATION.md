# EMG Robotic Arm Control - Global Configuration Variables

## 🔧 Global Configuration System

I've added comprehensive global configuration variables at the top of both main files to easily control various functionalities without modifying code throughout the application.

## 📁 **Files with Global Variables:**

### 1. `emg_robotic_arm.py` - Main Application
### 2. `emg_gesture_detector.py` - Gesture Detection Module

## ⚙️ **Configuration Categories**

### **Signal Processing Configuration**
```python
ENABLE_ADVANCED_FILTERING = True          # Enable/disable advanced filtering
DEFAULT_NOISE_REDUCTION_LEVEL = 2         # Default noise reduction (1-5)
DEFAULT_THRESHOLD_MULTIPLIER = 1          # Default threshold sensitivity (1-10)
DEFAULT_MIN_GESTURE_DURATION = 50         # Minimum gesture duration in ms
DEFAULT_MAX_GESTURE_DURATION = 2000       # Maximum gesture duration in ms
```

### **Visualization Configuration**
```python
VISUALIZATION_UPDATE_RATE = 50            # Visualization update rate in ms (20 FPS)
ENABLE_VISUALIZATION_SMOOTHING = True     # Enable smoothing for visualization
VISUALIZATION_SMOOTHING_WINDOW = 3        # Window size for visualization smoothing
```

### **Gesture Detection Configuration**
```python
ENABLE_AUTO_VISUALIZATION = True          # Auto-start visualization on EMG connect
ENABLE_CONFIRMATION_DIALOGS = True        # Enable confirmation dialogs for disconnect
GESTURE_COOLDOWN_TIME = 0.5               # Cooldown between gestures in seconds
COMMAND_COOLDOWN_TIME = 1.0               # Cooldown between commands in seconds
```

### **Robotic Arm Configuration**
```python
DEFAULT_MOCK_MODE = True                  # Default to mock mode (no hardware)
EMERGENCY_STOP_DELAY = 0.5                # Delay for emergency stop processing
```

### **UI Configuration**
```python
ENABLE_DEBUG_LOGGING = True               # Enable detailed debug logging
LOG_MAX_LINES = 100                       # Maximum lines in log display
STATS_UPDATE_INTERVAL = 1000              # Statistics update interval in ms
```

### **Signal Processing Thresholds**
```python
OUTLIER_THRESHOLD_BASE = 4.0              # Base outlier threshold
MEDIAN_FILTER_KERNEL = 3                  # Median filter kernel size
MOVING_AVERAGE_WINDOW = 2                 # Moving average window size
```

### **Filter Frequencies**
```python
HIGH_PASS_FREQUENCY = 20.0                # High-pass filter frequency (Hz)
LOW_PASS_FREQUENCY = 250.0                # Low-pass filter frequency (Hz)
NOTCH_50_FREQUENCY = [49.0, 51.0]         # 50 Hz notch filter range
NOTCH_60_FREQUENCY = [59.0, 61.0]         # 60 Hz notch filter range
```

## 🎯 **How to Use Global Variables**

### **Quick Sensitivity Adjustment:**
```python
# Make system more sensitive
DEFAULT_THRESHOLD_MULTIPLIER = 1          # Lower = more sensitive
DEFAULT_MIN_GESTURE_DURATION = 50         # Shorter = more sensitive
DEFAULT_NOISE_REDUCTION_LEVEL = 2         # Lower = less filtering

# Make system less sensitive
DEFAULT_THRESHOLD_MULTIPLIER = 3          # Higher = less sensitive
DEFAULT_MIN_GESTURE_DURATION = 200        # Longer = less sensitive
DEFAULT_NOISE_REDUCTION_LEVEL = 4         # Higher = more filtering
```

### **Performance Tuning:**
```python
# Faster visualization
VISUALIZATION_UPDATE_RATE = 30            # 33 FPS

# Slower but smoother
VISUALIZATION_UPDATE_RATE = 100           # 10 FPS

# More responsive
STATS_UPDATE_INTERVAL = 500               # Update every 500ms

# Less frequent updates
STATS_UPDATE_INTERVAL = 2000              # Update every 2 seconds
```

### **Debugging Control:**
```python
# Enable detailed logging
ENABLE_DEBUG_LOGGING = True

# Disable confirmation dialogs for testing
ENABLE_CONFIRMATION_DIALOGS = False

# Increase log capacity
LOG_MAX_LINES = 200
```

### **Hardware Configuration:**
```python
# Use real hardware
DEFAULT_MOCK_MODE = False

# Use mock mode for testing
DEFAULT_MOCK_MODE = True
```

## 🔧 **Common Adjustments**

### **For Noisy Environment:**
```python
DEFAULT_NOISE_REDUCTION_LEVEL = 4         # Higher noise reduction
ENABLE_ADVANCED_FILTERING = True          # Enable all filtering
DEFAULT_THRESHOLD_MULTIPLIER = 2          # Higher threshold
```

### **For Clean Environment:**
```python
DEFAULT_NOISE_REDUCTION_LEVEL = 1         # Minimal noise reduction
ENABLE_ADVANCED_FILTERING = False         # Disable heavy filtering
DEFAULT_THRESHOLD_MULTIPLIER = 1          # Lower threshold
```

### **For Fast Response:**
```python
DEFAULT_MIN_GESTURE_DURATION = 30         # Very short minimum
GESTURE_COOLDOWN_TIME = 0.2               # Shorter cooldown
COMMAND_COOLDOWN_TIME = 0.5               # Shorter command cooldown
```

### **For Stable Response:**
```python
DEFAULT_MIN_GESTURE_DURATION = 150        # Longer minimum
GESTURE_COOLDOWN_TIME = 1.0               # Longer cooldown
COMMAND_COOLDOWN_TIME = 2.0               # Longer command cooldown
```

## 🎮 **UI Integration**

The global variables automatically set the default values for UI controls:

- **Threshold Multiplier**: Uses `DEFAULT_THRESHOLD_MULTIPLIER`
- **Min Duration**: Uses `DEFAULT_MIN_GESTURE_DURATION`
- **Max Duration**: Uses `DEFAULT_MAX_GESTURE_DURATION`
- **Mock Mode**: Uses `DEFAULT_MOCK_MODE`
- **Advanced Filtering**: Uses `ENABLE_ADVANCED_FILTERING`
- **Noise Reduction**: Uses `DEFAULT_NOISE_REDUCTION_LEVEL`

## 🚀 **Benefits**

### **1. Easy Configuration**
- **Single location** for all settings
- **No code searching** required
- **Clear documentation** for each variable

### **2. Quick Testing**
- **Change one variable** to test different behaviors
- **No code compilation** required
- **Immediate effect** on next run

### **3. Environment Adaptation**
- **Easy adjustment** for different environments
- **Preset configurations** for common scenarios
- **User-specific tuning** without code changes

### **4. Development Efficiency**
- **Centralized control** of all parameters
- **Easy A/B testing** of different settings
- **Quick debugging** with configurable logging

## 📝 **Usage Examples**

### **Example 1: Make System More Sensitive**
```python
# At the top of emg_robotic_arm.py
DEFAULT_THRESHOLD_MULTIPLIER = 1          # More sensitive
DEFAULT_MIN_GESTURE_DURATION = 30         # Shorter gestures
DEFAULT_NOISE_REDUCTION_LEVEL = 1         # Less filtering
```

### **Example 2: Optimize for Noisy Environment**
```python
# At the top of emg_robotic_arm.py
DEFAULT_NOISE_REDUCTION_LEVEL = 4         # Heavy filtering
DEFAULT_THRESHOLD_MULTIPLIER = 2          # Higher threshold
ENABLE_ADVANCED_FILTERING = True          # All filters enabled
```

### **Example 3: Disable Confirmation Dialogs**
```python
# At the top of emg_robotic_arm.py
ENABLE_CONFIRMATION_DIALOGS = False       # No confirmation dialogs
ENABLE_DEBUG_LOGGING = True               # Keep debug logging
```

## 🎉 **Result**

The global configuration system provides **complete control** over the application behavior through simple variable changes at the top of the files. This makes it easy to:

- ✅ **Tune sensitivity** for different users
- ✅ **Adapt to environments** (noisy vs clean)
- ✅ **Test different configurations** quickly
- ✅ **Debug issues** with configurable logging
- ✅ **Optimize performance** for different use cases

**Perfect configuration system for easy customization!** ✨⚙️
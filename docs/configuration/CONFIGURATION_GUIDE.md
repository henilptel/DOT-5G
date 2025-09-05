# EMG Robotic Arm Control - Complete Configuration Guide

**Document ID:** CONFIG-001  
**Created:** September 5, 2024  
**Last Updated:** September 5, 2024  
**Version:** 1.0.0  
**Status:** ✅ Complete  
**Category:** Configuration & Customization  

---

## 📋 **Document Information**

| **Field** | **Value** |
|-----------|-----------|
| **Project Name** | EMG-Controlled Robotic Arm |
| **Document Type** | Configuration Instructions & Reference |
| **Target Audience** | Users, Developers, System Administrators |
| **Related Documents** | GLOBAL_CONFIGURATION.md, SYSTEM_READY.md |
| **Prerequisites** | Basic text editing knowledge |

---

## 📖 How to Change Configuration Values

This guide explains how to modify the global configuration variables to customize the EMG robotic arm control system behavior.

## 📁 **Where to Find Configuration Variables**

### **Main Application File:**
```
/mnt/d/_Hackathons/5G_Hackathon/MAIN/Chords-Python/chordspy/emg_robotic_arm.py
```
**Lines 7-47** contain all the global configuration variables.

### **Gesture Detection File:**
```
/mnt/d/_Hackathons/5G_Hackathon/MAIN/Chords-Python/chordspy/emg_gesture_detector.py
```
**Lines 7-25** contain gesture detection specific variables.

## 🔧 **How to Change Values**

### **Step 1: Open the File**
1. Navigate to the file location
2. Open `emg_robotic_arm.py` in any text editor
3. Scroll to the top (lines 7-47)

### **Step 2: Locate the Variable**
Find the variable you want to change in the configuration section.

### **Step 3: Modify the Value**
Change the value after the `=` sign:
```python
# Before
DEFAULT_THRESHOLD_MULTIPLIER = 1

# After (example)
DEFAULT_THRESHOLD_MULTIPLIER = 2
```

### **Step 4: Save and Restart**
1. Save the file
2. Restart the application
3. The new values will take effect

---

## ⚙️ **Complete Configuration Reference**

## 🎯 **Signal Processing Configuration**

### **`ENABLE_ADVANCED_FILTERING`**
- **Type:** Boolean (True/False)
- **Default:** `True`
- **What it does:** Enables/disables the advanced multi-stage filtering pipeline
- **When to change:**
  - `True`: Use when you have noisy EMG signals
  - `False`: Use when you have very clean signals and want maximum sensitivity

### **`DEFAULT_NOISE_REDUCTION_LEVEL`**
- **Type:** Integer (1-5)
- **Default:** `2`
- **What it does:** Controls the intensity of noise reduction filtering
- **Values:**
  - `1`: Minimal filtering - maximum sensitivity, some noise
  - `2`: Light filtering - balanced sensitivity and noise reduction
  - `3`: Moderate filtering - good balance
  - `4`: Heavy filtering - less sensitive, very clean signals
  - `5`: Maximum filtering - least sensitive, extremely clean signals

### **`DEFAULT_THRESHOLD_MULTIPLIER`**
- **Type:** Integer (1-10)
- **Default:** `1`
- **What it does:** Controls how sensitive the gesture detection is
- **Values:**
  - `1`: Very sensitive - detects small muscle movements
  - `2`: Sensitive - detects moderate muscle movements
  - `3`: Normal - detects strong muscle movements
  - `4-5`: Less sensitive - requires strong muscle contractions
  - `6-10`: Very insensitive - requires very strong muscle contractions

### **`DEFAULT_MIN_GESTURE_DURATION`**
- **Type:** Integer (milliseconds)
- **Default:** `50`
- **What it does:** Minimum time a gesture must last to be detected
- **Values:**
  - `30-50`: Very fast detection - quick gestures
  - `50-100`: Fast detection - normal gestures
  - `100-200`: Normal detection - deliberate gestures
  - `200-500`: Slow detection - very deliberate gestures

### **`DEFAULT_MAX_GESTURE_DURATION`**
- **Type:** Integer (milliseconds)
- **Default:** `2000`
- **What it does:** Maximum time a gesture can last before being rejected
- **Values:**
  - `1000`: Short maximum - quick gestures only
  - `2000`: Normal maximum - standard gestures
  - `3000-5000`: Long maximum - extended gestures

---

## 📊 **Visualization Configuration**

### **`VISUALIZATION_UPDATE_RATE`**
- **Type:** Integer (milliseconds)
- **Default:** `50`
- **What it does:** How often the visualization updates (frame rate)
- **Values:**
  - `30`: 33 FPS - very smooth but uses more CPU
  - `50`: 20 FPS - balanced smoothness and performance
  - `100`: 10 FPS - less smooth but uses less CPU
  - `200`: 5 FPS - choppy but very low CPU usage

### **`ENABLE_VISUALIZATION_SMOOTHING`**
- **Type:** Boolean (True/False)
- **Default:** `True`
- **What it does:** Applies smoothing to the visualization plots
- **When to change:**
  - `True`: Smoother looking plots, easier to see patterns
  - `False`: Raw signal display, shows actual noise

### **`VISUALIZATION_SMOOTHING_WINDOW`**
- **Type:** Integer (3-10)
- **Default:** `3`
- **What it does:** Size of smoothing window for visualization
- **Values:**
  - `3`: Light smoothing - preserves signal details
  - `5`: Moderate smoothing - good balance
  - `7-10`: Heavy smoothing - very smooth but may hide details

---

## 🎮 **Gesture Detection Configuration**

### **`ENABLE_AUTO_VISUALIZATION`**
- **Type:** Boolean (True/False)
- **Default:** `True`
- **What it does:** Automatically starts visualization when EMG connects
- **When to change:**
  - `True`: Visualization starts automatically (recommended)
  - `False`: Manual control of visualization

### **`ENABLE_CONFIRMATION_DIALOGS`**
- **Type:** Boolean (True/False)
- **Default:** `True`
- **What it does:** Shows confirmation dialogs before disconnecting
- **When to change:**
  - `True`: Safe operation with confirmations
  - `False`: Quick disconnection without confirmations

### **`GESTURE_COOLDOWN_TIME`**
- **Type:** Float (seconds)
- **Default:** `0.5`
- **What it does:** Minimum time between detected gestures
- **Values:**
  - `0.2`: Very fast - allows rapid gestures
  - `0.5`: Normal - prevents accidental double detection
  - `1.0`: Slow - requires deliberate timing
  - `2.0`: Very slow - very deliberate gestures only

### **`COMMAND_COOLDOWN_TIME`**
- **Type:** Float (seconds)
- **Default:** `1.0`
- **What it does:** Minimum time between robotic arm commands
- **Values:**
  - `0.5`: Fast commands - quick robotic arm response
  - `1.0`: Normal commands - standard response time
  - `2.0`: Slow commands - deliberate robotic arm control
  - `5.0`: Very slow commands - very deliberate control

---

## 🤖 **Robotic Arm Configuration**

### **`DEFAULT_MOCK_MODE`**
- **Type:** Boolean (True/False)
- **Default:** `True`
- **What it does:** Controls whether to use real hardware or simulation
- **When to change:**
  - `True`: Simulation mode - no real robotic arm needed
  - `False`: Real hardware mode - requires actual robotic arm

### **`EMERGENCY_STOP_DELAY`**
- **Type:** Float (seconds)
- **Default:** `0.5`
- **What it does:** Delay for emergency stop processing
- **Values:**
  - `0.1`: Very fast emergency stop
  - `0.5`: Normal emergency stop
  - `1.0`: Slower emergency stop (more processing time)

---

## 🖥️ **UI Configuration**

### **`ENABLE_DEBUG_LOGGING`**
- **Type:** Boolean (True/False)
- **Default:** `True`
- **What it does:** Controls detailed logging messages
- **When to change:**
  - `True`: Detailed logs for debugging and monitoring
  - `False`: Minimal logs for cleaner interface

### **`LOG_MAX_LINES`**
- **Type:** Integer
- **Default:** `100`
- **What it does:** Maximum number of lines in the log display
- **Values:**
  - `50`: Short log history
  - `100`: Normal log history
  - `200`: Long log history
  - `500`: Very long log history

### **`STATS_UPDATE_INTERVAL`**
- **Type:** Integer (milliseconds)
- **Default:** `1000`
- **What it does:** How often statistics are updated in the UI
- **Values:**
  - `500`: Updates every 0.5 seconds - very responsive
  - `1000`: Updates every 1 second - normal
  - `2000`: Updates every 2 seconds - less frequent
  - `5000`: Updates every 5 seconds - minimal updates

---

## 🔧 **Signal Processing Thresholds**

### **`OUTLIER_THRESHOLD_BASE`**
- **Type:** Float
- **Default:** `4.0`
- **What it does:** Base threshold for outlier removal
- **Values:**
  - `2.0`: Aggressive outlier removal - removes more noise
  - `4.0`: Normal outlier removal - balanced
  - `6.0`: Conservative outlier removal - preserves more signal

### **`MEDIAN_FILTER_KERNEL`**
- **Type:** Integer (odd numbers only)
- **Default:** `3`
- **What it does:** Size of median filter for spike removal
- **Values:**
  - `3`: Light spike removal
  - `5`: Moderate spike removal
  - `7`: Heavy spike removal

### **`MOVING_AVERAGE_WINDOW`**
- **Type:** Integer
- **Default:** `2`
- **What it does:** Window size for moving average smoothing
- **Values:**
  - `2`: Light smoothing
  - `3`: Moderate smoothing
  - `5`: Heavy smoothing

---

## 📡 **Filter Frequencies**

### **`HIGH_PASS_FREQUENCY`**
- **Type:** Float (Hz)
- **Default:** `20.0`
- **What it does:** High-pass filter cutoff frequency
- **Values:**
  - `10.0`: Removes more low-frequency noise
  - `20.0`: Standard EMG filtering
  - `30.0`: Preserves more low-frequency content

### **`LOW_PASS_FREQUENCY`**
- **Type:** Float (Hz)
- **Default:** `250.0`
- **What it does:** Low-pass filter cutoff frequency
- **Values:**
  - `200.0`: Removes more high-frequency noise
  - `250.0`: Standard EMG filtering
  - `300.0`: Preserves more high-frequency content

### **`NOTCH_50_FREQUENCY`**
- **Type:** List [low, high] (Hz)
- **Default:** `[49.0, 51.0]`
- **What it does:** 50 Hz power line interference removal
- **Values:**
  - `[48.0, 52.0]`: Wider notch - removes more interference
  - `[49.0, 51.0]`: Standard notch
  - `[49.5, 50.5]`: Narrower notch - preserves more signal

### **`NOTCH_60_FREQUENCY`**
- **Type:** List [low, high] (Hz)
- **Default:** `[59.0, 61.0]`
- **What it does:** 60 Hz power line interference removal
- **Values:**
  - `[58.0, 62.0]`: Wider notch - removes more interference
  - `[59.0, 61.0]`: Standard notch
  - `[59.5, 60.5]`: Narrower notch - preserves more signal

---

## 🎯 **Common Configuration Scenarios**

## **Scenario 1: Very Sensitive System**
```python
DEFAULT_THRESHOLD_MULTIPLIER = 1
DEFAULT_MIN_GESTURE_DURATION = 30
DEFAULT_NOISE_REDUCTION_LEVEL = 1
ENABLE_ADVANCED_FILTERING = False
GESTURE_COOLDOWN_TIME = 0.2
```
**Result:** Detects very small muscle movements quickly

## **Scenario 2: Noisy Environment**
```python
DEFAULT_NOISE_REDUCTION_LEVEL = 4
ENABLE_ADVANCED_FILTERING = True
DEFAULT_THRESHOLD_MULTIPLIER = 2
OUTLIER_THRESHOLD_BASE = 3.0
MEDIAN_FILTER_KERNEL = 5
```
**Result:** Clean signals in noisy environments

## **Scenario 3: Fast Response System**
```python
DEFAULT_MIN_GESTURE_DURATION = 30
GESTURE_COOLDOWN_TIME = 0.2
COMMAND_COOLDOWN_TIME = 0.5
VISUALIZATION_UPDATE_RATE = 30
STATS_UPDATE_INTERVAL = 500
```
**Result:** Very responsive system with fast updates

## **Scenario 4: Stable, Deliberate Control**
```python
DEFAULT_MIN_GESTURE_DURATION = 200
DEFAULT_THRESHOLD_MULTIPLIER = 3
GESTURE_COOLDOWN_TIME = 1.0
COMMAND_COOLDOWN_TIME = 2.0
```
**Result:** Requires deliberate, strong gestures

## **Scenario 5: Development/Debugging**
```python
ENABLE_DEBUG_LOGGING = True
LOG_MAX_LINES = 200
ENABLE_CONFIRMATION_DIALOGS = False
DEFAULT_MOCK_MODE = True
```
**Result:** Maximum logging and debugging information

## **Scenario 6: Production Use**
```python
ENABLE_DEBUG_LOGGING = False
LOG_MAX_LINES = 50
ENABLE_CONFIRMATION_DIALOGS = True
DEFAULT_MOCK_MODE = False
```
**Result:** Clean interface for end users

---

## 🚀 **Step-by-Step Configuration Process**

### **Step 1: Identify Your Needs**
- What type of environment? (noisy/clean)
- What sensitivity level? (high/medium/low)
- What response speed? (fast/normal/slow)
- What user experience? (debugging/production)

### **Step 2: Choose Base Configuration**
Select one of the scenarios above that matches your needs.

### **Step 3: Fine-tune Parameters**
Adjust specific values based on testing:
- If too sensitive: Increase `DEFAULT_THRESHOLD_MULTIPLIER`
- If too insensitive: Decrease `DEFAULT_THRESHOLD_MULTIPLIER`
- If too much noise: Increase `DEFAULT_NOISE_REDUCTION_LEVEL`
- If too slow: Decrease `DEFAULT_MIN_GESTURE_DURATION`

### **Step 4: Test and Iterate**
1. Save configuration
2. Restart application
3. Test with your EMG signals
4. Adjust as needed
5. Repeat until optimal

---

## ⚠️ **Important Notes**

### **File Locations:**
- Main configuration: `chordspy/emg_robotic_arm.py` (lines 7-47)
- Gesture detection: `chordspy/emg_gesture_detector.py` (lines 7-25)

### **Restart Required:**
- Changes only take effect after restarting the application
- No need to recompile or rebuild

### **Backup Recommended:**
- Save a copy of working configurations
- Document what works for different scenarios

### **Testing:**
- Test with actual EMG signals after changes
- Monitor the log output for feedback
- Use the visualization to see signal quality

---

## 🎉 **Quick Reference Card**

| **Need** | **Variable** | **Value** |
|----------|--------------|-----------|
| More Sensitive | `DEFAULT_THRESHOLD_MULTIPLIER` | `1` |
| Less Sensitive | `DEFAULT_THRESHOLD_MULTIPLIER` | `3` |
| Faster Response | `DEFAULT_MIN_GESTURE_DURATION` | `30` |
| Slower Response | `DEFAULT_MIN_GESTURE_DURATION` | `200` |
| Less Noise | `DEFAULT_NOISE_REDUCTION_LEVEL` | `4` |
| More Noise | `DEFAULT_NOISE_REDUCTION_LEVEL` | `1` |
| Debug Mode | `ENABLE_DEBUG_LOGGING` | `True` |
| Production Mode | `ENABLE_DEBUG_LOGGING` | `False` |
| Real Hardware | `DEFAULT_MOCK_MODE` | `False` |
| Simulation | `DEFAULT_MOCK_MODE` | `True` |

**Perfect configuration control for any scenario!** ✨⚙️
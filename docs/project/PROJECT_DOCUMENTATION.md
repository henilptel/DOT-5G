# EMG-Controlled Robotic Arm Project Documentation

**Document ID:** PROJ-001  
**Created:** September 5, 2024  
**Last Updated:** September 5, 2024  
**Version:** 1.0.0  
**Status:** ✅ Complete  
**Category:** Project Documentation  

---

## 📋 **Document Information**

| **Field** | **Value** |
|-----------|-----------|
| **Project Name** | EMG+EOG Controlled Robotic Arm |
| **Document Type** | Project Requirements & Specifications |
| **Target Audience** | Developers, Researchers, Users |
| **Related Documents** | IMPLEMENTATION_SUMMARY.md, SYSTEM_READY.md |
| **Dependencies** | Arduino UNO R4, BioAmp EXG Pill, SAZ DEKOR Robotic Arm |

---

## 🎯 Project Overview

**Project Name**: EMG+EOG Controlled Robotic Arm  
**Target Device**: SAZ DEKOR® DIY 6-DOF Robot Mechanical Arm Kits  
**Control Method**: EMG (Electromyography) + EOG (Electrooculography) signals  
**Hardware**: UpsideDown Lab's DIY Neuroscience Kit – Pro with Arduino UNO EK R4 Minima (14-bit ADC)  
**Sensor**: BioAmp EXG Pill  

## 🧠 Control Logic

### EMG Control Strategy
- **Primary Function**: Control grab/release operations of the robotic arm
- **Gesture Recognition**: Fist closing and opening movements
- **Control Mapping**:
  - **First fist close/open cycle** → **GRAB operation**
  - **Second fist close/open cycle** → **RELEASE operation**
  - **Pattern repeats**: Grab → Release → Grab → Release...

### Future EOG Integration
- EOG signals will be added after EMG is fully functional
- EOG will control directional movements (up, down, left, right)
- Current focus: EMG implementation only

## 🔧 Hardware Specifications

### Arduino Setup
- **Board**: Arduino UNO EK R4 Minima
- **ADC Resolution**: 14-bit (16,384 levels)
- **Sampling Rate**: 1000 Hz (as configured in current code)

### BioAmp EXG Pill
- **Purpose**: EMG signal acquisition
- **Output**: Analog signals to Arduino ADC
- **Data Format**: CSV files with Channel1 data

### Robotic Arm
- **Model**: SAZ DEKOR® DIY 6-DOF Robot Mechanical Arm Kits
- **Status**: Not yet acquired
- **Integration**: System must be ready for easy integration when hardware arrives


## 🎯 Implementation Requirements

### Current Status
- ✅ EMG data acquisition and analysis pipeline (chordspy)
- ❌ Machine learning model training
- ✅ Comprehensive visualization tools
- ❌ Real-time gesture detection
- ❌ Robotic arm integration
- ❌ Grab/release control logic

### Immediate Development Needs

#### 1. Real-Time Gesture Detection
- **Requirement**: Detect fist close/open cycles in real-time
- **Implementation**: 
  - Stream EMG data from Arduino
  - Apply trained model for gesture classification
  - Implement state machine for grab/release logic
  - Handle timing and thresholding for reliable detection

#### 2. Grab/Release State Machine
```python
# Pseudo-code for state machine
class GrabReleaseController:
    def __init__(self):
        self.state = "idle"  # idle, grab, release
        self.fist_cycle_count = 0
    
    def process_gesture(self, gesture):
        if gesture == "fist_close_open":
            self.fist_cycle_count += 1
            if self.fist_cycle_count % 2 == 1:
                self.state = "grab"
                self.send_grab_command()
            else:
                self.state = "release"
                self.send_release_command()
```

#### 3. Arduino Communication
- **Protocol**: Serial communication with Arduino
- **Data Format**: Real-time EMG samples
- **Sampling**: Continuous streaming at 1000 Hz
- **Processing**: Real-time feature extraction and classification

#### 4. Robotic Arm Integration (Future)
- **Interface**: Serial/USB communication with robotic arm controller
- **Commands**: Grab/Release control signals
- **Status**: Ready for integration when hardware arrives

## 🔄 Development Workflow

### Phase 1: EMG Analysis (Current)
1. Data acquisition from BioAmp EXG Pill
2. Signal preprocessing and feature extraction
3. Machine learning model training
4. Visualization and analysis tools

### Phase 2: Real-Time Implementation (Next)
1. Real-time data streaming from Arduino
2. Live gesture detection and classification
3. Grab/release state machine implementation
4. Arduino communication protocol

### Phase 3: Robotic Arm Integration (Future)
1. Robotic arm communication interface
2. Command mapping and control logic
3. System integration and testing
4. EOG signal integration for directional control

## 🎛️ Technical Specifications

### Signal Processing
- **Sampling Rate**: 1000 Hz
- **Window Size**: 200 samples (200ms)
- **Overlap**: 50% (100 samples)
- **Feature Extraction**: 20 comprehensive features
- **Classification**: 3-class (movement, rest, transition)

### Performance Metrics
- **Model Accuracy**: Varies by algorithm (see training results)
- **Real-time Requirements**: <100ms latency for gesture detection
- **Reliability**: Robust detection of fist close/open cycles

## 🚀 Next Steps for Implementation

1. **Real-time Data Streaming**
   - Implement Arduino serial communication
   - Create continuous data acquisition loop
   - Handle data buffering and processing

2. **Live Gesture Detection**
   - Adapt trained model for real-time classification
   - Implement sliding window feature extraction
   - Add gesture validation and filtering

3. **Grab/Release Controller**
   - Implement state machine for grab/release logic
   - Add timing controls and debouncing
   - Create command interface for robotic arm

4. **System Integration**
   - Prepare communication protocols
   - Design modular architecture for easy hardware integration
   - Implement error handling and safety features

## 📝 Notes for Future Development

- **Hardware Independence**: System designed to be hardware-agnostic until robotic arm arrives 
- **Documentation**: Comprehensive analysis reports generated for debugging and optimization

---
# 🔋 Battery Health Report System

A battery diagnostic system that analyzes EV battery data and generates detailed health reports with anomaly detection.

## 🚀 Features

- **Battery State of Health (SoH)** calculation
- **Charge/Discharge cycle counting**
- **Anomaly detection**:
  - Voltage imbalance between cells
  - Cell overheating detection
  - Capacity fade analysis
  - SoC drift detection
- **Interactive web UI** with Streamlit

## 📋 Requirements

- Python 3.8+
- Streamlit

## 🛠️ Installation

1. Clone or download the project
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

1. **Run the Streamlit app**:
```bash
streamlit run main.py
```

2. **Open your browser** to `http://localhost:8501`

3. **Load sample data** or upload JSON file

## 🔍 Anomaly Detection Thresholds

The system uses realistic thresholds based on industry standards:

- **Voltage Imbalance**: > 0.1V difference between cells
- **Overheating**: > 60°C (warning), > 80°C (critical)
- **Capacity Fade**: > 20% capacity loss
- **SoC Drift**: > 100% SoC change in single event

## 🎯 Key Calculations

### State of Health (SoH)
```
SoH = (Current Usable Capacity / Original Rated Capacity) × 100%
```

### Charge/Discharge Cycles
```
Full_Cycles = Σ(|SoC_End - SoC_Start|) / 100
```

### Voltage Imbalance
```
Voltage_Spread = Max_Cell_Voltage - Min_Cell_Voltage
```

## 🚨 Maintenance Recommendations

The system provides actionable recommendations based on detected issues:

- **SoH < 70%**: Battery replacement recommended
- **SoH < 80%**: Monitor battery closely
- **Overheating**: Check cooling system
- **Voltage Imbalance**: Cell balancing required
- **Capacity Fade**: Consider battery replacement
- **SoC Drift**: SoC calibration needed

## 📝 License

This project is open source and available under the MIT License.


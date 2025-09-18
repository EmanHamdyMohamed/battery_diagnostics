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
- **Download Report PDF**
- **Interactive web UI** with Streamlit

## 📋 Requirements

- Python 3.8+
- Streamlit
- pydantic
- fpdf

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

## 📝 License

This project is open source and available under the MIT License.


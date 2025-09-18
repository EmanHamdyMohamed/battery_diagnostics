import json
import streamlit as st

from analyzer.battery_analyzer import BatteryAnalyzer

# Page configuration
st.set_page_config(
    page_title="🔋 Battery Health Report",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)


def display_battery_health_metrics(report):
    """Display key battery health metrics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        soh = report['battery_health']['state_of_health_percent']
        st.metric(
            label="State of Health",
            value=f"{soh}%",
        )
        
    with col2:
        charge_cycles_count = report['battery_health']['charge_cycles']
        st.metric(
            label="Charge Cycles Count",
            value=charge_cycles_count,
            delta=None
        )
    
    with col3:
        discharge_cycles_count = report['battery_health']['discharge_cycles']
        st.metric(
            label="Discharge Cycles Count",
            value=discharge_cycles_count,
            delta=None
        )


def display_anomalies(report):
    """Display detected anomalies with appropriate styling"""
    
    st.subheader("🔍 Anomaly Detection")
    
    # Individual anomaly details
    for anomaly_type, anomaly_data in report['anomalies'].items():
        st.write(f"**{anomaly_type.replace('_', ' ').title()}**: {anomaly_data['message']}")
        
        # Show additional details for specific anomalies
        if anomaly_type == "voltage_imbalance" and anomaly_data['anomaly']:
            st.write(f"  - Voltage spread: {anomaly_data['voltage_spread']}V")
            st.write(f"  - Min voltage: {anomaly_data['min_voltage']}V")
            st.write(f"  - Max voltage: {anomaly_data['max_voltage']}V")
        
        elif anomaly_type == "overheating" and anomaly_data['anomaly']:
            st.write(f"  - Max temperature: {anomaly_data['max_temperature']}°C")
            st.write(f"  - Hot cells: {anomaly_data['hot_cells_count']}")
            if anomaly_data['critical_cells_count'] > 0:
                st.write(f"  - Critical cells: {anomaly_data['critical_cells_count']}")
        
        elif anomaly_type == "capacity_fade" and anomaly_data['anomaly']:
            st.write(f"  - Capacity loss: {anomaly_data['capacity_loss_percent']}%")
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">🔋 Battery Health Report</h1>', unsafe_allow_html=True)
    st.markdown("Upload a battery diagnostic JSON file to generate a comprehensive health report.")
    
    # File upload
    st.header("📤 Upload Battery Data")
    uploaded_file = st.file_uploader(
        "Choose a JSON file",
        type=["json"],
        help="Upload a battery diagnostic JSON file"
    )
    
    # Load data
    battery_data = None
    if uploaded_file:
        try:
            battery_data = json.load(uploaded_file)
            st.success("✅ File uploaded successfully!")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file. Please upload a valid JSON file.")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    # Generate report if data is available
    if battery_data:
        try:
            # Initialize analyzer
            analyzer = BatteryAnalyzer()
            
            # Generate report
            with st.spinner("🔍 Analyzing battery data..."):
                report = analyzer.generate_battery_report(battery_data)
            
            if 'error' in report:
                st.error(f"❌ {report['error']}")
                return
            
            # Display report
            st.header("📊 Battery Health Report")
            
            # Vehicle info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Vehicle ID:** {report['vehicle_id']}")
            with col2:
                st.write(f"**Report Generated:** {report['timestamp']}")
            
            display_battery_health_metrics(report)

            display_anomalies(report)

        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            st.exception(e)
    
    else:
        # Show instructions when no data is loaded
        st.info("👆 Please upload a JSON file or select sample data to get started.")


if __name__ == "__main__":
    main()

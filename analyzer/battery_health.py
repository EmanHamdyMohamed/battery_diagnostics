
from models.battery_health_report import BatteryHealthData


class BatteryHealth:

    @staticmethod
    def calculate_state_of_health(
        original_capacity: float, current_capacity: float
    ) -> float:
        """
        Calculate State of Health (SoH) as percentage
        SoH = (Current Usable Capacity / Original Rated Capacity) × 100%
        """
        if original_capacity <= 0:
            raise ValueError("Original capacity must be positive")
        soh = (current_capacity / original_capacity) * 100
        return round(soh, 2)

    @staticmethod
    def count_charge_cycles(battery_usage_log: list[dict]) -> int:
        """
        Count full charge cycles from usage log
        Full_Cycles = Σ(|SoC_End - SoC_Start|) / 100
        """
        charge_accumulated = 0
        charge_cycles = 0
        for log in battery_usage_log:
            if log['event'] == 'charge':
                charge_accumulated += abs(log['soc_end'] - log['soc_start'])
                while charge_accumulated >= 100:
                    charge_cycles += 1
                    charge_accumulated -= 100
        return charge_cycles

    @staticmethod
    def count_discharge_cycles(battery_usage_log: list[dict]) -> int:
        """
        Count full discharge cycles from usage log
        Full_Cycles = Σ(|SoC_Start - SoC_End|) / 100
        """
        discharge_accumulated = 0
        discharge_cycles = 0
        for log in battery_usage_log:
            if log['event'] == 'discharge':
                discharge_accumulated += abs(log['soc_start'] - log['soc_end'])
                while discharge_accumulated >= 100:
                    discharge_cycles += 1
                    discharge_accumulated -= 100
        return discharge_cycles

    def generate_battery_health(
        self, battery_data: dict
    ) -> BatteryHealthData:
        battery_pack = battery_data.get('battery_pack', {})
        usage_log = battery_data.get('battery_usage_log', [])
        
        soh = self.calculate_state_of_health(
            battery_pack.get('baseline_capacity_kWh', 0),
            battery_pack.get('current_capacity_kWh', 0)
        )
        
        charge_cycles = self.count_charge_cycles(usage_log)
        discharge_cycles = self.count_discharge_cycles(usage_log)
        
        battery_health = BatteryHealthData(
            state_of_health_percent=soh,
            charge_cycles=charge_cycles,
            discharge_cycles=discharge_cycles,
        )
        return battery_health

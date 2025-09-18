from pydantic import BaseModel, Field
from typing import TypeVar


class BatteryHealthData(BaseModel):
    state_of_health_percent: float = Field(description="State of health as percentage")
    charge_cycles: int = Field(description="Number of charge cycles")
    discharge_cycles: int = Field(description="Number of discharge cycles")


class VoltageImbalance(BaseModel):
    anomaly: bool = Field(description="Whether voltage imbalance is detected")
    voltage_spread: float = Field(description="Voltage spread between min and max cells")
    min_voltage: float = Field(description="Minimum cell voltage")
    max_voltage: float = Field(description="Maximum cell voltage")
    message: str = Field(description="Human-readable message about voltage status")


class Overheating(BaseModel):
    anomaly: bool = Field(description="Whether overheating is detected")
    max_temperature: float = Field(description="Maximum cell temperature")
    hot_cells_count: int = Field(description="Number of cells above overheating threshold")
    critical_cells_count: int = Field(description="Number of cells above critical threshold")
    message: str = Field(description="Human-readable message about temperature status")


class CapacityFade(BaseModel):
    anomaly: bool = Field(description="Whether capacity fade is detected")
    capacity_loss_percent: float = Field(description="Percentage of capacity lost")
    message: str = Field(description="Human-readable message about capacity status")


class SoCDrift(BaseModel):
    anomaly: bool = Field(description="Whether SoC drift is detected")
    unrealistic_changes_count: int = Field(description="Number of unrealistic SoC changes")
    unrealistic_changes: list[dict] = Field(description="Details of unrealistic changes")
    message: str = Field(description="Human-readable message about SoC status")


T = TypeVar(
    "T",
    bound=(
        SoCDrift |
        CapacityFade |
        Overheating |
        VoltageImbalance
    )
)


class BatteryHealthReport(BaseModel):
    vehicle_id: str = Field(description="Vehicle identifier")
    timestamp: str = Field(description="Report generation timestamp")
    battery_health: BatteryHealthData = Field(description="Battery health metrics")
    anomalies: dict[str, T] = Field(description="Anomaly detection results")
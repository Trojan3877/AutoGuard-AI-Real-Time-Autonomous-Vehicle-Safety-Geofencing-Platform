# agents/state.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TelemetryState(BaseModel):
    """
    The immutable telemetry data contract governing the AutoGuard-AI safety lifecycle.
    Enforces rigid validation checks on core streaming coordinates.
    """
    vehicle_id: str
    latitude: float
    longitude: float
    current_speed_mph: float
    active_geofences: List[str] = Field(default_factory=list)
    
    # Safety Agent Telemetry Evaluation Frames
    geofence_breached: bool = False
    collision_risk_detected: bool = False
    recommended_braking_force: float = 0.0  # 0.0 to 1.0 (100% Max Brake)
    override_activated: bool = False
    
    # Observability & System Auditing Trace
    processing_latency_ms: float = 0.0
    execution_sequence: List[str] = Field(default_factory=list)

    def append_trace(self, log_msg: str) -> "TelemetryState":
        """Generates a read-only copy of the telemetry state with appended logs."""
        return self.model_copy(update={"execution_sequence": list(self.execution_sequence) + [log_msg]})

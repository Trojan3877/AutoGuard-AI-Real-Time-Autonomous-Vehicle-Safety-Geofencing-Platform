# agents/supervisor.py
import time
from .state import TelemetryState
from .guards import SafetyCircuitBreaker, TelemetryDeadlineException

class AutoGuardSupervisorEngine:
    """
    The central Safety Supervisor Orchestrator. Directs edge parsing, 
    geofence evaluation, and navigation mitigation sequences.
    """
    def __init__(self):
        self.breaker = SafetyCircuitBreaker(critical_deadline_ms=5.0)

    def audit_telemetry_frame(self, vehicle_id: str, lat: float, lon: float, speed: float) -> TelemetryState:
        state = TelemetryState(vehicle_id=vehicle_id, latitude=lat, longitude=lon, current_speed_mph=speed)
        state = state.append_trace("Ingested raw vehicle telemetry sequence frame.")
        
        start_time = time.time()
        try:
            # 1. Geofence Boundary Verification Step (Worker 1)
            state = self._run_geofence_worker(state)
            
            # 2. Collision Risk Optimization Evaluation Step (Worker 2)
            state = self._run_collision_worker(state)
            
            # Check for timing SLA compliance boundaries
            elapsed_ms = (time.time() - start_time) * 1000
            self.breaker.evaluate_deadline(elapsed_ms)
            
            return state.model_copy(update={"processing_latency_ms": elapsed_ms})

        except TelemetryDeadlineException as tde:
            # Hardware Override Fail-Safe Triage Path
            elapsed_ms = (time.time() - start_time) * 1000
            return state.model_copy(update={
                "override_activated": True,
                "geofence_breached": True,
                "recommended_braking_force": 1.0,  # Engage maximum physical mechanical braking forces
                "processing_latency_ms": elapsed_ms
            }).append_trace(f"HARDWARE OVERRIDE INITIATED: {str(tde)}")

    def _run_geofence_worker(self, state: TelemetryState) -> TelemetryState:
        # Core algorithmic coordinates containment logic checking (mocked behavior pattern)
        # In production, replace with sharp r-tree/shapely spatial boundary evaluations
        if state.latitude == 0.0 or state.longitude == 0.0:
            return state.model_copy(update={"geofence_breached": True, "active_geofences": ["RESTRICTED_ZONE_A"]}).append_trace("Worker 1: Geofence perimeter violation confirmed.")
        return state.append_trace("Worker 1: Geofence constraints clear.")

    def _run_collision_worker(self, state: TelemetryState) -> TelemetryState:
        if state.geofence_breached and state.current_speed_mph > 25:
            return state.model_copy(update={"collision_risk_detected": True, "recommended_braking_force": 0.75}).append_trace("Worker 2: Hazard confirmed. Calculated 75% required decelerating thrust force.")
        return state.append_trace("Worker 2: Collision mitigation clear.")

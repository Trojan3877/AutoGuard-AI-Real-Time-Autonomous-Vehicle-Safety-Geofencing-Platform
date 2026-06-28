# agents/guards.py
class TelemetryDeadlineException(Exception):
    """Raised when an active safety agent breaches the sub-5ms processing boundary."""
    pass

class SafetyCircuitBreaker:
    """
    Active hardware monitoring circuit designed to handle processing exceptions 
    or unexpected system lag in autonomous vehicle control units.
    """
    def __init__(self, critical_deadline_ms: float = 5.0):
        self.critical_deadline_ms = critical_deadline_ms
        self.system_status = "OPERATIONAL"  # OPERATIONAL, OVERRIDE_TRIPPED

    def evaluate_deadline(self, elapsed_ms: float):
        """Trips the hardware safety system if processing threatens vehicle control loops."""
        if elapsed_ms > self.critical_deadline_ms:
            self.system_status = "OVERRIDE_TRIPPED"
            raise TelemetryDeadlineException(
                f"CRITICAL SLA FAULT: System latency reached {elapsed_ms:.2f}ms (Deadline Bound: {self.critical_deadline_ms}ms)."
            )

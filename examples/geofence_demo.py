"""
AutoGuard-AI CUDA Geofence Verification
========================================

High-performance GPU-accelerated Point-in-Polygon (PIP) verification for autonomous
vehicle geofence safety systems. This module demonstrates async stream-based kernel
execution for real-time vehicle coordinate validation.

Usage:
------
import torch
import geofence_cuda

# Create sample data on GPU
vehicles = torch.randn(1000, 2, device='cuda', dtype=torch.float32) * 100
polygon = torch.tensor([
    [0.0, 0.0],
    [100.0, 0.0],
    [100.0, 100.0],
    [0.0, 100.0]
], device='cuda', dtype=torch.float32)

# Synchronous execution (blocks until complete)
violations = geofence_cuda.geofence_pip_cuda(vehicles, polygon)

# Asynchronous execution with manual stream (non-blocking)
stream = torch.cuda.Stream()
with torch.cuda.stream(stream):
    violations_async = geofence_cuda.geofence_pip_cuda(
        vehicles, polygon,
        stream_id=stream.cuda_stream
    )

print(f"Vehicles inside geofence: {violations.sum().item()}")
"""

import torch
import geofence_cuda
from typing import Tuple
import time


class GeofenceViolationDetector:
    """
    Real-time geofence violation detector with GPU acceleration.
    
    Attributes:
        polygon (torch.Tensor): Polygon vertices [M, 2] cached on GPU
        device (torch.device): GPU device for computation
        stream (torch.cuda.Stream): CUDA stream for asynchronous operations
    """
    
    def __init__(self, polygon_vertices: torch.Tensor, use_async_stream: bool = True):
        """
        Initialize geofence detector.
        
        Args:
            polygon_vertices: Tensor [M, 2] of polygon vertices (float32)
            use_async_stream: If True, create dedicated stream for async execution
        """
        assert polygon_vertices.is_cuda(), "Polygon must be on GPU"
        assert polygon_vertices.dtype == torch.float32, "Polygon must be float32"
        assert polygon_vertices.dim() == 2 and polygon_vertices.size(1) == 2, \
            "Polygon must have shape [M, 2]"
        
        self.polygon = polygon_vertices.contiguous()
        self.device = polygon_vertices.device
        self.stream = torch.cuda.Stream(device=self.device) if use_async_stream else None
    
    def check_violations(
        self,
        vehicle_coords: torch.Tensor,
        synchronous: bool = False
    ) -> torch.Tensor:
        """
        Check which vehicles violate the geofence boundary.
        
        Args:
            vehicle_coords: Tensor [N, 2] of vehicle coordinates (float32)
            synchronous: If True, block until computation completes
        
        Returns:
            Boolean mask tensor [N] where True indicates geofence violation
        """
        assert vehicle_coords.is_cuda(), "Vehicle coords must be on GPU"
        assert vehicle_coords.dtype == torch.float32, "Vehicle coords must be float32"
        assert vehicle_coords.dim() == 2 and vehicle_coords.size(1) == 2, \
            "Vehicle coords must have shape [N, 2]"
        
        vehicle_coords = vehicle_coords.contiguous()
        
        if synchronous or self.stream is None:
            # Synchronous execution
            return geofence_cuda.geofence_pip_cuda_sync(
                vehicle_coords, self.polygon,
                sync=True
            )
        else:
            # Asynchronous execution with dedicated stream
            with torch.cuda.stream(self.stream):
                violations = geofence_cuda.geofence_pip_cuda(
                    vehicle_coords,
                    self.polygon,
                    stream_id=int(self.stream.cuda_stream)
                )
            return violations
    
    def get_violation_indices(
        self,
        vehicle_coords: torch.Tensor,
        synchronous: bool = False
    ) -> torch.Tensor:
        """
        Get indices of vehicles that violate the geofence.
        
        Args:
            vehicle_coords: Tensor [N, 2] of vehicle coordinates
            synchronous: If True, block until computation completes
        
        Returns:
            1D tensor of indices where violations occur
        """
        violations = self.check_violations(vehicle_coords, synchronous)
        return torch.where(violations)[0]


def benchmark_geofence_detection(
    num_vehicles: int = 10000,
    num_vertices: int = 100,
    iterations: int = 100,
    use_async: bool = True
) -> Tuple[float, float]:
    """
    Benchmark geofence detection performance.
    
    Args:
        num_vehicles: Number of vehicles to test
        num_vertices: Number of polygon vertices
        iterations: Number of iterations for averaging
        use_async: If True, use asynchronous stream execution
    
    Returns:
        (avg_time_ms, throughput_vehicles_per_second)
    """
    # Create test data
    vehicles = torch.randn(num_vehicles, 2, device='cuda', dtype=torch.float32) * 1000
    polygon = torch.randn(num_vertices, 2, device='cuda', dtype=torch.float32) * 1000
    
    detector = GeofenceViolationDetector(polygon, use_async_stream=use_async)
    
    # Warmup
    _ = detector.check_violations(vehicles, synchronous=True)
    torch.cuda.synchronize()
    
    # Benchmark
    times = []
    for _ in range(iterations):
        torch.cuda.synchronize()
        start = time.perf_counter()
        
        violations = detector.check_violations(vehicles, synchronous=True)
        
        torch.cuda.synchronize()
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
    
    avg_time_ms = sum(times[10:]) / (iterations - 10)  # Exclude warmup
    throughput = (num_vehicles / avg_time_ms) * 1000  # vehicles/sec
    
    return avg_time_ms, throughput


def example_pipeline_with_streams():
    """
    Example: pipelined execution with multiple CUDA streams for overlapped computation.
    """
    print("=== AutoGuard-AI CUDA Geofence Pipeline Example ===")
    print()
    
    # Create geofence polygon (rectangular boundary)
    polygon = torch.tensor([
        [-10.0, -10.0],
        [110.0, -10.0],
        [110.0, 110.0],
        [-10.0, 110.0]
    ], device='cuda', dtype=torch.float32)
    
    detector = GeofenceViolationDetector(polygon, use_async_stream=True)
    
    # Simulate batch processing with overlapped streams
    batch_size = 5000
    num_batches = 4
    
    streams = [torch.cuda.Stream() for _ in range(num_batches)]
    results = []
    
    print(f"Processing {num_batches} batches of {batch_size} vehicles asynchronously...")
    print()
    
    # Launch all batches asynchronously
    for i in range(num_batches):
        vehicles = torch.randn(batch_size, 2, device='cuda', dtype=torch.float32) * 200 - 100
        
        with torch.cuda.stream(streams[i]):
            violations = detector.check_violations(vehicles, synchronous=False)
            results.append((i, violations))
    
    # Synchronize and collect results
    torch.cuda.synchronize()
    
    for batch_idx, violations in results:
        num_violations = violations.sum().item()
        print(f"Batch {batch_idx}: {num_violations}/{batch_size} vehicles violating geofence "
              f"({100*num_violations/batch_size:.1f}%)")
    
    print()
    print("=== Performance Benchmark ===")
    print()
    avg_time, throughput = benchmark_geofence_detection(
        num_vehicles=100000,
        num_vertices=200,
        iterations=50,
        use_async=True
    )
    print(f"Average latency: {avg_time:.3f} ms")
    print(f"Throughput: {throughput:.0f} vehicles/second")


if __name__ == "__main__":
    example_pipeline_with_streams()

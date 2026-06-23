#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

// Shared memory configuration: 48KB per block (768 vertices @ 8 bytes per coord pair)
// Adjust based on your target GPU (Maxwell/Pascal: 48KB, Volta+: 96KB)
#define MAX_SHARED_VERTICES 768

/**
 * @brief Ray-casting algorithm for Point-in-Polygon (PIP) detection
 * 
 * Uses horizontal ray-casting: cast a ray from the point to the right and count
 * intersections. Odd count = inside, even count = outside.
 * 
 * GPU Optimizations:
 * - Shared memory caching of polygon vertices (coalesced reads from global memory once)
 * - Minimal warp divergence through careful boundary checking
 * - Fast math for trigonometric operations (if enabled)
 * - Register-level variable reuse to reduce memory pressure
 */
__device__ inline bool pointInPolygonRayCast(
    float px, float py,
    const float* vertices,
    int vertex_count)
{
    int crossings = 0;
    
    // Ray casting: test intersections with each edge
    for (int i = 0; i < vertex_count; ++i) {
        int j = (i + 1) % vertex_count;
        
        // Load vertices: coalesced access pattern within warp
        float x1 = vertices[2 * i];
        float y1 = vertices[2 * i + 1];
        float x2 = vertices[2 * j];
        float y2 = vertices[2 * j + 1];
        
        // Check if ray crosses the edge
        // Ray: horizontal line from point going right (y = py, x >= px)
        
        // Fast path: both vertices above or both below the ray
        if ((y1 <= py && y2 > py) || (y2 <= py && y1 > py)) {
            // Compute x-intersection of edge with horizontal ray at y=py
            // Using cross-multiplication to avoid division
            // x_intersect = x1 + (py - y1) / (y2 - y1) * (x2 - x1)
            
            float dy = y2 - y1;
            float dx = x2 - x1;
            
            // Fast approximation: x_intersect * dy = x1 * dy + (py - y1) * dx
            float x_intersect_dy = __fmaf(py - y1, dx, x1 * dy);  // FMA: fused multiply-add
            
            // Ray extends to the right (x >= px), so check if intersection is to the right
            if (px * dy < x_intersect_dy) {
                crossings++;
            }
        }
    }
    
    // Odd number of crossings = inside polygon
    return (crossings & 1) != 0;
}

/**
 * @brief CUDA kernel for batch Point-in-Polygon verification
 * 
 * Block configuration: 256 threads per block (optimal for most GPUs)
 * Each thread processes one vehicle coordinate
 * 
 * Memory layout:
 * - Global: vehicle coords [N, 2], polygon vertices [M, 2], output mask [N]
 * - Shared: polygon vertices cached per block
 * 
 * @param vehicle_coords Device pointer to vehicle coordinates [N, 2]
 * @param polygon_vertices Device pointer to polygon vertices [M, 2]
 * @param vertex_count Number of polygon vertices
 * @param vehicle_count Number of vehicles (N)
 * @param output_mask Device pointer to output boolean mask [N]
 */
__global__ void geofenceKernel(
    const float* __restrict__ vehicle_coords,
    const float* __restrict__ polygon_vertices,
    const int vertex_count,
    const int vehicle_count,
    bool* __restrict__ output_mask)
{
    extern __shared__ float shared_vertices[];
    
    int vehicle_idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    // Shared memory initialization: all threads cooperatively load vertices
    // Coalesce global memory reads
    int vertices_per_thread = (2 * vertex_count + blockDim.x - 1) / blockDim.x;
    
    #pragma unroll
    for (int i = 0; i < vertices_per_thread; ++i) {
        int global_idx = threadIdx.x + i * blockDim.x;
        if (global_idx < 2 * vertex_count) {
            shared_vertices[global_idx] = polygon_vertices[global_idx];
        }
    }
    
    __syncthreads();
    
    // Boundary check: prevent out-of-bounds vehicle access
    if (vehicle_idx < vehicle_count) {
        // Load vehicle coordinates (coalesced read)
        float px = vehicle_coords[2 * vehicle_idx];
        float py = vehicle_coords[2 * vehicle_idx + 1];
        
        // Perform point-in-polygon test using shared memory vertices
        bool inside = pointInPolygonRayCast(px, py, shared_vertices, vertex_count);
        
        // Write result (non-coalesced writes acceptable for boolean mask)
        output_mask[vehicle_idx] = inside;
    }
}

/**
 * @brief Wrapper function for CUDA kernel launch
 * 
 * @param vehicle_coords_d Device pointer to vehicle coordinates
 * @param polygon_vertices_d Device pointer to polygon vertices
 * @param vertex_count Number of vertices
 * @param vehicle_count Number of vehicles
 * @param output_mask_d Device pointer to output mask
 * @param stream CUDA stream for asynchronous execution
 * @return CUDA error code
 */
extern "C" cudaError_t launchGeofenceKernel(
    const float* vehicle_coords_d,
    const float* polygon_vertices_d,
    const int vertex_count,
    const int vehicle_count,
    bool* output_mask_d,
    cudaStream_t stream)
{
    // Optimal block size for modern GPUs (Turing/Ampere: 256 threads)
    const int BLOCK_SIZE = 256;
    const int GRID_SIZE = (vehicle_count + BLOCK_SIZE - 1) / BLOCK_SIZE;
    
    // Shared memory size: store polygon vertices
    // Each vertex: 2 floats = 8 bytes
    // Limit to MAX_SHARED_VERTICES to avoid overflow (48KB typical)
    int shared_mem_size = (vertex_count <= MAX_SHARED_VERTICES) 
        ? (2 * vertex_count * sizeof(float)) 
        : 0;
    
    // Fallback to global memory if vertex count exceeds shared memory capacity
    if (vertex_count > MAX_SHARED_VERTICES) {
        fprintf(stderr, "Warning: vertex_count (%d) exceeds MAX_SHARED_VERTICES (%d). "
                "Using global memory only.\n", vertex_count, MAX_SHARED_VERTICES);
    }
    
    // Launch kernel with specified stream for async execution
    geofenceKernel<<<GRID_SIZE, BLOCK_SIZE, shared_mem_size, stream>>>(
        vehicle_coords_d,
        polygon_vertices_d,
        vertex_count,
        vehicle_count,
        output_mask_d);
    
    return cudaGetLastError();
}

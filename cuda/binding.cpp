#include <torch/extension.h>
#include <cuda_runtime.h>
#include <vector>

// Forward declaration of CUDA kernel wrapper
extern "C" cudaError_t launchGeofenceKernel(
    const float* vehicle_coords_d,
    const float* polygon_vertices_d,
    const int vertex_count,
    const int vehicle_count,
    bool* output_mask_d,
    cudaStream_t stream);

/**
 * @brief PyTorch C++ binding for geofence kernel
 * 
 * Validates input tensors, manages memory transfers, and launches CUDA operations
 * with stream support for asynchronous execution.
 * 
 * @param vehicle_coords Tensor [N, 2] of vehicle coordinates (float32)
 * @param polygon_vertices Tensor [M, 2] of polygon vertices (float32)
 * @param stream_id Optional CUDA stream ID for async execution (default: 0 = default stream)
 * @return Boolean mask tensor [N] indicating geofence violations
 */
torch::Tensor geofence_pip_cuda(
    torch::Tensor vehicle_coords,
    torch::Tensor polygon_vertices,
    const int64_t stream_id = 0)
{
    // Input validation
    TORCH_CHECK(vehicle_coords.is_cuda(), "vehicle_coords must be a CUDA tensor");
    TORCH_CHECK(polygon_vertices.is_cuda(), "polygon_vertices must be a CUDA tensor");
    TORCH_CHECK(vehicle_coords.dtype() == torch::kFloat32, "vehicle_coords must be float32");
    TORCH_CHECK(polygon_vertices.dtype() == torch::kFloat32, "polygon_vertices must be float32");
    TORCH_CHECK(vehicle_coords.is_contiguous(), "vehicle_coords must be contiguous");
    TORCH_CHECK(polygon_vertices.is_contiguous(), "polygon_vertices must be contiguous");
    TORCH_CHECK(vehicle_coords.size(1) == 2, "vehicle_coords must have shape [N, 2]");
    TORCH_CHECK(polygon_vertices.size(1) == 2, "polygon_vertices must have shape [M, 2]");
    
    int vehicle_count = vehicle_coords.size(0);
    int vertex_count = polygon_vertices.size(0);
    
    // Create output tensor for boolean mask
    torch::Tensor output_mask = torch::zeros(
        {vehicle_count},
        torch::TensorOptions()
            .dtype(torch::kBool)
            .device(vehicle_coords.device())
    );
    
    // Get device pointers
    float* vehicle_coords_d = vehicle_coords.data_ptr<float>();
    float* polygon_vertices_d = polygon_vertices.data_ptr<float>();
    bool* output_mask_d = output_mask.data_ptr<bool>();
    
    // Get CUDA stream (user-provided or default)
    cudaStream_t stream = (stream_id == 0) ? nullptr : reinterpret_cast<cudaStream_t>(stream_id);
    
    // Launch kernel asynchronously
    cudaError_t err = launchGeofenceKernel(
        vehicle_coords_d,
        polygon_vertices_d,
        vertex_count,
        vehicle_count,
        output_mask_d,
        stream);
    
    // Check for kernel launch errors
    TORCH_CHECK(err == cudaSuccess, "CUDA kernel launch failed: ", cudaGetErrorString(err));
    
    return output_mask;
}

/**
 * @brief PyTorch C++ binding with stream synchronization
 * 
 * Allows explicit synchronization before Python code continues.
 * Useful when you need to ensure GPU operations complete before accessing results.
 * 
 * @param vehicle_coords Tensor [N, 2] of vehicle coordinates (float32)
 * @param polygon_vertices Tensor [M, 2] of polygon vertices (float32)
 * @param sync If true, synchronize the device after kernel launch
 * @return Boolean mask tensor [N] indicating geofence violations
 */
torch::Tensor geofence_pip_cuda_sync(
    torch::Tensor vehicle_coords,
    torch::Tensor polygon_vertices,
    const bool sync = false)
{
    // Validate inputs (same as above)
    TORCH_CHECK(vehicle_coords.is_cuda(), "vehicle_coords must be a CUDA tensor");
    TORCH_CHECK(polygon_vertices.is_cuda(), "polygon_vertices must be a CUDA tensor");
    TORCH_CHECK(vehicle_coords.dtype() == torch::kFloat32, "vehicle_coords must be float32");
    TORCH_CHECK(polygon_vertices.dtype() == torch::kFloat32, "polygon_vertices must be float32");
    TORCH_CHECK(vehicle_coords.is_contiguous(), "vehicle_coords must be contiguous");
    TORCH_CHECK(polygon_vertices.is_contiguous(), "polygon_vertices must be contiguous");
    TORCH_CHECK(vehicle_coords.size(1) == 2, "vehicle_coords must have shape [N, 2]");
    TORCH_CHECK(polygon_vertices.size(1) == 2, "polygon_vertices must have shape [M, 2]");
    
    int vehicle_count = vehicle_coords.size(0);
    int vertex_count = polygon_vertices.size(0);
    
    // Create output tensor
    torch::Tensor output_mask = torch::zeros(
        {vehicle_count},
        torch::TensorOptions()
            .dtype(torch::kBool)
            .device(vehicle_coords.device())
    );
    
    // Get device pointers
    float* vehicle_coords_d = vehicle_coords.data_ptr<float>();
    float* polygon_vertices_d = polygon_vertices.data_ptr<float>();
    bool* output_mask_d = output_mask.data_ptr<bool>();
    
    // Launch kernel on default stream
    cudaError_t err = launchGeofenceKernel(
        vehicle_coords_d,
        polygon_vertices_d,
        vertex_count,
        vehicle_count,
        output_mask_d,
        nullptr);  // Default stream
    
    TORCH_CHECK(err == cudaSuccess, "CUDA kernel launch failed: ", cudaGetErrorString(err));
    
    // Optional synchronization
    if (sync) {
        cudaDeviceSynchronize();
    }
    
    return output_mask;
}

// PyTorch module binding
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("geofence_pip_cuda", &geofence_pip_cuda,
        "Point-in-Polygon geofence verification (async, stream-enabled)",
        torch::pybind11_module_arg("vehicle_coords"),
        torch::pybind11_module_arg("polygon_vertices"),
        pybind11::arg("stream_id") = 0);
    
    m.def("geofence_pip_cuda_sync", &geofence_pip_cuda_sync,
        "Point-in-Polygon geofence verification (with optional sync)",
        torch::pybind11_module_arg("vehicle_coords"),
        torch::pybind11_module_arg("polygon_vertices"),
        pybind11::arg("sync") = false);
}

from setuptools import setup, Extension
from torch.utils import cpp_extension
import torch
import os

# Get CUDA include directories
cuda_home = os.environ.get('CUDA_HOME', '/usr/local/cuda')
cuda_include = os.path.join(cuda_home, 'include')

# Define the CUDA extension
geofence_extension = cpp_extension.CUDAExtension(
    name='geofence_cuda',  # Module name
    sources=[
        'cuda/geofence_kernel.cu',
        'cuda/binding.cpp'
    ],
    include_dirs=[
        cuda_include,
        torch.utils.cpp_extension.include_paths()[0]
    ],
    extra_compile_args={
        'cxx': ['-O3', '-march=native'],
        'nvcc': [
            '-O3',
            '-gencode', 'arch=compute_70,code=sm_70',  # V100, RTX 20XX
            '-gencode', 'arch=compute_75,code=sm_75',  # RTX 20XX, A10
            '-gencode', 'arch=compute_80,code=sm_80',  # A100, RTX 30XX
            '-gencode', 'arch=compute_86,code=sm_86',  # RTX 30XX
            '-gencode', 'arch=compute_89,code=sm_89',  # RTX 40XX
            '--ftz=true',                               # Flush denormals to zero
            '--use_fast_math',                          # Enable fast math
            '--prec-div=false',                         # Relaxed division precision
            '--prec-sqrt=false',                        # Relaxed sqrt precision
        ]
    },
    extra_ldflags=[
        f'-L{os.path.join(cuda_home, "lib64")}',
        '-lcudart'
    ]
)

setup(
    name='geofence_cuda',
    version='1.0.0',
    author='AutoGuard-AI',
    description='CUDA-accelerated Point-in-Polygon geofence verification',
    ext_modules=[geofence_extension],
    cmdclass={'build_ext': cpp_extension.BuildExtension},
    python_requires='>=3.8',
    install_requires=[
        'torch>=1.9.0',
    ],
)

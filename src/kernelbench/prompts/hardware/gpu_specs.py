"""
A List of GPU Specs to include in the prompt

"""

GPU_SPEC_INFO = {
    "L40S": {
        "GPU Architecture": "Ada",
        "GPU Memory": "48GB GDDR6 with ECC",
        "Memory Bandwidth": "864 GB/s",
        "RT Core Performance TFLOPS": "212",
        "FP32 TFLOPS": "91.6",
        "TF32 Tensor Core TFLOPS": "183.2 (366 with sparsity)",
        "FP16 Tensor Core TFLOPS": "362.05 (733 with sparsity)",
        "FP8 Tensor Core TFLOPS": "733 (1466 with sparsity)",
        "Peak INT8 Tensor TOPS": "733 (1466 with sparsity)",
        "Peak INT4 Tensor TOPS": "733 (1466 with sparsity)",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "24",
        "Shared memory capacity per SM": "100 KB",
        "Maximum shared memory per thread block": "99 KB",
    },
    "H100": {
        "GPU Architecture": "Hopper",
        "GPU Memory": "80GB",
        "Memory Bandwidth": "3.35 TB/s",
        "FP64 TFLOPS": "34",
        "FP64 Tensor Core TFLOPS": "67",
        "FP32 TFLOPS": "67",
        "TF32 Tensor Core TFLOPS": "989 with sparsity",
        "BFLOAT16 Tensore Core TFLOPS": "1979 with sparsity",
        "FP16 Tensor Core TFLOPS": "1979 with sparsity",
        "FP8 Tensor Core TFLOPS": "3958 with sparsity",
        "INT8 Tensor Core TOPS": "3958 with sparsity",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "32",
        "Shared memory capacity per SM": "228 KB",
        "Maximum shared memory per thread block": "227 KB",
    },
    # this is 40GB (Standard)
    "A100": {
        "GPU Architecture": "Ampere",
        "GPU Memory": "40GB",
        "Memory Bandwidth": "1935 GB/s",
        "FP64 TFLOPS": "9.7",
        "FP64 Tensor Core TFLOPS": "19.5",
        "FP32 TFLOPS": "19.5",
        "TF32 Tensor Core TFLOPS": "156 (312 with sparsity)",
        "BFLOAT16 Tensore Core TFLOPS": "312 (624 with sparsity)",
        "FP16 Tensor Core TFLOPS": "312 (624 with sparsity)",
        "INT8 Tensor Core TOPS": "624 (1248 with sparsity)",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "32",
        "Shared memory capacity per SM": "164 KB",
        "Maximum shared memory per thread block": "163 KB",
    },
    "A100-80GB": {
        "GPU Architecture": "Ampere",
        "GPU Memory": "80GB",
        "Memory Bandwidth": "1935 GB/s",
        "FP64 TFLOPS": "9.7",
        "FP64 Tensor Core TFLOPS": "19.5",
        "FP32 TFLOPS": "19.5",
        "TF32 Tensor Core TFLOPS": "156 (312 with sparsity)",
        "BFLOAT16 Tensore Core TFLOPS": "312 (624 with sparsity)",
        "FP16 Tensor Core TFLOPS": "312 (624 with sparsity)",
        "INT8 Tensor Core TOPS": "624 (1248 with sparsity)",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "32",
        "Shared memory capacity per SM": "164 KB",
        "Maximum shared memory per thread block": "163 KB",
    },
    "L4": {
        "GPU Architecture": "Ada",
        "GPU Memory": "24GB",
        "Memory Bandwidth": "300 GB/s",
        "FP32 TFLOPS": "30.3",
        "TF32 Tensor Core TFLOPS": "120 with sparsity",
        "BFLOAT16 Tensore Core TFLOPS": "242 with sparsity",
        "FP8 Tensor Core TFLOPS": "485 with sparsity",
        "INT8 Tensor Core TOPS": "485 with sparsity",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "24",
        "Shared memory capacity per SM": "100 KB",
        "Maximum shared memory per thread block": "99 KB",
    },
    "T4": {
        "GPU Architecture": "Turing",
        "GPU Memory": "16 GB GDDR6",
        "Memory Bandwidth": "300 GB/s",
        "Single-Precision TFLOPS": "8.1",
        "Mixed-Precision (FP16/FP32) TFLOPS": "65",
        "INT8 TOPS": "130",
        "INT4 TOPS": "260",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "16",
        "Shared memory capacity per SM": "64 KB",
    },
    "A10G": {
        "GPU Architecture": "Ampere",
        "GPU Memory": "24GB GDDR6",
        "Memory Bandwidth": "600 GB/s",
        "FP32 TFLOPS": "31.2",
        "TF32 Tensor Core TFLOPS": "62.5 (125 with sparsity)",
        "BFLOAT16 Tensore Core TFLOPS": "125 (250 with sparsity)",
        "FP16 Tensor Core TFLOPS": "125 (250 with sparsity)",
        "INT8 Tensor Core TOPS": "250 (500 with sparsity)",
        "INT4 Tensor Core TOPS": "500 (1000 with sparsity)",
        "Register File Size": "64K 32-bit registers per SM",
        "Maximum number of registers per thread": "255",
        "Maximum number of thread blocks per SM": "32",
        "Shared memory capacity per SM": "164 KB",
        "Maximum shared memory per thread block": "163 KB",
    },
}

# Basic GPU concept definitions
GPU_DEFINITIONS = {
    "Thread": "A thread is a single execution unit that can run a single instruction at a time.",
    "Thread Block": "A thread block is a group of threads that can cooperate with each other.",
    "Warp": "A warp is a group of threads that are scheduled together and execute in parallel.",
    "Shared Memory": "Shared memory is a memory space that can be accessed by all threads in a thread block.",
    "Register": "A register is a small memory space that can be accessed by a single thread.",
    "Memory Hierarchy": "Memory hierarchy is a pyramid of memory types with different speeds and sizes.",
    "Memory Bandwidth": "Memory bandwidth is the rate at which data can be read from or stored into memory.",
    "Cache": "Cache is a small memory space that stores frequently accessed data.",
    "HBM": "HBM is a high-bandwidth memory technology that uses 3D-stacked DRAM.",
}


GPU_BEST_PRACTICES = [
    # From https://docs.nvidia.com/cuda/ada-tuning-guide/index.html
    # CUDA Best Practices Section
    "Find ways to parallelize sequential code.",
    "Minimize data transfers between the host and the device.",
    "Adjust kernel launch configuration to maximize device utilization.",
    "Ensure that global memory accesses are coalesced.",
    "Minimize redundant accesses to global memory whenever possible.",
    "Avoid long sequences of diverged execution by threads within the same warp.",
    # we added this to reference the specific GPU architecture
    "Use specialized instructions based on the specific GPU architecture",
]

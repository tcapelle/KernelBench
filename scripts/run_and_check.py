import os
import shutil
import importlib.util
import sys
import tempfile

import torch
import numpy as np
import pydra
from pydra import REQUIRED, Config
from datasets import load_dataset

from kernelbench.eval import eval_kernel_against_ref, KernelExecResult
from kernelbench.utils import read_file, set_gpu_arch

"""
Run a pair of KernelBench format (problem, solution) to check if solution is correct and compute speedup

You will need two files
1. Reference: PyTorch reference (module Model) implementation with init and input shapes
2. Solution: PyTorch solution (module ModelNew) with inline CUDA Code
Please see examples in src/prompts

The Reference could be either
1. a local file: specify the path to the file
2. a kernelbench problem: specify level and problem id

====================================================
Usage:
1. PyTorch reference is a local file
python3 scripts/run_and_check.py ref_origin=local ref_arch_src_path=src/prompts/model_ex_add.py kernel_src_path=src/prompts/model_new_ex_add.py

2. PyTorch refernece is a kernelbench problem
python3 scripts/run_and_check.py ref_origin=kernelbench level=<level> problem_id=<problem_id> kernel_src_path=<path to model-generated kernel>
====================================================

"""

torch.set_printoptions(precision=4, threshold=10)


class ScriptConfig(Config):
    def __init__(self):

        # Problem and Solution definition
        # Input src origin definition
        self.ref_origin = REQUIRED  # either local or kernelbench
        # ref_origin is local, specify local file path
        self.ref_arch_src_path = ""
        # ref_origin is kernelbench, specify level and problem id
        self.dataset_name = "ScalingIntelligence/KernelBench"
        self.level = ""
        self.problem_id = ""
        # Solution src definition
        self.kernel_src_path = ""

        # KernelBench Eval specific
        # number of trials to run for correctness
        self.num_correct_trials = 5
        # number of trials to run for performance
        self.num_perf_trials = 100
        # timeout for each trial
        self.timeout = 300
        # verbose logging
        self.verbose = False
        self.measure_performance = True
        self.build_dir_prefix = ""  # if you want to specify a custom build directory
        self.clear_cache = False  # TODO

        # Replace with your NVIDIA GPU architecture, e.g. ["Hopper"]
        self.gpu_arch = ["Ada"]

    def __repr__(self):
        return f"ScriptConfig({self.to_dict()})"


def evaluate_single_sample_src(
    ref_arch_src: str, kernel_src: str, configs: dict, device: torch.device
) -> KernelExecResult:
    """
    Evaluate a single sample source code against a reference source code
    """

    kernel_hash = str(hash(kernel_src))
    build_dir = os.path.join(configs["build_dir_prefix"], "test_build", kernel_hash)

    if configs["clear_cache"]:  # fresh kernel build
        print(f"[INFO] Clearing cache for build directory: {build_dir}")
        shutil.rmtree(build_dir, ignore_errors=True)

    num_correct_trials = configs["num_correct_trials"]
    num_perf_trials = configs["num_perf_trials"]
    verbose = configs["verbose"]
    measure_performance = configs["measure_performance"]
    try:
        eval_result = eval_kernel_against_ref(
            original_model_src=ref_arch_src,
            custom_model_src=kernel_src,
            measure_performance=measure_performance,
            verbose=verbose,
            num_correct_trials=num_correct_trials,
            num_perf_trials=num_perf_trials,
            build_dir=build_dir,
            device=device,
        )
        return eval_result
    except Exception as e:
        print(f"[WARNING] Last level catch: Some issue evaluating for kernel: {e} ")
        if "CUDA error" in str(e):
            # NOTE: count this as compilation failure as it is not runnable code
            metadata = {
                "cuda_error": f"CUDA Error: {str(e)}",
                "hardware": torch.cuda.get_device_name(device=device),
                "device": str(device),
            }
            eval_result = KernelExecResult(
                compiled=False, correctness=False, metadata=metadata
            )
            return eval_result
        else:
            metadata = {
                "other_error": f"error: {str(e)}",
                "hardware": torch.cuda.get_device_name(device=device),
                "device": str(device),
            }
            eval_result = KernelExecResult(
                compiled=False, correctness=False, metadata=metadata
            )
            return eval_result


def measure_program_time(
    ref_arch_name: str,  # Added for consistency, although not used in this version
    ref_arch_src: str,
    num_trials: int,
    device: torch.device,
    use_torch_compile: bool = False,
    torch_compile_backend: str | None = None,
    torch_compile_options: str | None = None,
) -> dict:
    """Measure the execution time of a reference program"""

    # Create temporary module
    temp_dir = tempfile.mkdtemp()
    ref_module_path = os.path.join(temp_dir, "ref_module.py")

    with open(ref_module_path, "w") as f:
        f.write(ref_arch_src)

    # Load reference module
    spec = importlib.util.spec_from_file_location("ref_module", ref_module_path)
    ref_module = importlib.util.module_from_spec(spec)
    sys.modules["ref_module"] = ref_module
    spec.loader.exec_module(ref_module)

    # Create model instance
    if hasattr(ref_module, "get_init_inputs"):
        init_inputs = ref_module.get_init_inputs()
        init_inputs = [
            (
                x
                if (isinstance(x, torch.Tensor) and x.device == device)
                else (x.to(device) if isinstance(x, torch.Tensor) else x)
            )
            for x in init_inputs
        ]
        ref_model = ref_module.Model(*init_inputs).to(device)
    else:
        ref_model = ref_module.Model().to(device)

    # Apply torch.compile if needed
    if use_torch_compile:
        if torch_compile_backend is not None:
            if torch_compile_options is not None and torch_compile_options != "default":
                compile_options = (
                    {"mode": torch_compile_options}
                    if torch_compile_options in ["max-autotune", "reduce-overhead"]
                    else {}
                )
                ref_model = torch.compile(
                    ref_model,
                    backend=torch_compile_backend,
                    options=compile_options,
                )
            else:
                ref_model = torch.compile(ref_model, backend=torch_compile_backend)
        else:
            ref_model = torch.compile(ref_model)

    # Generate inputs
    if hasattr(ref_module, "get_inputs"):
        inputs = ref_module.get_inputs()
        inputs = [
            (
                x
                if (isinstance(x, torch.Tensor) and x.device == device)
                else (x.to(device) if isinstance(x, torch.Tensor) else x)
            )
            for x in inputs
        ]
    elif hasattr(ref_module, "INPUT_SHAPE"):
        input_shape = ref_module.INPUT_SHAPE
        if isinstance(input_shape, tuple):
            inputs = (torch.randn(input_shape, device=device),)
        elif isinstance(input_shape, list):
            inputs = tuple(torch.randn(shape, device=device) for shape in input_shape)
        else:
            raise ValueError(f"Invalid INPUT_SHAPE: {input_shape}")
    else:
        # Infer inputs from model
        if hasattr(ref_model, "forward"):
            argcount = ref_model.forward.__code__.co_argcount
            inputs = tuple(
                torch.randn(1, 128, device=device) for _ in range(argcount - 1)
            )
        else:
            raise ValueError("Could not determine appropriate inputs for the model")

    # Warmup
    for _ in range(10):
        ref_model(*inputs)

    # Timing
    torch.cuda.synchronize(device=device)
    times = []
    for _ in range(num_trials):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)

        start.record()
        ref_model(*inputs)
        end.record()

        torch.cuda.synchronize(device=device)
        times.append(start.elapsed_time(end))

    # Clean up
    try:
        os.remove(ref_module_path)
        os.rmdir(temp_dir)
    except OSError:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Calculate statistics
    times = np.array(times)
    return {
        "mean": float(np.mean(times)),
        "std": float(np.std(times)),
        "min": float(np.min(times)),
        "max": float(np.max(times)),
        "median": float(np.median(times)),
    }


@pydra.main(base=ScriptConfig)
def main(config: ScriptConfig):

    print("Running with config", config)

    # Fetch reference and kernel code

    assert (
        config.ref_origin == "local" or config.ref_origin == "kernelbench"
    ), "ref_origin must be either local or kernelbench"
    assert config.kernel_src_path != "", "kernel_src_path is required"

    if config.ref_origin == "local":
        assert config.ref_arch_src_path != "", "ref_arch_src_path is required"
        ref_arch_src = read_file(config.ref_arch_src_path)
    elif config.ref_origin == "kernelbench":
        assert config.dataset_name != "", "dataset_name is required"
        assert config.level != "", "level is required"
        assert config.problem_id != "", "problem_id is required"

        # for now use the HuggingFace dataset
        dataset = load_dataset(config.dataset_name)
        curr_level_dataset = dataset[f"level_{config.level}"]

        curr_problem_row = curr_level_dataset.filter(
            lambda x: x["problem_id"] == config.problem_id
        )
        ref_arch_src = curr_problem_row["code"][0]
        problem_name = curr_problem_row["name"][0]

        problem_number = int(problem_name.split("_")[0])
        assert (
            problem_number == config.problem_id
        ), f"Problem number in filename ({problem_number}) does not match config problem_id ({config.problem_id})"

        print(
            f"Fetched problem {config.problem_id} from KernelBench level {config.level}: {problem_name}"
        )

    else:
        raise ValueError("Invalid ref_origin")

    kernel_src = read_file(config.kernel_src_path)

    # Start Evaluation
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    set_gpu_arch(config.gpu_arch)

    print("[INFO] Evaluating kernel against reference code")
    # Evaluate kernel against reference code
    kernel_eval_result = evaluate_single_sample_src(
        ref_arch_src=ref_arch_src,
        kernel_src=kernel_src,
        configs=config.to_dict(),
        device=device,
    )
    kernel_exec_time = kernel_eval_result.runtime

    # Measure baseline time
    print("[INFO] Measuring reference program time")
    # Default using PyTorch Eager here
    ref_time_eager_result = measure_program_time(
        ref_arch_name="Reference Program",
        ref_arch_src=ref_arch_src,
        num_trials=config.num_perf_trials,
        use_torch_compile=False,
        device=device,
    )
    ref_exec_eager_time = ref_time_eager_result.get("mean", None)

    # Measure Torch Compile time
    ref_time_compile_result = measure_program_time(
        ref_arch_name="Reference Program",
        ref_arch_src=ref_arch_src,
        num_trials=config.num_perf_trials,
        use_torch_compile=True,
        torch_compile_backend="inductor",
        torch_compile_options="default",
        device=device,
    )
    ref_exec_compile_time = ref_time_compile_result.get("mean", None)

    print("=" * 40)
    print(f"[Eval] Kernel eval result: {kernel_eval_result}")
    print("-" * 40)
    print(f"[Timing] PyTorch Reference Eager exec time: {ref_exec_eager_time} ms")
    print(f"[Timing] PyTorch Reference torch.compile time: {ref_exec_compile_time} ms")
    print(f"[Timing] Custom Kernel exec time: {kernel_exec_time} ms")
    print("-" * 40)

    if kernel_eval_result.correctness:
        print(
            f"[Speedup] Speedup over eager: {ref_exec_eager_time / kernel_exec_time:.2f}x"
        )
        print(
            f"[Speedup] Speedup over torch.compile: {ref_exec_compile_time / kernel_exec_time:.2f}x"
        )
    else:
        print("[Speedup] Speedup Not Available as Kernel did not pass correctness")

    print("=" * 40)


if __name__ == "__main__":
    main()

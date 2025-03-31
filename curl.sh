curl -X POST "https://tcapelle--kernel-benchmark-server-benchmarkservice-fastapi-app.modal.run/benchmark" \
  -F "ref_file=@src/prompts/model_ex_1.py" \
  -F "kernel_file=@src/prompts/model_new_ex_1.py" \
  -F "num_correct_trials=5" \
  -F "num_perf_trials=100" \
  -F "verbose=false" | python -m json.tool

from tools import load_test_cases, save_to_file
from tqdm import tqdm
from pathlib import Path


def generate_results(model, run_inference):
    tests = load_test_cases()
    results = []
    for test in tqdm(tests):
        outputs = []
        results.append({"task_id": test["task_id"], "outputs": outputs})
        for iteration in range(3):
            changes = run_inference("../llm-devops-eval", test)
            outputs.append(changes.model_dump())
            results[-1]["outputs"] = outputs
            save_to_file(model, results)

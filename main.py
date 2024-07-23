from inference import run_inference
from tools import load_test_cases, get_results, create_prompt, save_to_file
from evaluation import evaluate, summarize_score
import os, sys, json
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()

if sys.argv[1] == "generate":
    assert "/" in sys.argv[2], "model name should be of the format openai/gpt-35-turbo-1106"
    model = sys.argv[2]
    tests = load_test_cases()
    results = []

    for test in tqdm(tests):
        outputs = []
        results.append({"task_id": test["task_id"], "outputs": outputs})
        prompt = create_prompt(test)
        for iteration in range(3):
            changes = run_inference(sys.argv[2], prompt)
            outputs.append(changes.model_dump())
            results[-1]["outputs"] = outputs
            save_to_file(model, results)

if sys.argv[1] == "evaluate":
    assert "/" in sys.argv[2], "model name should be of the format openai/gpt-35-turbo-1106"
    results = get_results(sys.argv[2])
    tests = load_test_cases()

    scores = []
    for test in tqdm(tests):
        scores.append(evaluate(test, results))
    summarize_score(scores)

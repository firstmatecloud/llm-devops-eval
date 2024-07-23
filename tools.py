import os, json
from glob import glob
from pathlib import Path

def load_test_cases():
    test_cases = []
    for file in glob("dataset/*.json"):
        with open(file, "r") as fp:
            test_cases += json.load(fp)
    return test_cases


def get_results(model):
    model = model.split("/")[1]
    assert os.path.exists(os.path.join("results", model + ".json"))
    with open(os.path.join("results", model + ".json"), "r") as fp:
        results = json.load(fp)
    return results


def create_prompt(test_case):
    repo = repo_to_string(os.path.join("code", test_case["source"]))
    return f"Issue:\n{test_case['prompt']}\n\nRepo structure:\n{repo}"


def save_to_file(model, result):
    with open("results/" + model.split("/")[1] + ".json", "w") as fp:
        json.dump(result, fp)


def summarize_repo(path: str):
    overview = ""
    file_list = []
    for root, dirs, files in os.walk(path):
        base = root[len(path):]
        if ".git" in root:
            continue
        level = root.replace(path, '').count(os.sep)
        indent = '|  ' * (level)
        overview += '{}{}/\n'.format(indent, os.path.basename(root))
        for f in files:
            overview += '{}{}\n'.format(indent + "|- ", f)
            try:
                with open(os.path.join(root, f), "r") as fp:
                    content = fp.read()
                file_list.append(f"\n\n-- {os.path.join(base, f)} --\n<content>\n{content}\n</content>")
            except UnicodeDecodeError:
                pass
    return overview, file_list


def repo_to_string(path):
    tree, file_list = summarize_repo(path)
    result = tree + "\n\nContent of all files:"
    for file in file_list:
        result += file
    return result


def edit_file(path, file):
    path = os.path.join(path, file["file_path"][1:])
    print(path)
    if file["mode"] == "overwrite":
        assert os.path.exists(path)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fp:
            fp.write(file["changes"][0]["changed_snippet"])
    elif file["mode"] == "create":
        assert not os.path.exists(path)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fp:
            fp.write(file["changes"][0]["changed_snippet"])
    else:
        try:
            with open(path, "r") as fp:
                content = fp.read()
        except FileNotFoundError:
            print(f"File does not exist ({file['file_path']})")
            return False
        for change in file["changes"]:
            if change["original_snippet"] in content:
                content = content.replace(change["original_snippet"], change["changed_snippet"], 1)
            elif abs(len(change["original_snippet"]) - len(content)) < 3:
                content = change["changed_snippet"]
            else:
                print("WARNING: Original snippet not found")
                return False
        with open(path, "w") as fp:
            fp.write(content)
    return True

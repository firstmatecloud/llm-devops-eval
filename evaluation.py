import os, json, shutil
from tools import edit_file
import subprocess
from inference import run_ice_prompt, Changes


def criteria_file_exists(changes: dict, test):
    exists = []
    for file in changes["file_to_change"]:
        fpath = file["file_path"][1:] if file["file_path"].startswith("/") else file["file_path"]
        path = os.path.join("code", test["source"], fpath)
        if file['mode'] != "create":
            exists.append(os.path.exists(path))
        else:
            exists.append(not os.path.exists(path))
    return round(sum(exists) / (len(exists) + 10e-10), 3)


def criteria_change(changes: dict, test):
    exists = []
    file_changes = ""
    for file in changes["file_to_change"]:
        path = os.path.join("code", test["source"], file["file_path"][1:])
        content = ""
        if file["mode"] == "change" and not os.path.exists(path):
            exists.append(False)
            continue
        if file["mode"] == "overwrite" and not os.path.exists(path):
            exists.append(False)
            continue
        if file["mode"] == "create" and os.path.exists(path):
            exists.append(False)
            continue
        file_changes += f"--- {file['mode']} ---\n"
        if file["mode"] == "change":
            with open(path, "r") as fp:
                content = fp.read()
        for change in file["changes"]:
            exists.append(change["original_snippet"] in content)
    return round(sum(exists) / (len(exists) + 10e-10), 3)


def criteria_execute(changes: dict, test):
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    shutil.copytree(os.path.join("code", test["source"]), "temp")
    for file in changes["file_to_change"]:
        status_ok = edit_file("temp", file)
        if not status_ok:
            return 0
    try:
        subprocess.run("cd temp; terraform init -backend=false", shell=True, check=True)
        subprocess.run("terraform validate", shell=True, check=True)
        return 1
    except subprocess.CalledProcessError:
        return 0


def criteria_ice(changes: dict, test):
    useful = run_ice_prompt("azure/gpt-35-turbo-1106", "usefulness", test["prompt"], str(Changes.parse_obj(changes)))
    functional = run_ice_prompt("azure/gpt-35-turbo-1106", "functional correctness", test["prompt"],
                                str(Changes.parse_obj(changes)))
    score = (useful + functional) / 8
    return score


class Run:
    def __init__(self, result, test):
        self.ice = criteria_ice(result, test)
        self.execute = criteria_execute(result, test)
        self.file_exists = criteria_file_exists(result, test)
        self.snippet_exists = criteria_change(result, test)


class Score:

    def __init__(self, test):
        self.test = test
        self.runs = []

    def add_run(self, result, test):
        self.runs.append(Run(result, test))

    def as_dict(self):
        return {"files_exist": sum(run.file_exists for run in self.runs) / len(self.runs),
                "edit_exists": sum(run.snippet_exists for run in self.runs) / len(self.runs),
                "execution": sum(run.execute for run in self.runs) / len(self.runs),
                "ice": sum(run.ice for run in self.runs) / len(self.runs)}

    def __str__(self):
        r = f"---\nfile_exists: {sum(run.file_exists for run in self.runs) / len(self.runs)}\n" \
            f"snippet exists: {sum(run.snippet_exists for run in self.runs) / len(self.runs)}\n" \
            f"can be executed: {sum(run.execute for run in self.runs) / len(self.runs)}\n" \
            f"ICE score: {sum(run.ice for run in self.runs) / len(self.runs)}\n"
        return r


def summarize_score(scores: list[Score]):
    criteria = {}
    for score in scores:
        if not score:
            continue
        for key, value in score.as_dict().items():
            if key not in criteria:
                criteria[key] = [value]
            else:
                criteria[key].append(value)
    for category, scores in criteria.items():
        print(f"{category}: {round(sum(scores) / len(scores), 3)}")


def evaluate(test: dict, results: list):
    score = Score(test)
    for r in results:
        if r["task_id"] == test["task_id"]:
            for output in r["outputs"]:
                score.add_run(output, test)
            print(score.test)
            return score
    else:
        return None

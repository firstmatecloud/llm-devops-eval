import instructor
from litellm import completion
from pydantic import BaseModel, Field
from enum import Enum
import yaml
from dotenv import load_dotenv
from llm_code_eval import utils as ice

load_dotenv()


class Score(BaseModel):
    score: int = Field()


class FileMode(str, Enum):
    create = "create"
    overwrite = "overwrite"
    change = "change"


class SnippetChange(BaseModel):
    original_snippet: str = Field(
        description="Empty in case of 'create' file mode. Otherwise: exact copy of the part of code you want to edit"
                    " (at least two lines, include correct spacing and indents like in the given source code).")
    changed_snippet: str = Field(
        description="Your changes on this piece of code. We will replace the original snippet by your updated snippet.")


class File(BaseModel):
    file_path: str = Field(
        description="Exact path of the file we need to change. Use the path structure like defined between '--',"
                    " starting with / and excluding the repo name.")
    mode: FileMode = Field(
        description="File mode should be in:\n'change': change snippets in existing file. \n 'overwrite': "
                    "change content of existing file completely. \n 'create': create new file.")
    changes: list[SnippetChange] = Field(
        description="Non-empty list of changes needed. Every SnippetChange should have changed_snippet code.")


class Changes(BaseModel):
    file_to_change: list[File] = Field(
        description="List of files to change. Keep empty if its not worth it to change anything.")

    def __str__(self):
        result = ""
        for f in self.file_to_change:
            result += f"\n{f.file_path}\n"
            for change in f.changes:
                result += f"\n--- source\n{change.original_snippet}\n\n--- changed\n{change.changed_snippet}---\n"
        return result


# Load configuration
def load_config(config_path: str = "config/config.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


# Get model based on the configuration
def get_model(config):
    return config['provider_name'] + "/" + config['model_name']


client = instructor.from_litellm(completion)


class User(BaseModel):
    name: str
    age: int


def run_inference(model, user):
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an experienced cloud/devops engineer. "
                           "Generate yhe necessary changes to solve this issue.",
            },
            {
                "role": "user",
                "content": user,
            }
        ],
        response_model=Changes,
    )
    return resp


def run_ice_prompt(model, aspect, problem, output):
    prompt = ice.TASK_PROMPTS["code-gen"][aspect]["reference-free"]
    prompt = prompt.replace("{{PROBLEM}}", problem).replace("{{OUTPUT}}", output)
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": prompt,
            }
        ],
        response_model=Score,
    )
    return resp.score

# 🤖 LLM testing repo for devops tasks

This repo was created by [FirstMate - DevOps LLM Agent](https://firstmate.cloud) because we did not find any proper datasets to evaluate code-generation on DevOps tasks.
The goal is to evaluate end-to-end capabilities: the generation of a correctly formatted commit (file changes based on snippets) on infra-as-code repositories, dockerfiles and CI/CD pipelines.

We also want to make clear that building an elaborate agent with multiple phases can provide better and ready-to-use results than using a 


## 🧪 Pass@1 Results on DevOps code-generation tasks

🕙 Last updated on 01.08.2023

| Model          | Commit creation | Executable | ICE Score |
|----------------|-----------------|------------|-----------|
| gpt-35-1106    | .830            | .519       | .870      |
| gpt-4o         | .907            | .704       | .921      |
| FirstMate v1.1 | .974            | .815       | .986      |


FirstMate uses tool calling and multiple prompting layers including code-planning to create high quality code.
We FirstMate is used in real git environments, we use multiple retries & communicate with git pipelines to improve results even further.
In this case we disabled this feature to get fair insights in the capabilities (Pass@1).

FirstMate uses gpt-3.5 and gpt-4o in multiple stages.

<br>

## ✅ Used Test Cases

All used test-cases can be found in the dataset repo.
The prompts defined in these test-cases are used to generate 1 commit a infra repository.
We use our own example repos which are linked as git submodules in this repo in directory `code`

Linked repo's:

➡️ `example-terraform` : https://github.com/firstmatecloud/example-terraform

## Evaluation Metrics

We evaluate LLM generated commits in multiple ways.

- **Commit Creation:**  
Do the generated source snippets exist, so they can be correctly altered?

- **Executable:**  
Use commands like `terraform validate` to validate code correctness.

- **ICE score:**  
Mean of the 'Usefullness' and 'Functional correctness' score described in this paper:
https://arxiv.org/pdf/2304.14317
The authors propose a way to use LLM models to evaluate code generation and prove the correlation with human-evaluated
scoring.

Terraform example repo

https://github.com/futurice/terraform-examples/tree/master/azure/azure_linux_docker_app_service

firstmate usage
{'gpt-35-turbo-1106': {'prompt_tokens': 220025, 'completion_tokens': 12128, 'cost': 0.1282045}, 'gpt-4o': {'prompt_tokens': 107755, 'completion_tokens': 40027, 'cost': 1.13918}}

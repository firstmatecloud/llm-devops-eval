# 🤖 LLM testing repo for devops tasks

## 🧪 Results

🕙 Last updated on 23.07.2023

| Model       | Commit creation | Executable | ICE Score |
|-------------|-----------------|------------|-----------|
| gpt-35-1106 | .830            | .519       | .870      |
| gpt-4o      | .932            | .704       | .921      |
| FirstMate   |                 |            |           |


FirstMate uses tool calling and multiple prompting layers including code-planning to create high quality.
In production we use multiple retries after validating code using `terraform validate`, `docker build`etc. 
In this case we disabled this feature to get fair insights in the capabilities.

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



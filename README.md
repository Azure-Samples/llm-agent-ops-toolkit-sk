# LLMAgentOps Toolkit

`LLMAgentOps` Toolkit is repository that contains basic structure of LLM Agent based application built on top of the Semantic Kernel. The toolkit is designed to be a starting point for data scientists and developers for experimentation to evaluation and finally deploy to production their own LLM Agent based applications.

The sample is implemented the concept of `StateFlow` (a Finite State Machine FSM based LLM workflow) using [Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/overview/) agents - [StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows](https://arxiv.org/abs/2403.11322)

## Architecture

## Core Concepts

## Experimentation

[Experimentation](experimentation/README.md) is the process of testing a hypothesis or a proposed LLM Agents based solution to a problem.

## Evaluation

[Evaluation](evaluation/README.md) is the process of evaluating the performance of the LLM Agents based solution.

## Engineering Fundamentals

### Local Linting

```bash
conda activate base
pylint src
```

### Local Unit Testing

```bash
conda activate base
python -m unittest discover -s tests
```

Get the test coverage report:

```bash
pip install coverage
python -m coverage run --source src -m unittest discover -s tests
python -m coverage report -m
```

### Local Functional Testing (Docker)

```bash
cp env_docker .env_docker # only once and update the values
docker build --rm -t stateflow-semantic-kernel-api:latest .
docker run -d --link mysql_server:mysql-local --name StateFlowApiSemanticKernel -p 8085:8000 --env-file .env_docker stateflow-semantic-kernel-api:latest
```

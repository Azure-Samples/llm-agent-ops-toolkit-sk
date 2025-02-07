# LLMAgentOps Toolkit (Semantic Kernel)

`LLMAgentOps` Toolkit is repository that contains basic structure of LLM Agent based application built on top of the Semantic Kernel. The toolkit is designed to be a starting point for data scientists and developers for experimentation to evaluation and finally deploy to production their own LLM Agent based applications.

The sample `MySql Copilot` has been implemented using the concept of `StateFlow` (a Finite State Machine FSM based LLM workflow) using [Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/overview/) agents - [StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows](https://arxiv.org/abs/2403.11322).

This toolkit can be used by replacing the `MySql Copilot` with any other LLM Agent based solution or it can be enhanced for a specific use case.

## Architecture

The `LLMAgentOps` Architecture is based on the following components:

- `LLM Selection`: Selecting the right LLM for LLM Agent based solution for the problem.
- `Agent Architecture`: Designing the agent architecture for the LLM Agent based solution. For this sample we have used `Semantic Kernel` development kit by using `Python` programming language.
- `Experimentation & Evaluation`: Experimentation and Evaluation of the LLM Agent based solution. Where the experimentation is done using `console` or `ui` or in `batch` mode and evaluation is done using `LLM as Judge` and `Human Evaluation`.
- `CI CE and CD`: Continuous Integration, Continuous Evaluation and Continuous Deployment of the LLM Agent based solution.
- `Deployment`: Deployment of the LLM Agent based solution in `local` or `cloud` environment.
- `Monitoring`: Monitoring the LLM Agent based solution for performance and other metrics.

## Key Features

This repository is having the follow key features:

- **Source Code Structure**: The [source code](./src/) is structured in such a way that it can be easily developed and maintained by data scientists and developers together with following key concepts:
    - **Agents Base Class**: The [base class](./src/agents/base.py) for the agents.
    - **Agents**: All of the [agents](./src/agents/) with their specific prompts and descriptions. Example: [Observe Agent](./src/agents/observe.py).
    - **Code Execute Agent**: The [code execute agent](./src/agents/execute.py) is an agent that can join the group of agents but it will execute the code (in this sample it is SQL queries) and return the result, instead of using LLM for generating response like other agents.
    - **Group Chat Selection Logic**: The [group chat selection logic](./src/groupchat/state_flow_selection_strategy.py) is used to select the appropriate next agent based on the current state of the conversation. In this sample the concept of `StateFlow` is used for the selection of the next agent.
    - **Group Chat Termination Logic**: The [group chat termination logic](./src/groupchat/state_flow_termination_strategy.py) is used to terminate the conversation based on the current state of the conversation or maximum number of turns. In this sample the concept of `StateFlow` is used for the termination of the conversation.
    - **Group Chat**: The [group chat](./src/groupchat/state_flow_chat) contains the group chat client that can serve the conversation between the user and the agents.
    - **Operational Code (Ops)**: There are few operational code that can is used in the agents:
        - Observability Code: The [observability code](./src/logging) contains the code for logging and monitoring the agents. In this sample `OpenTelemetry` is used for logging and monitoring.
        - MySql Interaction Code: The [MySql interaction code](./src/mysql/execution_env.py) contains the code for interacting with MySql database.
    - **Deployment Code**: The[deployment code contains the code for deploying the agents in local or cloud environment. In this sample the code is provided for deploying the agents in Azure Web App Service. The deployment code will be:
        - [Source Module](./src/): core implementation of the agents and group chat.
        - [REST API Based App](./app_rest_api.py): REST API based app for calling the agents and getting the response (in this example it's `FastAPI`).
        - [Dockefile](./Dockerfile): Dockerfile for building the image of the entire application.
        - [Requirements](./requirements.txt) file for the dependencies.
- **Experimentation**: The [experimentation](./experimentation/) setup by using `console` or `ui` or in `batch` mode.
- **Evaluation**: The [evaluation](./evaluation/) setup by using `LLM as Judge` and `Human Evaluation`.
- **Engineering Fundamentals**: The [engineering fundamentals](#engineering-fundamentals) for the development and maintenance of the LLM Agent based solution.
- **CI CE and CD**: The [CI CE and CD](./.github/workflows/) setup for the continuous integration, continuous evaluation and continuous deployment of the LLM Agent based solution.

## Getting Started

### Pre-requisites

- [Visual Studio Code](https://code.visualstudio.com/) with [Dev Containers](https://code.visualstudio.com/docs/remote/containers) extension.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- [Azure AI Foundry Service](https://learn.microsoft.com/en-us/azure/ai-studio/what-is-ai-studio).
- [Azure OpenAI Chat Model](https://learn.microsoft.com/en-us/azure/ai-studio/quickstarts/get-started-playground#deploy-a-chat-model).
- [Azure Web App Service](https://learn.microsoft.com/en-us/azure/app-service/overview) (needed only for CD).
- [Azure Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) (needed only for CD).

### Experimentation

[Experimentation](experimentation/README.md) is the process of designing the agents and testing a hypothesis or a proposed LLM Agents based solution to a problem.

### Evaluation

[Evaluation](evaluation/README.md) is the process of evaluating the performance of the LLM Agents based solution.

### Engineering Fundamentals

#### CI CE and CD

The repository is setup with [CI CE and CD](.github/workflows/) for the continuous integration, continuous evaluation and continuous deployment of the LLM Agent based solution.

- **CI**: The [CI](.github/workflows/ci.yml) workflow is triggered on every push or pull request to the repository. The CI workflow will run the unit tests and linting checks.
- **CE**: The [CE](.github/workflows/ce.yml) workflow is triggered manually. The CE workflow will run the batch experimentation and batch evaluation (LLM as Judge).
- **CD**: The [CD](.github/workflows/cd.yml) workflow is triggered manually. The CD workflow will deploy the LLM Agent based solution to the Azure Web App Service.

#### Dev Containers

The repository is setup with [Dev Containers](https://code.visualstudio.com/docs/remote/containers) for development and testing.

#### Local Linting

```bash
conda activate base
pylint src
```

#### Local Unit Testing

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

#### Local Functional Testing (Docker)

```bash
cp env_docker .env_docker # only once and update the values
docker build --rm -t stateflow-semantic-kernel-api:latest .
docker run -d --link mysql_server:mysql-local --name StateFlowApiSemanticKernel -p 8085:8000 --env-file .env_docker stateflow-semantic-kernel-api:latest
```

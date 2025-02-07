# Experimentation

For this sample repository, we will demonstrate the experimentation process for MySqlCopilot, a LLM Agents based solution to retrieve data from a MySQL database using a conversational interface.

## Problem Definition

The problem statement is to retrieve data from a MySQL database using a conversational interface. The hypothesis is that a LLM Agents based solution can be used to retrieve data from a MySQL database using a conversational interface.

## Data Collection

The data collection process involves understanding the data schema of the MySQL database and the data retrieval requirements. For this sample repository, we will use the following data schema from [MySql Sample Database](https://www.mysqltutorial.org/getting-started-with-mysql/mysql-sample-database/)

![Database Schema](https://www.mysqltutorial.org/wp-content/uploads/2023/10/mysql-sample-database.png)

Sample questions that can be asked to retrieve data from the MySQL database:

- Total number of products
- Total number of customers
- Total Sales value so far
- Total number of orders
- Top 5 products by sales
- How many employees are there in the company
- How many employees are placing orders

## LLM Agent Design

The LLM Agent design involves creating a conversational interface to interact with the MySQL database. The LLM Agent will process the user input, generate SQL queries, execute the queries on the MySQL database, and return the results to the user.

To implement this we will use the concept of [StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows](https://arxiv.org/abs/2403.11322) and [Semantic Kernel Agent Framework](learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/?pivots=programming-language-python).

StateFlow is a Finite State Machine (FSM) based workflow that defines the states and transitions of the LLM Agent. The Semantic Kernel Agent Framework provides the infrastructure to build custom agents using the StateFlow workflow.

![LLM Agent Design](https://microsoft.github.io/autogen/0.2/assets/images/intercode-fd9f091f97c91e13a58232ebc9dca4e6.png)
*source: [StateFlow - Build State-Driven Workflows with Customized Speaker Selection in GroupChat](https://microsoft.github.io/autogen/0.2/blog/2024/02/29/StateFlow/)*

The agents will be designed to handle the following tasks:

- `init`: The initial LLM Agent state to start the conversation.
- `observe`: The state to observe the user input and generate SQL queries.
- `select`: The state to construct the SQL query based on the user input.
- `verify`: The state to verify if the results are correct.
- `error`: The state to handle any SQL errors during the conversation and construct an appropriate query.
- `execute`: The state to execute the SQL query on the MySQL database.

## Experimentation Process

The experimentation can be done using `Console` or `Chainlit based UI` or in `Batch` for the LLM Agents based solution. The user can interact with the LLM Agent using a conversational interface to retrieve data from the MySQL database.

The experimentation process involves the following steps:

### 1. Local MySQL Database Setup

If you have a MySql existing setup on which you would like to run the experiment, you can skip this step.

If you do not have a MySQL database setup, you can use the [Steps for setting up local MySql](./data/local_mysql/) to set up a local MySQL database using Docker.

### 2. Create the `.env` file

Create a `.env` file in the `experimentation` directory by filling the values as given in the [env_template](./env_template) file.

### 2. Experimentation with Console

The `Console` based experimentation involves running the LLM Agent in the console and interacting with it using a text-based interface.

**Note**: The console based experimentation is for initial `exploration` stage and does not store any data for evaluation.

To run the LLM Agent in the console, follow the steps:

```bash
conda activate experimentation
cd experimentation
python app_experiment_console.py
```

### 3. Experimentation with UI

The `Chainlit UI` based experimentation involves running the LLM Agent with a UI interface and interacting with it using a conversational interface. The Chainlit UI provides a more interactive and user-friendly experience for the LLM Agents based solution. It not only stores the conversation data for evaluation but also provides a way to provide `Human Feedback` for the overall conversation and individual agents.

**Note**: The UI based experimentation is `experiment` stage and it can be provided to `Human Evaluator` for feedback.

To run the LLM Agent with Chainlit UI, follow the steps:

```bash
conda activate experimentation
cd experimentation
chainlit run -w app_experiment_ui.py
```

The collected data can be viewed by opening the [sql_copilot.sqlite.db](./exp_src/persistence/sql_copilot.sqlite.db) file in a SQLite browser. This file will only be generated after you run the `python app_experiment_ui.py` command.

### 4. Experimentation in Batch

The `Batch` based experimentation involves running the LLM Agent in a batch mode to process a large number of queries and evaluate the performance of the LLM Agents based solution. The batch experimentation can be used to evaluate the accuracy, efficiency, and scalability of the LLM Agents based solution.

**Note**: The batch based experimentation is for `continuous evaluation` stage and it can be used to evaluate the performance of the LLM Agents based solution.

To run the LLM Agent in batch mode, follow the steps:

```bash
conda activate experimentation
cd experimentation
python app_experiment_batch.py data/batch_input/queries.jsonl ../evaluation/.evaluation_input_data_batch/ "SQL Copilot Batch Experiment"
```

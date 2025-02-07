# Evaluation

For this sample repository, we will demonstrate the evaluation process for MySqlCopilot, a LLM Agents based solution to retrieve data from a MySQL database using a conversational interface.

## Human Evaluation

The `Human Evaluation` is the process of evaluating the performance of the LLM Agents based solution by providing the conversational interface to the `Human Evaluator`. The `Human Evaluator` will interact with the LLM Agents using a conversational interface and provide feedback on the overall conversation and individual agents.

This can be achieved by running the experiment in the UI mode and providing the `Chainlit UI` based interface to the `Human Evaluator`. For mode details, refer to the [Experimentation](../experimentation/README.md) section.

The collected data can be viewed by opening the [sql_copilot.sqlite.db](./exp_src/persistence/sql_copilot.sqlite.db) file in a SQLite browser. If you would like view the data programmatically, you can use the following code snippet:

```python
import pandas as pd
from sqlalchemy import create_engine

df_steps = pd.read_sql_table('steps', create_engine("path to sql_copilot.sqlite.db"))
df_feedbacks = pd.read_sql_table('feedbacks', engine("path to sql_copilot.sqlite.db"))

human_feedback_data = pd.merge(df_steps, df_feedbacks, left_on='id', right_on='forId')
```

## LLM as Judge

The `LLM as Judge` is the process of evaluating the performance of the LLM Agents using another LLM Agent as a judge. For this evaluations `Azure AI Foundry Service` can be used. For more details, refer to the [documentation](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/evaluate-sdk).

This can be achieved by running the experiment in the batch mode. For mode details, refer to the [Experimentation](../experimentation/README.md) section. This step will generate evaluation dataset for each agent in the [.evaluation_input_data_batch](./.evaluation_input_data_batch/) directory.

The evaluation dataset can be evaluated using the `Azure AI Foundry Service` by following the steps:

- Create a `.env` file in the `evaluation` directory by filling the values as given in the [env_template](./env_template) file.
- Run the following command to evaluate the performance of the LLM Agents based solution:

```bash
conda activate evaluation
cd evaluation
python run_azure_ai_foundry_local_eval.py <evaluation agent name> <evaluation agent dataset path>
# Example: python run_azure_ai_foundry_local_eval.py "observe" ".evaluation_input_data_batch/observe.jsonl"
```

## Analyze Results

The results of the evaluation can be analyzed by comparing the performance of the LLM Agents based solution with the `Human Evaluator` feedback and the `LLM as Judge` evaluation. The results can be used to improve the performance of the LLM Agents based solution by providing feedback to the agents and retraining them.

## End to End Sample

For an end to end sample of the evaluation process, refer to the [Result Analysis Notebook](./Result_Analysis.ipynb).

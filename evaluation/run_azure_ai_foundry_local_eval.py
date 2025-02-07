import os
import sys
import uuid
import pandas as pd
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import evaluate, GroundednessEvaluator
from dotenv import load_dotenv

load_dotenv(override=True)

project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"],
    credential=DefaultAzureCredential(),
)
connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=True
)
evaluator_model = {
    "azure_endpoint": connection.endpoint_url,
    "azure_deployment": os.environ["EVALUATION_MODEL"],
    "api_version": "2024-08-01-preview",
    "api_key": connection.key,
}

groundedness = GroundednessEvaluator(evaluator_model)

output_path = "./.evaluation_output_data"
if not os.path.exists(output_path):
    os.makedirs(output_path)


def mock_target_function(input):
    return input


if __name__ == "__main__":
    # workaround for multiprocessing issue on linux
    from pprint import pprint
    from pathlib import Path
    import multiprocessing
    import contextlib

    with contextlib.suppress(RuntimeError):
        multiprocessing.set_start_method("spawn", force=True)

    if len(sys.argv) < 3:
        raise ValueError(
            "Please provide an evaluation name and a data file to evaluate, usage: python run_azure_ai_foundry_local_eval.py <evaluation_name> <input_data_file>"
        )
    evaluation_name = sys.argv[1]
    data_file_path = sys.argv[2]
    data_file_name = os.path.basename(data_file_path).replace(
        ".jsonl", f".{str(uuid.uuid4())}.jsonl"
    )
    print(f"Running evaluation for {evaluation_name} on {data_file_path}")

    evaluators = {}
    evaluators["groundedness"] = groundedness

    result = evaluate(
        data=Path(data_file_path),
        evaluation_name=evaluation_name,
        evaluators=evaluators,
        evaluator_config={
            "groundedness": {
                "column_mapping": {
                    "query": "${data.input}",
                    "response": "${data.output}",
                    "context": "${data.conversation_history}",
                }
            }
        },
        output_path=Path(output_path) / data_file_name,
    )

    tabular_result = pd.DataFrame(result.get("rows"))

    pprint("-----Summarized Metrics-----")
    pprint(result["metrics"])
    pprint("-----Tabular Result-----")
    pprint(tabular_result)
    pprint(f"View evaluation results in AI Studio: {result['studio_url']}")

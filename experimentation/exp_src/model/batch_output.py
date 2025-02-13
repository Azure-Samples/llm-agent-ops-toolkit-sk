from uuid import uuid4


class BatchOutput:
    def __init__(self, role: str, name: str, threadId: str, parentId: str,
                 input: str, output: str, conversation_history: str, experiment: str):
        self.id = str(uuid4())
        self.role = role
        self.name = name
        self.threadId = threadId
        self.parentId = parentId
        self.input = input
        self.output = output
        self.conversation_history = conversation_history
        self.experiment = experiment

    def to_dict_without_role(self):
        return {
            "experiment": self.experiment,
            "id": self.id,
            "name": self.name,
            "threadId": self.threadId,
            "parentId": self.parentId,
            "input": self.input,
            "output": self.output,
            "conversation_history": self.conversation_history
        }

class AgentInvokingData:
    def __init__(self, name: str, conversation_history: str):
        self.name = name
        self.conversation_history = conversation_history
    
    def to_dict(self):
        return {
            "name": self.name,
            "conversation_history": self.conversation_history
        }

class AgentInvokingTrajectory:
    def __init__(self, experiment: str, threadId: str, input: str, final_output: str,
                 agent_selections: list[AgentInvokingData]):
        self.agent_selections = agent_selections
        self.experiment = experiment
        self.threadId = threadId
        self.input = input
        self.final_output = final_output
        self.id = str(uuid4())

    def to_dict(self):
        return {
            "experiment": self.experiment,
            "id": self.id,
            "threadId": self.threadId,
            "input": self.input,
            "final_output": self.final_output,
            "agent_selections": [agent.to_dict() for agent in self.agent_selections]
        }
    
    def to_flattened_dict(self) -> list[dict]:
        """
        Flatten the agent selection data to a list of dictionaries. Which can be used for easy evaluation in Azure AI Foundry.
        """
        return [
            {
                "experiment": self.experiment,
                "id": self.id,
                "threadId": self.threadId,
                "input": self.input,
                "final_output": self.final_output,
                "selected_agent": agent.name,
                "conversation_history": agent.conversation_history
            }
            for agent in self.agent_selections
        ]

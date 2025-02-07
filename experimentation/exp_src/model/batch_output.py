from uuid import uuid4


class BatchOutput:
    id: str = str(uuid4())
    
    def __init__(self, role: str, name: str, threadId: str, parentId: str,
                 input: str, output: str, conversation_history: str, experiment: str):
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


from openai import AsyncOpenAI
from typing import Any, Dict, List
from dataclasses import dataclass

class Agent:
    def __init__(self, name: str, instructions: str, output_type: Any, model: Any):
        self.name = name
        self.instructions = instructions
        self.output_type = output_type
        self.model = model

class Runner:
    @staticmethod
    async def run(agent: "Agent", input: Any) -> Any:
        return await agent.model.run(agent.instructions, input)

class OpenAIChatCompletionsModel:
    def __init__(self, model: str, openai_client: Any):
        self.model = model
        self.client = openai_client

    async def run(self, instructions: str, input: Any):
        return DummyAgentResponse()

@dataclass
class RunConfig:
    model: Any
    model_provider: Any
    tracing_disabled: bool = True


class DummyAgentResponse:
    @property
    def final_output(self):
        return type('obj', (object,), {
            'queries': ["dummy query 1", "dummy query 2"],
            'thought': "dummy thought process"
        })()

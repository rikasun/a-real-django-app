from typing import Dict


class EchoTool:
    """A simple tool that echoes back the input"""

    name = "echo"
    description = "A simple tool that echoes back the input"
    inputs = [
        {
            "name": "message",
            "variable_type": "string",
            "description": "The message to echo back",
        }
    ]
    output_schema = {"echo": "string"}

    def __init__(self, env: Dict[str, str]):
        """Initialize with environment variables"""
        self.env = env

    def __call__(self, message: str) -> Dict[str, str]:
        """Echo back the input message"""
        return {"echo": message}

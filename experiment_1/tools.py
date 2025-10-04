import random


def calculate_random_number() -> float:
    """Generate a random number between 0 and 1."""
    return random.random()


def calculate_magic_number(a: float, b: float, c: float) -> float:
    """Calculate a magic number based on three floats."""
    return (a - b) / (a + b) + c


def handle_tool_call(name, **kwargs) -> str:
    try:
        if name == "calculate_random_number":
            nr = calculate_random_number()
            return f"Random number: {nr}"

        elif name == "calculate_magic_number":
            magic_number = calculate_magic_number(**kwargs)
            return f"Magic number: {magic_number}"

        raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return f"Error handling tool call: {e}"


TOOLS = [
    {
        "name": "calculate_random_number",
        "description": "Calculates a random number between 0 and 1",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "calculate_magic_number",
        "description": "Calculates a magic number based on three floats",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "c": {"type": "number"},
            },
            "required": ["a", "b", "c"],
        },
    },
]

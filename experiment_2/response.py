from typing import List


class OllamaStreamingResponse:
    def __init__(self, response: dict):
        self.response = response
        self._tool_calls = response.get("message", {}).get("tool_calls") or []
        self._content = response.get("message", {}).get("content", "")

    def has_tool_calls(self) -> bool:
        return len(self._tool_calls) > 0

    def tools_list(self) -> List[tuple[str, dict]]:
        return [
            (tool_call["function"]["name"], tool_call["function"]["arguments"])
            for tool_call in self._tool_calls
        ]

    def content(self) -> str:
        return self._content

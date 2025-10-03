from ollama import ChatResponse


class OllamaStreamingResponse:
    def __init__(self, response: ChatResponse):
        self.response = response
        self._tool_calls = response.message.tool_calls
        self._content = response.message.content

    def has_tool_calls(self) -> bool:
        if not self._tool_calls:
            return False
        return len(self._tool_calls) > 0

    def tools_list(self):
        return [
            (tool_call["function"]["name"], tool_call["function"]["arguments"])
            for tool_call in self._tool_calls
        ]

    def content(self) -> str | None:
        return self._content

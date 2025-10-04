import pytest


def parse_stream(response):
    tool_uses = []
    for item in response:
        if (
            item.get("type") == "content_block_start"
            and item.get("content_block", {}).get("type") == "tool_use"
        ):
            tool_name = item["content_block"]["name"]

            # Collect the tool input by reconstructing the partial JSON deltas
            tool_input = {}
            input_json = ""

            # Find and concatenate input JSON deltas
            for sub_item in response[response.index(item) + 1 :]:
                if (
                    sub_item.get("type") == "content_block_delta"
                    and sub_item.get("delta", {}).get("type") == "input_json_delta"
                ):
                    input_json += sub_item["delta"].get("partial_json", "")

                if sub_item.get("type") == "content_block_stop":
                    break

            # Careful JSON parsing
            if input_json.strip():
                # Remove leading/trailing whitespaces and handle potential JSON parsing
                tool_input = eval(input_json.strip())

            tool_uses.append({"name": tool_name, "arguments": tool_input})

    return tool_uses


response = [
    {
        "type": "message_start",
        "message": {
            "id": "msg_014p7gG3wDgGV9EUtLvnow3U",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-5-20250929",
            "stop_sequence": None,
            "usage": {"input_tokens": 472, "output_tokens": 2},
            "content": [],
            "stop_reason": None,
        },
    },
    {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": ""},
    },
    {"type": "ping"},
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": "Okay"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": ","},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " let"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": "'s"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " check"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " the"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " weather"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " for"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " San"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " Francisco"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": ","},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": " CA"},
    },
    {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": ":"},
    },
    {"type": "content_block_stop", "index": 0},
    {
        "type": "content_block_start",
        "index": 1,
        "content_block": {
            "type": "tool_use",
            "id": "toolu_01T1x1fJ34qAmk2tNTrN7Up6",
            "name": "get_weather",
            "input": {},
        },
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": ""},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": '{"location":'},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": ' "San'},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": " Francisc"},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": "o,"},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": ' CA"'},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": ", "},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": '"unit": "fah'},
    },
    {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": 'renheit"}'},
    },
    {"type": "content_block_stop", "index": 1},
    {
        "type": "message_delta",
        "delta": {"stop_reason": "tool_use", "stop_sequence": None},
        "usage": {"output_tokens": 89},
    },
    {"type": "message_stop"},
]


def test_parse():
    expected = [
        {
            "name": "get_weather",
            "arguments": {"location": "San Francisco, CA", "unit": "fahrenheit"},
        }
    ]
    assert parse_stream(response) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])

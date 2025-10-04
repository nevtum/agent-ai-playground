system_prompt = """
You are an AI assistant that helps people calculate numbers. \
Describe the plan how you will answer the question then \
execute on that plan. Provide only the answer requested and \
nothing else.
"""

user_prompt = """
Calculate a magic number using a series of random numbers. \
In your final response, output only the calculation in json \
results similar to the following example:
{
    "result": 0.23626
}
"""

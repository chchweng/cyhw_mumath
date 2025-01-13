#%%
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI 
import docker
import re
from collections import Counter

# Function to generate reasoning (CoT) and corresponding Python code using OpenAI API

async def generate_reasoning_and_code(question: str) -> tuple:
    """
    Generate reasoning (CoT) and corresponding Python code for the question.
    """
    client = OpenAI(
        api_key="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"
    )

    # Chat-based completion
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a mathematical reasoning and Python coding expert. "
                    "You will solve mathematical questions step-by-step using Python code. "
                    "Follow this format:\n"
                    "1. Explain the approach in plain text.\n"
                    "2. Provide the Python code inside ```python ... ```.\n"
                    "3. Ensure the Python code outputs the result in this format: Final result: <number>\n"
                    "If debugging is required, include corrections and ensure the final format is followed."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Analyze the following question and provide step-by-step reasoning with Python code:\n"
                    f"\"{question}\"\n"
                    "Ensure that the Python code outputs the result using the format: Final result: <number>."
                )
            }
        ],
        max_tokens=1000,
        temperature=0.2  # Reduced randomness to ensure structured outputs
    )

    response_text = chat_completion.choices[0].message.content

    # Parsing reasoning and Python code block
    if "```python" in response_text:
        reasoning = response_text.split("```python")[0].strip()
        code = response_text.split("```python")[-1].split("```")[0].strip()
    else:
        reasoning = response_text
        code = "Error: No valid Python code block found."

    return reasoning, code

# Function to execute Python code in a Docker container
async def execute_and_debug_code(code: str) -> str:
    """
    Execute Python code in a Docker container. If errors occur, debug and retry.
    """
    client = docker.from_env()

    try:
        # Format the command to avoid multi-line issues
        command = f'python -c "{code.replace(chr(10), " ")}"'
        container = client.containers.run(
            "python:3.9",
            command,
            detach=False,
            stderr=True,
            stdout=True,
            remove=True
        )
        result = container.decode('utf-8').strip()

        # Parse the final result using the specified key
        if "Final result:" in result:
            return parse_output(result)
        else:
            return "Error: No final result format found."
    except Exception as e:
        debugged_code = debug_code(code, str(e))
        return await execute_and_debug_code(debugged_code)
    finally:
        client.close()


# Helper function to parse the output
def parse_output(output: str) -> str:
    """
    Extract the final result from the output using the format "Final result: <number>".
    """
    match = re.search(r'Final result: (\d+)', output)
    return match.group(1) if match else "Error: Could not parse the result."

# Function to use LLM for code debugging
def debug_code(code: str, error_message: str) -> str:
    """
    Use LLM to debug the given Python code based on the error message.
    """
    client = OpenAI(
        api_key="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", 
    )
    debug_prompt = f"The following code:\n{code}\nproduced an error:\n{error_message}\nPlease correct it."
    chat_completion = client.chat.completions.create(
        engine="gpt-4o-mini",
        prompt=debug_prompt,
        max_tokens=300,
        temperature=0.5
    )
    debugged_code = chat_completion.choices[0].text.strip()
    return debugged_code

# Function to perform majority voting
def majority_vote(results: list) -> str:
    """
    Perform majority voting on the results.
    """
    counter = Counter(results)
    return counter.most_common(1)[0][0]

# Main function to get the answer using prefix CoT, code execution, and debugging
async def get_answer(question: str, majority_num: int = 3) -> str:
    """
    Generate an answer for a given question using prefix CoT, code generation, 
    execution, debugging, and majority sampling.

    Args:
        question (str): The math question to solve.
        majority_num (int): Number of samples for majority voting.

    Returns:
        str: Final answer after majority sampling.
    """
    reasoning_and_code_tasks = [
        generate_reasoning_and_code(question) for _ in range(majority_num)
    ]

    results = await asyncio.gather(*reasoning_and_code_tasks)

    # Step 2: Extract and execute code
    execution_tasks = [
        execute_and_debug_code(code) for _, code in results
    ]

    execution_results = await asyncio.gather(*execution_tasks)

    # Step 3: Perform majority voting
    final_answer = majority_vote(execution_results)

    return final_answer

#%%
# Example usage
if __name__ == "__main__":
    question = "What is the smallest whole number that has a remainder of 1 when divided by 4, a remainder of 1 when divided by 3, and a remainder of 2 when divided by 5?"
    final_result = asyncio.run(get_answer(question, majority_num=2))
    print(f"Final Answer: {final_result}")

#%%

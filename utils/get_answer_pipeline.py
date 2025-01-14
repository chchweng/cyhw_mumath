#%%
import os
import asyncio
from openai import OpenAI 
import docker
import re
from collections import Counter
import json
import uuid
import subprocess

with open("api.json", "r") as f:
    config = json.load(f)
# Load API key from an environment variable
api_key = config["OPENAI_API_KEY"] 
#%%

# Function to generate reasoning (CoT) and corresponding Python code using OpenAI API
async def generate_reasoning_and_code(question: str) -> tuple:
    """
    Generate reasoning (CoT) and corresponding Python code for the question.
    """
    client = OpenAI(
        api_key=api_key
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
    Execute Python code in a Docker container using a local folder for the script.
    If an error occurs, debug and retry.
    """
    client = docker.from_env()

    try:
        # Generate a unique filename for the Python script
        script_name = script_name = f"/tmp/script_{uuid.uuid4().hex}.py"

        # Save the code to a temporary file
        with open(script_name, "w") as f:
            f.write(code)

        # Start the Docker container
        container = client.containers.run(
            "python:3.9",
            detach=True,
            tty=True
        )

        container_id = container.id

        # Copy the script into the container using `docker cp`
        subprocess.run(
            ["docker", "cp", script_name, f"{container_id}:/tmp/script.py"],
            stdout=subprocess.DEVNULL,  # Suppress stdout
            stderr=subprocess.DEVNULL,  # Suppress stderr
            check=True
        )

        # Execute the script inside the container
        exec_result = container.exec_run("python /tmp/script.py", stderr=True, stdout=True)
        result = exec_result.output.decode("utf-8").strip()

        # Check if the result contains an error (stderr)
        if "Traceback" in result or "Error" in result or "SyntaxError" in result:
            raise RuntimeError(result)  # Trigger the `except` block to handle debugging

        # Clean up
        container.stop()
        container.remove()
        os.remove(script_name)

        # Parse the output
        return parse_output(result) if "Final result:" in result else "Error: No final result format found."

    except Exception as e:
        print(f"Error detected: {e}")
        debugged_code = debug_code(code, str(e))
        # print(f"Debugged Code: {debugged_code}")
        return await execute_and_debug_code(debugged_code)  # Retry with debugged code
    finally:
        client.close()


# Helper function to parse the output
def parse_output(output: str) -> str:
    """
    Extract the final result from the output using the format "Final result: <number>".
    """
    match = re.search(r'Final result: (\d+)', output)
    return match.group(1) if match else "Error: Could not parse the result."
    # return output

# Function to use LLM for code debugging
def debug_code(code: str, error_message: str) -> str:
    """
    Use LLM to debug the given Python code based on the error message.
    """
    client = OpenAI(
        api_key=api_key, 
    )
    debug_prompt = (
        f"You are a Python expert. The following code has a bug:\n"
        f"---\n{code}\n---\n"
        f"The error message is:\n---\n{error_message}\n---\n"
        "Please correct the code and format your response as Python code only, inside a code block using ```python."
    )

    # OpenAI ChatCompletion API call
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert Python programmer and debugging assistant."},
            {"role": "user", "content": debug_prompt},
        ],
        max_tokens=1000,
        temperature=0.2,
    )

    # Extract content from the response
    response_text = chat_completion.choices[0].message.content

    # Post-process to extract the Python code inside ```python ... ```
    match = re.search(r"```python\s*(.*?)```", response_text, re.DOTALL)
    if match:
        debugged_code = match.group(1).strip()  # Get the Python code inside the code block
    else:
        debugged_code = "Error: No valid Python code block found."

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
    print(f'Question:\n {question}')
    final_result = asyncio.run(get_answer(question, majority_num=1))
    print(f"Final Answer: {final_result}")

#%%
'''
code = '# Initialize the candidate number\nx = 0\n\n# Loop until we find the correct number\nwhile True:\n    # Check the conditions\n    if (x % 4 == 1) and (x % 3 == 1) and (x % 5 == 2):\n        break  # Found the number\n    x += 1  # Increment the candidate number\n\n# Output the final result\nprint(f"Final result: {x}")'

error test:
code = '# Initialize the candidate number\nx = 0\n\n# Loop until we find the correct number\nwhile True:\n    # Check the conditions\n    if (x % 4 = 1) and (x % 3 == 1) and (x % 5 == 2):\n        break  # Found the number\n    x += 1  # Increment the candidate number\n\n# Output the final result\nprint(f"Final result: {x}")'
'''
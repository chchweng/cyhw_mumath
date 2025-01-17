#%%
from openai import OpenAI 
import json
import re
import os

with open("api.json", "r") as f:
    config = json.load(f)
# Load API key from an environment variable
api_key = config["OPENAI_API_KEY"] 

#%%
def load_questions(input_file: str) -> list:
    """
    Load questions from a JSON file.

    Args:
        input_file (str): Path to the input JSON file.

    Returns:
        list: List of question-answer dictionaries.
    """
    with open(input_file, 'r') as f:
        return json.load(f)

def bf_trans_augment_with_api(question: str, answer: int) -> dict:
    """
    Perform BF-Trans augmentation using OpenAI API.

    Args:
        question (str): Original question to be augmented.
        answer (int): The answer to the original question.

    Returns:
        dict: A dictionary containing the original and augmented question-answer pairs.
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
                    "You are an assistant specializing in transforming mathematical questions into augmented questions using the BF-Trans method. "
                    "Ensure the transformations are accurate, mathematically valid, and clear."
                )
            },
            {
                "role": "user",
                "content": (
                    "Your task is to apply the Backward-Forward Transformation (BF-Trans) method. "
                    "Follow these steps: \n"
                    "1. Provide the original answer as a new condition to the original question.\n"
                    # "2. Randomly mask one integer value apart from the origin answer in the question from step 1 that can be replaced with an unknown variable 'X'. So the question's answer become the value X you masked\n"
                    "2. Choose another interger in the question as the new answer of this question from step 1 and replaced with an unknown variable 'X'.\n"
                    " rephrase the question asking for value X"
                    
                    "3. Keep all conditions in the quenstion from previos step and rephrase the masked question into a forward question that directly asks for the value X without using unknown symbol X.\n"
                    # "Two important note: 1. No X in augmented question\n 2. Augmented answer must be different from original answer. If either of these happend, retry the process steps again"
                    "Create the question step by step. Make sure following the instructions"
                    # "Ensure the augmented question asks about the masked condition naturally and clearly."
                    "4. Provide the augmented question and its corresponding answer in this exact structure:\n"
                    "   Augmented question: <Your BF-Trans question here>\n"
                    "   Augmented answer: <The corresponding answer to the augmented question>\n"
                    f"Original question: \"{question}\"\n"
                    f"Answer: {answer}\n"                      

                )
            }
        ],
        max_tokens=1000,
        temperature=0.5
    )

    response_text = chat_completion.choices[0].message.content
    
    # Extract the augmented question and answer
    augmented_question_match = re.search(r"Augmented question: (.*?)\n", response_text, re.DOTALL)
    augmented_answer_match = re.search(r"Augmented answer: (.*?)$", response_text, re.DOTALL)

    if not augmented_question_match or not augmented_answer_match:
        raise ValueError("The API response did not contain the expected augmented question or answer.")

    augmented_question = augmented_question_match.group(1).strip()
    augmented_answer = augmented_answer_match.group(1).strip()
    print(f"bf-trans augmented_question: {augmented_question}")
    print(f"bf-trans augmented_answer: {augmented_answer}")
    return {
        "original_question": question,
        "original_answer": answer,
        "augmented_question": augmented_question,
        "augmented_answer": augmented_answer
    }



def save_augmented_questions(input_file: str, output_file: str):
    """
    Read questions from a JSON file, generate augmented QA pairs, and save to a new JSON file.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to save the output JSON file.
    """
    questions_data = load_questions(input_file)
    augmented_data = []

    for qa_pair in questions_data:
        original_question = qa_pair["question"]
        answer = qa_pair.get("answer", None)
        if answer is None:
            raise ValueError("Each question must have an answer in the input file.")
        augmented_qa_pair = bf_trans_augment_with_api(original_question, answer)
        augmented_data.append(augmented_qa_pair)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(augmented_data, f, indent=4)
#%%
# Example usage
if __name__ == "__main__":
    origin_qa_file = './examples/questions_w_ans.json'
    output_file = './examples/bf_trans_qa.json'
    save_augmented_questions(origin_qa_file, output_file)
# %%

import re

# Function to transform the question using FOBAR
def apply_fobar(question: str) -> str:
    """
    Transforms the original question into a backward question by masking a condition.
    The original question's condition is replaced with 'X', and the answer becomes the new condition.
    """
    # Example transformation logic (adjust based on your dataset):
    match = re.search(r'remainder of (\d+) when divided by (\d+)', question)
    if match:
        value, divisor = match.groups()
        backward_question = re.sub(r'remainder of \d+', f'remainder of X', question)
        backward_question += f"; Given: X = {value}"
        return backward_question
    return question

# Function to rephrase the backward question into a forward question
def rephrase_backward(backward_question: str) -> str:
    """
    Rephrases a backward question into a direct forward question.
    For example, from "Find X given ..." to "What is the value of X?".
    """
    # Rephrasing logic (customize as needed):
    if 'X =' in backward_question:
        forward_question = re.sub(r'Given: X = (\d+)', r'What is the value of X that satisfies this condition?', backward_question)
        forward_question = forward_question.replace(';', '.').strip()
        return forward_question
    return backward_question

# Main BF-Trans function
def bf_trans_augment(question: str) -> str:
    # Step 1: Apply FOBAR to transform question
    backward_question = apply_fobar(question)
    
    # Step 2: Rephrase the backward question
    forward_question = rephrase_backward(backward_question)
    
    return forward_question

# import spacy
# from transformers import pipeline

# # Load NLP models
# nlp = spacy.load("en_core_web_sm")
# rephrase_model = pipeline("text2text-generation", model="t5-small")

# def apply_fobar(question: str) -> str:
#     """
#     Dynamically apply FOBAR transformation by identifying conditions and masking key values.
#     """
#     doc = nlp(question)
#     # Example logic: Mask numerical entities and add a new condition
#     backward_question = question
#     for ent in doc.ents:
#         if ent.label_ in ("CARDINAL", "QUANTITY"):
#             backward_question = backward_question.replace(ent.text, "X")
#             backward_question += f" Given: {ent.text} = X."
#     return backward_question

# def rephrase_backward(backward_question: str) -> str:
#     """
#     Use a language model to rephrase the backward question into a forward question.
#     """
#     result = rephrase_model(backward_question, max_length=50, truncation=True)
#     return result[0]['generated_text']

# def bf_trans_augment(question: str) -> str:
#     """
#     Generalized BF-Trans pipeline.
#     """
#     # Step 1: Apply FOBAR to transform question
#     backward_question = apply_fobar(question)
    
#     # Step 2: Rephrase the backward question
#     forward_question = rephrase_backward(backward_question)
    
#     return forward_question

# Example usage
if __name__ == "__main__":
    example_question = "What is the smallest whole number that has a remainder of 1 when divided by 4, a remainder of 1 when divided by 3, and a remainder of 2 when divided by 5?"
    print(bf_trans_augment(example_question))

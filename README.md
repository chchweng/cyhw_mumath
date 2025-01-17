# MuMath Project

This repository demonstrates the implementation of `get_answer_pipeline` and `bf_trans_augment` functions for solving and augmenting mathematical reasoning problems using OpenAI GPT-4o-mini, Docker, and Python.

---

## Environment Setup

To run this project, ensure the following dependencies are installed:

### **Python Packages**
Install the required packages by running the installation command:
```bash
pip install -r requirements.txt
```

### **Docker**
Ensure Docker is installed and running. Follow the [Docker installation guide](https://docs.docker.com/get-started/) for your operating system.

---

## How to Run the Code

### **Step 1: Clone the Repository**
Clone the GitHub repository to your local machine:
```bash
git clone https://github.com/chchweng/cyhw_mumath.git
cd MuMath
```

### **Step 2: Configure API Key**
Create an `api.json` file in the root directory with your OpenAI API key:

```json
{
    "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY"
}
```

### **Step 3: Run the Demo Script**
To see the full demonstration, run:
```bash
python run.py
```

#### **Script Overview**
The `run.py` script demonstrates the following:

1. **Answering Example Questions**: Generates answers for input questions using `get_answer_pipeline` and saves the output as a JSON file `/examples/questions_w_ans.json`.
2. **Generating BF-Trans Augmented Questions**: Creates BF-Trans augmented questions based on the answered questions `/examples/bf_trans_qa.json`.

#### **Expected Output**
The script generates two files in the `examples` directory:

1. **`questions_w_ans.json`**: Contains the original questions with their computed answers.
2. **`bf_trans_qa.json`**: Contains the BF-Trans augmented questions and their corresponding answers.

---

## Testing Results

### **1. Answering Questions**
The `get_answer` function consistently outputs the correct answer, such as:

```json
{
    "question": "What is the smallest whole number that has a remainder of 1 when divided by 4, a remainder of 1 when divided by 3, and a remainder of 2 when divided by 5?",
    "answer": 37
}
```

### **2. Debugging Functionality**
When testing the `get_answer` function with faulty code like:

```python
# Initialize the candidate number
x = 0

# Loop until we find the correct number
while True:
    # Check the conditions
    if (x % 4 = 1) and (x % 3 == 1) and (x % 5 == 2):  # SyntaxError here
        break  # Found the number
    x += 1  # Increment the candidate number

# Output the final result
print(f"Final result: {x}")
```

The function correctly identifies the syntax error, fixes it in one iteration of the debug loop, and outputs the correct result: **37**.

---

## Future Work

### **1. Randomness in Augmentation**
Due to the randomness of GPT-4o-mini, the BF-Trans augmentation sometimes outputs unexpected questions, such as:

- "What is the value of X, the smallest whole number that has a remainder of 1 when divided by 4, a remainder of 1 when divided by 3, and a remainder of 2 when divided by 5?"
- "What is the value of X if the smallest whole number has a remainder of 1 when divided by 4, a remainder of 1 when divided by 3, and a remainder of X?"

This issue may be resolved by using a better-pretrained language model or by selecting other question types.

### **2. Additional Question Types**
Tests with other questions like:

```
Jim spends 2 hours watching TV and then decides to go to bed and reads for half as long. He does this 3 times a week. How many hours does he spend on TV and reading in 4 weeks?
```

Produce augmented questions such as:

```
Jim spends 2 hours watching TV and then decides to go to bed and reads for half as long. He does this a certain number of times a week. If he spends a total of 36 hours on TV and reading in 4 weeks, how many times a week does he do this?
```

**Augmented Answer**: `3`

These results suggest promising avenues for expanding the types of questions supported by the BF-Trans augmentation.
BF-trans works well on this question, However still need some improvement. 



'''
Run this script to demo the result of get_answer_pipline and bf_trans_augment functions
'''
import asyncio
from utils.bf_trans_augment import save_augmented_questions
from utils.get_answer_pipeline import process_questions

if __name__ == "__main__":
    origin_ques_path = './examples/questions.json'
    ques_w_ans_out_path = './examples/questions_w_ans.json'
    bf_trans_qa_path = './examples/bf_trans_qa.json'

    # step1: Get the answer of the example question using get_answer_pipeline and output a new file with QA pairs
    asyncio.run(process_questions(origin_ques_path, ques_w_ans_out_path, majority_num = 3))

    # step2: Get bf_trans_augments
    save_augmented_questions(ques_w_ans_out_path, bf_trans_qa_path)

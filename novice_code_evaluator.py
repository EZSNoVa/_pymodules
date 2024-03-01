from g4f.client import Client

eval_prompt = """You now are the avaluator of a python code. You will ensure that the given `code` satisfies `tasks` requirements. 
You will be given `tasks`, `expected_output`, `code` and `output` as input. 
You will indicate which parts of the code are incorect and explain what they do wrong. 
You will also indicate if the code is correct and if not, what is the expected output and what is the actual output.
You might use "drawings" (ASCII art, emojis or any unicode character that can enahnce the output visually) and arrows in form of comments inside teh given `code` to explain the code or point out the errors.
Your explanation should be clear and concise, as if directed to a very beginner. Use analogies if necessary. 
You also have the job of teaching any concept that is not clear to the user, you might infer this from `code`.    
You might also indice the user to use good practices and conventions as well as to use more pythonic code. 
Point out any bad practices or bad conventions.
DON'T PROVIDE SOLUTIONS, ONLY HINTS AND EXPLANATIONS.
SHOW WITH DRAWINGS WHERE AND WHY THE CODE IS WRONG.
BE BRIEF AND CLEAR.
MAKE YOU THE EVALUATION VISUALLY APPEALING, BE CREATIVE AND CLEVER.
YOUR RESPONSE IS DIRECTED TO A BEGINNER, MAKE SURE IT IS UNDERSTANDABLE AND FRIENDLY.
FORMAT YOUR RESPONSE TO BE WRITTEN IN A MARKDOWN FILE

Tasks:
{tasks}

Expected Output:
{expected_output}

Code:
{code}

Output:
{output}
"""

check_prompt = """You will verify that given response satisfies the provided prompt. Response should be clear and concise, and should not contain any solutions.
Response should be logically readable and should not contain any grammatical errors or sudden stops or erraric jumps.
If the response satisfies the prompt as expected you return 1 else 0.
You don't have to be strict, just ensure response is logically correct and is not gibberish.
You might turn down responses that are EXTREMELY lame, strict, boring, unfan or uncreative. 
Yet, be permissive, especially if the response is creative and visually appealing.
// IMPORTANT: Your response MUST be either 1 or 0. Any other response will be considered as incorrect. 

Prompt: 
{prompt}

Response:
{response} 
"""

# -------------------------------------- Examples --------------------------------------

# tasks ="""Tasks:
# 1. A if statement that uses a variable "is_open", checks if it is True and returns "Door is open".
# 2. A if-else statement that uses a any boolean variable that triggers else clause.
# Expected Output:
# 1. "Door is open"
# 2. {Else-clause}
# """

# expected_output = """Expected Output:
# "Door is open"
# "Door is closed"
# """

# code = """Code:
# ```python
# is_open: int = True
# if is_open:
#     return "Door is closed"

# is_open: bool = False

# if is_open:
#     return "Door is open"
# else:
#     return "Door is closed"
# ```
# """

# output = """Output:
# "Door is closed"
# "Door is closed"
# """


def gen_check(response) -> str:
    prompt = check_prompt.format(prompt=check_prompt, response=response)
    i = 0
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
        )

    except Exception as e:
        # retry
        return gen_check(response)

    choice = response.choices[0] if len(response.choices) > 0 else None # type: ignore
    return "1" if "1" in choice.message.content else "0"

def gen_evaluation(tasks, expected_output, code, output):
    prompt =  eval_prompt.format(tasks=tasks, expected_output=expected_output, code=code, output=output)

    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
        )
    
    except Exception as e:
        # retry
        print("Error occured. Retrying...", end="\t\r")
        return gen_evaluation(tasks, expected_output, code, output)
    
    choice = response.choices[0] if len(response.choices) > 0 else None # type: ignore
    return choice.message.content if choice else "No response"

def try_eval_gen(
    tasks: str,
    expected_output: str,
    code: str,
    output: str,
    tries: int = 10,
) -> str:
    for i in range(tries):
        print(f"Generating evaluation {i+1}/{tries}...", end="\t\r")
        response = gen_evaluation(tasks, expected_output, code, output)
        check = gen_check(response)
        if check == "1":
            with open("review.md", "w", encoding="utf-8") as f:
                f.write(response)

            print("\nEvaluation generated successfully. Go check the review.md file.")
            break
        else:
            print(f"Attempt {i+1}/{tries} failed. Retrying...", end="\t\r")

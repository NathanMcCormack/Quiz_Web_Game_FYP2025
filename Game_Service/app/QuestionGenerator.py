import os 
from typing import Literal # used for the set of allowed strings for difficulty 
from pydantic import BaseModel, Field 
from openai import OpenAI

Difficulty = Literal["easy", "medium", "hard"] #avoids other entries for difficulty 

#schemas the model has to follow 
class GeneratedQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    answer: int = Field(ge=0)
    category: str = Field(min_length=1, max_length=64)
    difficulty: Difficulty


class GeneratedQuestionSet(BaseModel):
    questions: list[GeneratedQuestion]

#function for generating the questions
#* forces keyword-only arguments meaning it must be caled like (category="Math", difficulty = "hard", count=20). It avoids accidental mix-ups 
#it tghen returns a list of generated questions 
def generate_questions(*, category: str, difficulty: Difficulty, count: int = 20) -> list[GeneratedQuestion]:

    #choosing which model to use
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    client = OpenAI()

#writing the prompts:
#system prompt is my rules that the model has to follow 
#the user prompt is the specific requests for this call 
system = (
    "You generate trivia questions for a numeric-ordering (timeline/number) quiz game.\n"
    "You MUST return exactly the requested number of items.\n"
    "\n"
    "Hard rules:\n"
    "- Each item must have: question (string), answer (integer), category (string), difficulty (easy/medium/hard).\n"
    "- answer MUST be a single whole number integer >= 0 (no decimals, no ranges, no lists).\n"
    "- Do NOT use approximations: no 'about', 'around', 'circa', '~', 'est.', or 'approximately'.\n"
    "- The question text MUST explicitly state what the number represents AND its unit "
    "e.g. 'In what year...', 'How many minutes...', 'How many kilometers...', 'How many people...'.\n"
    "- Answers must be unambiguous and based on widely accepted facts.\n"
    "- Avoid controversy, sensitive topics, or ambiguous figures.\n"
    "- Avoid duplicates: no repeated question prompts AND no repeated answers within the set.\n"
    "\n"
    "Content rules:\n"
    "- Mix year-based questions and other numeric facts. Ensure non-year questions include clear units.\n"
    "- Keep questions suitable for general audiences.\n"
    "\n"
    "If you cannot produce enough compliant items, regenerate internally until you can."
)

user = (
    f"Category: {category}\n"
    f"Difficulty: {difficulty}\n"
    f"Count: {count}\n"
    "Return exactly Count items that strictly match the provided output schema."
)

    #the code below is following the exact template form teh offical OpenAI reccomendations for validating the propmts response
    #sends the request to teh model and tells teh SDK to only accept an output that matches the schema above 
    resp = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        #the schema I want it to follow 
        text_format=GeneratedQuestionSet,
        # prevents storing teh request/response for privacy/data retention 
        store=False,
    )

    parsed: GeneratedQuestionSet = resp.output_parsed

    #checks that teh exact amount of questions were generated 
    if len(parsed.questions) != count:
        raise ValueError(f"Expected {count} questions, got {len(parsed.questions)}")

    #used for safety to avoid model confusion, will valuidate the answer, clean up the question and overwrite the category and difficulty to ensure they are exactly what the user inputted
    out: list[GeneratedQuestion] = []
    for q in parsed.questions:
        out.append(
            GeneratedQuestion(
                question=q.question.strip(), #strip() removes any characters before or after the text eg spaces, new lines or tabs 
                answer=int(q.answer), #makes sure answer is an integer
                category=category,
                difficulty=difficulty,
            )
        )
    return out

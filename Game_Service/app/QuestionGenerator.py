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
        "You generate timeline / numeric-ordering trivia questions for a quiz game.\n"
        "Return exactly the requested number of items.\n"
        "Rules:\n"
        "- The answer MUST be a single integer >= 0.\n"
        "- Mix 'year' questions and other numeric facts, but always make the number unambiguous.\n"
        "- The question text must clearly state what the number represents (e.g., year, population, height in meters, etc.).\n"
        "- Avoid duplicates and avoid controversial/ambiguous numbers.\n"
        "- Keep questions safe for general audiences."
    )

    user = (
        f"Category: {category}\n"
        f"Difficulty: {difficulty}\n"
        f"Generate exactly {count} questions.\n"
        "Output must match the schema strictly."
    )
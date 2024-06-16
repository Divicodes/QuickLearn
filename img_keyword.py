import os
import openai
from chunking import result
from dotenv import load_dotenv

load_dotenv()
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_keywords(script):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Based on the given sentence '{script}', generate one keyword which is used to search for the stock image related to the sentence.",
            },
        ],
        n=1,
        stop=None,
        temperature=0.7,
    )
    script = response.choices[0].message.content
    # print(script)
    return script  # Ensure the API returns a valid Python dictionary


for line in result.splitlines():
    keyword = generate_keywords(line)
    print(keyword)

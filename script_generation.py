import os
import openai

from dotenv import load_dotenv

load_dotenv()
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_openai(interests, topic):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Based on the user's '{interests}', generation a short paragraph script in a way that user will explain the '{topic}' with analogy of the interests mentioned.",
            },
        ],
        n=1,
        stop=None,
        temperature=0.7,
    )
    script = response.choices[0].message.content
    print(script)
    return script  # Ensure the API returns a valid Python dictionary


# interests = input("Enter your interests: ")
# topics = input("Enter your topics: ")
# ini_script = generate_openai(interests, topics)

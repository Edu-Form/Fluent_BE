
from openai import OpenAI

# # Load environment variables from the .env file
# load_dotenv.load_dotenv()

# # Access the OpenAI API key
# openai_api_key = os.getenv("OPENAI_API_KEY")
# 

client = OpenAI(api_key = "")

def ai_diary(original_text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a grammar checker. For grammatically incorrect parts, put astericks around the incorrect parts. Add correct words right next to the incorrect words. Put double astericks around the correct words."},
            {
                "role": "user",
                "content": f"{original_text}"
            }
        ]
    )

    print(completion.choices[0].message.content)
    return (completion.choices[0].message.content)

from openai import OpenAI

# # Load environment variables from the .env file
# load_dotenv.load_dotenv()

# # Access the OpenAI API key
# openai_api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key = "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")

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


# Split the text into lines based on '\n'
# Remove any leading or trailing whitespace from each line. Save into list. 
def parse_quizlet(original_text):
    lines = original_text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return lines

def translate_quizlet(eng_quizlet):

    eng_quizlet = "\n".join(eng_quizlet)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Translate the following lines of text from English to Korean. Return each translation on a new line:\n\n"},
            {
                "role": "user",
                "content": f"{eng_quizlet}"
            }
        ]
    )

    print(completion.choices[0].message.content)
    translated_text = completion.choices[0].message.content.strip()
    kor_quizlet = translated_text.split('\n')
    return kor_quizlet
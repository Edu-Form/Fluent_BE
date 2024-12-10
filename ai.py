
from openai import OpenAI
from difflib import SequenceMatcher

# # Load environment variables from the .env file
# load_dotenv.load_dotenv()

# # Access the OpenAI API key
# openai_api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key = "")

# Diary Correction
def ai_diary_correction(original_text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your task is to correct a student's diary sentences with a limited number of corrections to improve their writing skills.\n"
                    "Guidelines:\n"
                    "- Focus on identifying only crucial English grammar mistakes.\n"
                    "- Only correct the language aspect, refraining from altering spaces, commas, and similar punctuation.\n"
                    "- Correct each sentence individually without combining them.\n"
                    "- Respond only with the corrected text, without sentences like: "
                    "'Sure / Certainly. Here are the corrections based on the given criteria.'"
                ),
            },
            {
                "role": "user",
                "content": f"Here's the text to correct: {original_text}"
            }
        ]
    )

    print(completion.choices[0].message.content)
    return (completion.choices[0].message.content)


# Diary Expression
def ai_diary_expressions(original_text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                    "Recommend 5~10 new expressions for the student that can be used to improve the diary entry.\n"
                    "Guidelines:\n"
                    "- Stay within the vocabulary and grammar level of the diary text.\n"
                    "- Feel free to be slightly creative in line with the contents of the diary when recommending new expressions.\n"
                    "- Recommend new sentence structures.\n"
                    "- Recommend casual versions of the same sentence.\n"
                    "- Always include the number at the beginning of each expression.\n"
                    "- On the input, each sentence from the diary corrected text is separated by a newline character '\\n'.\n"
                    "- Sentences must be no longer than 50 characters.\n\n"
                    "Expected response example:\n"
                    "I headed to my friend's house\n"
                    "I didn't get up until noon\n"
                    "I woke up late\n"
                    "I was excited this morning because I used my new perfume\n"
                    "We watched a movie called \"Dune 2\"\n"
                    "My friend runs a pizza store in Seoul.\n"
                    "I was stressed because I woke up 20 minutes late\n"
                    "I didn't hear the alarm\n"
                    "I couldn't find my wallet\n"
                    "I didn't eat breakfast because I didn't have enough time"
                ),
            },
            {
                "role": "user",
                "content": f"Here is the diary to summarize: {original_text}"
            }
        ]
    )

    print(completion.choices[0].message.content)
    return (completion.choices[0].message.content)


# Diary Summary
def ai_diary_summary(original_text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your task is to summarize a student's diary entry in 3-5 sentences.\n"
                    "Guidelines:\n"
                    "- Write the summary in casual adult English tone.\n"
                    "- Write in first person.\n"
                    "- Use simple 4th-grade level vocabulary.\n"
                    "- Ensure that the first sentence starts with 'I wrote about'.\n"
                    "- Each sentence should have at most 40 words."
                ),
            },
            {
                "role": "user",
                "content": f"Here is the diary to summarize: {original_text}"
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



# Modifies the original text and corrected text to the red and green line that directly compares each other.
def generate_inline_comparison_html(original_text, corrected_text):
    """
    Generates an HTML file showing inline text comparison with changes highlighted.
    
    Args:
        original_text (str): The original text.
        corrected_text (str): The corrected text.
    
    Returns:
        str: An HTML string displaying the inline comparison.
    """
    matcher = SequenceMatcher(None, original_text.split(), corrected_text.split())
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # No changes; keep the text as is
            result.extend(original_text.split()[i1:i2])
        elif tag == "replace":
            # Show replaced words in red (original) and green (corrected)
            for orig, corr in zip(original_text.split()[i1:i2], corrected_text.split()[j1:j2]):
                result.append(f'<span style="color: red; text-decoration: line-through;">{orig}</span> <span style="color: green;">{corr}</span>')
        elif tag == "delete":
            # Highlight deleted text in red with strikethrough
            for orig in original_text.split()[i1:i2]:
                result.append(f'<span style="color: red; text-decoration: line-through;">{orig}</span>')
        elif tag == "insert":
            # Highlight inserted text in green
            for corr in corrected_text.split()[j1:j2]:
                result.append(f'<span style="color: green;">{corr}</span>')

    # Wrap the result in a styled HTML template
    html_output = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }}
            span {{
                margin: 0 2px;
            }}
        </style>
    </head>
    <body>
        {" ".join(result)}
    </body>
    </html>
    """
    return html_output


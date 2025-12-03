from llm_helper import llm
from few_shot import FewShotPosts
import requests
from bs4 import BeautifulSoup  # Import these two

few_shot = FewShotPosts()


def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"


# --- NEW FUNCTION START ---
def get_text_from_url(url):
    """
    Fetches text content from a given URL (Article, Blog, etc.)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove junk (scripts, styles, navbars)
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()

        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]  # Limit to 3000 chars to save token costs
    except Exception as e:
        return f"Error extracting content: {str(e)}"


# --- NEW FUNCTION END ---

def generate_post(length, language, tag, reference_text=None, use_only_reference=False):
    # ... (Rest of your file remains EXACTLY the same)
    if reference_text:
        print("✅ Using reference style:", "ONLY reference" if use_only_reference else "Mixed with few-shot")

    prompt = get_prompt(length, language, tag, reference_text, use_only_reference)
    response = llm.invoke(prompt)
    return response.content


def get_prompt(length, language, tag, reference_text=None, use_only_reference=False):
    # ... (Keep exactly as it was)
    length_str = get_length_str(length)

    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    If Language is Hinglish then it means it is a mix of Hindi and English.
    The script for the generated post should always be English.
    '''

    # --- Load few-shot examples ---
    examples = few_shot.get_filtered_posts(length, language, tag)

    # --- Handle reference style ---
    if reference_text:
        if use_only_reference:
            examples = [{"text": reference_text}]
        else:
            examples.append({"text": reference_text})

    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."

    for i, post in enumerate(examples):
        post_text = post["text"]
        prompt += f"\n\nExample {i + 1}:\n{post_text}"

        if i == 1:
            break

    return prompt


def generate_hashtags_for_post(post_text):
    # ... (Keep exactly as it was)
    prompt = f"""
    Generate 5-10 relevant LinkedIn hashtags for the following post. No preamble.
    Use #CamelCase format and separate hashtags by space and add # at the beginning of every hashtag.

    Post: {post_text}
    """
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    print(generate_post("Medium", "English", "Mental Health"))

from llm_helper import llm
from few_shot import FewShotPosts
import requests
from bs4 import BeautifulSoup
import re  # Used for cleaning text

few_shot = FewShotPosts()


def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"


# --- 1. URL SCRAPER FUNCTION ---
def get_text_from_url(url):
    """
    Fetches text content from a given URL (Article, Blog, etc.)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove junk (scripts, styles, navbars)
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()

        text = soup.get_text(separator=' ', strip=True)
        return text[:1000]  # Limit to 3000 chars to save token costs
    except Exception as e:
        return f"Error extracting content: {str(e)}"


# --- 2. HOOK GENERATOR (With Parsing Fix) ---
def generate_hooks(tag, language, reference_text=None):
    prompt = f"""
    Generate 3 distinct, catchy opening lines (hooks) for a LinkedIn post about '{tag}'.

    Constraints:
    1. Language: {language}
    2. Hook 1: Question style.
    3. Hook 2: Strong/Controversial Statement.
    4. Hook 3: Short Story/Personal Opener.
    5. CRITICAL: Separate the 3 hooks using the delimiter "|||". 
    6. Do not number them (e.g. dont write 1. or Option 1). Just the text.

    Example Output:
    Did you know AI is changing? ||| Stop ignoring this trend right now. ||| I made a huge mistake yesterday.

    Reference Context:
    {reference_text if reference_text else "None provided"}
    """
    response = llm.invoke(prompt)
    content = response.content.strip()

    # --- Robust Parsing Logic ---
    # Attempt to split by delimiter
    if "|||" in content:
        hooks = content.split("|||")
    else:
        # Fallback: Split by newlines if LLM ignored delimiter
        hooks = content.split("\n")

    # Clean the hooks (remove "1.", "-", empty strings)
    clean_hooks = []
    for h in hooks:
        h = h.strip()
        # Regex to remove leading numbers like "1. ", "1)", "Hook 1:"
        h = re.sub(r'^(Hook \d:|Option \d:|\d+\.|-)\s*', '', h)

        if h and len(h) > 5:  # Filter out empty or too short lines
            clean_hooks.append(h)

    return clean_hooks[:3]  # Ensure we return max 3 items


# --- 3. MAIN POST GENERATOR ---
def generate_post(length, language, tag, reference_text=None, use_only_reference=False, selected_hook=None):
    if reference_text:
        print("✅ Using reference style:", "ONLY reference" if use_only_reference else "Mixed with few-shot")

    prompt = get_prompt(length, language, tag, reference_text, use_only_reference, selected_hook)
    response = llm.invoke(prompt)
    return response.content


# --- 4. PROMPT BUILDER ---
def get_prompt(length, language, tag, reference_text=None, use_only_reference=False, selected_hook=None):
    length_str = get_length_str(length)

    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    If Language is Hinglish then it means it is a mix of Hindi and English.
    The script for the generated post should always be English.

    IMPORTANT: Do not add hashtags in the output.
    '''

    # Inject the selected hook if it exists
    if selected_hook:
        prompt += f"\n   IMPORTANT: You MUST start the post with this exact opening line: '{selected_hook}'\n"

    # --- Load few-shot examples ---
    examples = few_shot.get_filtered_posts(length, language, tag)

    # --- Handle reference style ---
    if reference_text:
        if use_only_reference:
            examples = [{"text": reference_text}]
        else:
            examples.append({"text": reference_text})

    # --- Add examples to the prompt ---
    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."

    for i, post in enumerate(examples):
        post_text = post["text"]
        prompt += f"\n\nExample {i + 1}:\n{post_text}"

        if i == 1:  # Use max two examples
            break

    return prompt


# --- 5. HASHTAG GENERATOR ---
def generate_hashtags_for_post(post_text):
    prompt = f"""
    Generate 5-10 relevant LinkedIn hashtags for the following post. No preamble.
    Use #CamelCase format and separate hashtags by space and add # at the beginning of every hashtag.

    Post: {post_text}
    """
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    # Small test
    print("Test Hook Gen:", generate_hooks("AI", "English"))

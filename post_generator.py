from llm_helper import llm
from few_shot import FewShotPosts

few_shot = FewShotPosts()


def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"


def generate_post(length, language, tag, reference_text=None, use_only_reference=False):
    if reference_text:
        print("✅ Using reference style:", "ONLY reference" if use_only_reference else "Mixed with few-shot")

    prompt = get_prompt(length, language, tag, reference_text, use_only_reference)

    response = llm.invoke(prompt)
    return response.content


def get_prompt(length, language, tag, reference_text=None, use_only_reference=False):
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
            # User wants only this reference style
            examples = [{"text": reference_text}]
        else:
            # Mix reference example with few-shot
            examples.append({"text": reference_text})

    # --- Add examples to the prompt ---
    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."

    for i, post in enumerate(examples):
        post_text = post["text"]
        prompt += f"\n\nExample {i+1}:\n{post_text}"

        if i == 1:  # Use max two examples
            break

    return prompt



def generate_hashtags_for_post(post_text):
    prompt = f"""
    Generate 5-10 relevant LinkedIn hashtags for the following post. No preamble.
    Use #CamelCase format and separate hashtags by space and add # at the beginning of every hashtag.
    

    Post: {post_text}
    """
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    print(generate_post("Medium", "English", "Mental Health"))
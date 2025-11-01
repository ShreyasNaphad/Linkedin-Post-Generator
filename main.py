import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post
from post_generator import generate_hashtags_for_post
import sys
sys.stdout.reconfigure(encoding='utf-8')



# Options for length and language
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]


# Main app layout
def main():
    st.subheader("LinkedIn Post Generator")

    # Create three columns for the dropdowns
    col1, col2, col3 = st.columns(3)

    fs = FewShotPosts()
    tags = fs.get_tags()
    with col1:
        # Dropdown for Topic (Tags)
        selected_tag = st.selectbox("Topic", options=tags)

    with col2:
        # Dropdown for Length
        selected_length = st.selectbox("Length", options=length_options)

    with col3:
        # Dropdown for Language
        selected_language = st.selectbox("Language", options=language_options)

    # --- Optional Reference Section ---
    st.subheader("🎯 Optional Reference Style")

    reference_text = st.text_area(
        "If you want to mimic a specific influencer or style, paste a sample LinkedIn post here:",
        placeholder="Paste influencer’s post or your own content style here...",
        height=150
    )

    use_only_reference = st.checkbox(
        "Use ONLY this reference style (ignore few-shot examples)"
    )

    # Checkbox for optional hashtags
    generate_hashtags_option = st.checkbox("Add Hashtags to Post")

    # Generate Button
    if st.button("Generate"):
        post = generate_post(
            selected_length,
            selected_language,
            selected_tag,
            reference_text=reference_text,
            use_only_reference=use_only_reference
        )

        # Post card
        st.markdown(
            f"""
            <div style="
                background-color:#ffffff; 
                padding:20px; 
                border-radius:15px; 
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom:15px;
            ">
                <h4 style="color:#0073b1; margin-bottom:10px;">📝 Generated Post</h4>
                <p style="font-size:16px; line-height:1.6; color:#0f0f0f;">{post}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Optional hashtags
        if generate_hashtags_option:
            hashtags = generate_hashtags_for_post(post)
            st.markdown(
                f"""
                <div style="
                    background-color:#0073b1;  /* LinkedIn blue background */
                    padding:15px; 
                    border-radius:12px; 
                    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                    margin-bottom:15px;
                ">
                    <h5 style="color:#ffffff; margin-bottom:8px;">🔖 Suggested Hashtags</h5>
                    <p style="font-size:15px; color:#ffffff; line-height:1.6;">{hashtags}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


# Run the app
if __name__ == "__main__":
    main()
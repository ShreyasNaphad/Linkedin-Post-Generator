import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post, generate_hashtags_for_post, get_text_from_url
import sys

# Ensure UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# --- Page Configuration ---
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Dark Mode & Creative UI) ---
st.markdown("""
<style>
    /* 1. MAIN BACKGROUND */
    .stApp {
        background-color: #0b0c10; /* Deep Dark */
        color: #c5c6c7;
    }

    /* 2. SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background-color: #1f2833; /* Dark Blue-Grey */
        border-right: 1px solid #45a29e;
    }

    /* Sidebar Text */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label {
        color: #66fcf1 !important; /* Neon Cyan */
        font-family: 'Helvetica', sans-serif;
    }

    /* 3. INPUT FIELDS (Dropdowns & Text Areas) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #2b3542 !important;
        color: white !important;
        border: 1px solid #45a29e !important;
    }

    .stTextInput input {
        background-color: #2b3542 !important;
        color: white !important;
        border: 1px solid #45a29e !important;
    }

    .stTextArea textarea {
        background-color: #2b3542 !important;
        color: #ffffff !important;
        border: 1px solid #45a29e !important;
        border-radius: 8px;
    }

    /* 4. MAIN HEADERS */
    .main-title {
        background: -webkit-linear-gradient(45deg, #66fcf1, #45a29e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #c5c6c7;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-style: italic;
    }

    /* 5. LINKEDIN DARK CARD PREVIEW */
    .linkedin-card {
        background: #1b1f23; /* LinkedIn Dark Mode Bg */
        border: 1px solid #383b40;
        border-radius: 12px;
        padding: 0;
        margin-top: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto;
        color: #e1e9ee;
    }

    .card-header {
        padding: 12px 16px;
        display: flex;
        align-items: center;
    }

    .avatar {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #66fcf1, #45a29e);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0b0c10;
        font-weight: 800;
        margin-right: 12px;
    }

    .user-details h4 {
        margin: 0;
        font-size: 15px;
        font-weight: 600;
        color: #ffffff;
    }

    .user-details p {
        margin: 0;
        font-size: 12px;
        color: #a0b4b7;
    }

    .card-body {
        padding: 4px 16px 16px 16px;
        font-size: 14px;
        line-height: 1.6;
        color: #e1e9ee;
        white-space: pre-wrap; /* Preserves formatting */
    }

    .card-footer {
        border-top: 1px solid #383b40;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        color: #a0b4b7;
        font-weight: 600;
        font-size: 14px;
    }

    .card-footer div {
        cursor: pointer;
        padding: 8px;
        border-radius: 4px;
        transition: background 0.2s;
    }
    .card-footer div:hover {
        background-color: #383b40;
    }

    /* 6. BUTTON STYLING */
    .stButton button {
        background: linear-gradient(90deg, #45a29e 0%, #66fcf1 100%);
        color: #0b0c10;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        width: 100%;
        box-shadow: 0 4px 10px rgba(69, 162, 158, 0.3);
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        color: #000;
    }

    /* Code block styling */
    code {
        color: #66fcf1;
        background-color: #1f2833;
    }

</style>
""", unsafe_allow_html=True)


def main():
    # --- Initialize Session State ---
    if 'generated_post' not in st.session_state:
        st.session_state.generated_post = ""
    if 'generated_hashtags' not in st.session_state:
        st.session_state.generated_hashtags = ""
    if 'reference_content' not in st.session_state:
        st.session_state.reference_content = ""

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")

        # Load Few Shot Tags
        try:
            fs = FewShotPosts()
            tags = fs.get_tags()
        except Exception:
            tags = ["General"]

        selected_tag = st.selectbox("🎯 Topic", options=tags)
        selected_length = st.selectbox("📏 Length", options=["Short", "Medium", "Long"])
        selected_language = st.selectbox("🌐 Language", options=["English", "Hinglish"])

        st.markdown("---")
        st.markdown("### 🔧 Settings")
        use_only_reference = st.checkbox("Strict Mode (Ignore Examples)")
        generate_hashtags_option = st.checkbox("Auto-Hashtags", value=True)

    # --- Main Content ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="main-title">LinkedIn Creator</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Turn messy thoughts into viral influence.</div>', unsafe_allow_html=True)

        # --- NEW: URL INPUT SECTION ---
        st.markdown("##### 🔗 Import Content (New!)")
        url_col_1, url_col_2 = st.columns([3, 1])

        with url_col_1:
            url_input = st.text_input(
                "Paste Article URL",
                placeholder="https://techcrunch.com/...",
                label_visibility="collapsed"
            )

        with url_col_2:
            if st.button("📥 Load"):
                if url_input:
                    with st.spinner("Scraping content..."):
                        # Calls the function we added to post_generator.py
                        scraped_text = get_text_from_url(url_input)
                        st.session_state.reference_content = scraped_text
                else:
                    st.warning("Paste a URL first.")

        # --- MAIN TEXT AREA ---
        st.markdown("##### 💡 Source Material")
        reference_text = st.text_area(
            "Content Source",
            value=st.session_state.reference_content,
            label_visibility="collapsed",
            height=250,
            placeholder="Paste your rough notes, OR use the URL loader above..."
        )

        # Sync manual typing back to session state
        if reference_text != st.session_state.reference_content:
            st.session_state.reference_content = reference_text

        # --- GENERATE BUTTON ---
        if st.button("✨ Generate Magic"):
            if not selected_tag and not reference_text:
                st.error("Please enter some text or select a topic!")
            else:
                with st.spinner("🤖 AI is crafting your masterpiece..."):
                    # Call Backend
                    post = generate_post(
                        selected_length,
                        selected_language,
                        selected_tag,
                        reference_text=reference_text,
                        use_only_reference=use_only_reference
                    )

                    # Fix whitespace
                    post = post.strip()

                    st.session_state.generated_post = post

                    if generate_hashtags_option:
                        st.session_state.generated_hashtags = generate_hashtags_for_post(post)
                    else:
                        st.session_state.generated_hashtags = ""

    # --- Preview Column ---
    with col2:
        if st.session_state.generated_post:
            st.markdown("##### 📱 Dark Mode Preview")

            full_text = st.session_state.generated_post
            if st.session_state.generated_hashtags:
                full_text += f"\n\n{st.session_state.generated_hashtags}"

            # HTML Card Rendering (With Whitespace Fix)
            st.markdown(f"""
            <div class="linkedin-card">
                <div class="card-header">
                    <div class="avatar">AI</div>
                    <div class="user-details">
                        <h4>Your Name</h4>
                        <p>Thought Leader • 1st</p>
                        <p>Now • 🌐</p>
                    </div>
                    <div style="margin-left:auto; color:#a0b4b7;">...</div>
                </div>
                <div class="card-body">{full_text}</div>
                <div class="card-footer">
                    <div>👍 Like</div>
                    <div>💬 Comment</div>
                    <div>🔁 Repost</div>
                    <div>🚀 Send</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Native Copy Button
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📋 Copy to Clipboard")
            st.code(full_text, language="markdown")
        else:
            # Empty State
            st.markdown("""
            <div style="text-align:center; margin-top:100px; color:#45a29e; opacity:0.7;">
                <h1>👈</h1>
                <h3>Paste a URL or write notes on the left to see the magic here.</h3>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

import streamlit as st
import streamlit.components.v1 as components
from few_shot import FewShotPosts
from post_generator import generate_post, generate_hashtags_for_post, get_text_from_url, generate_hooks
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

# --- Custom CSS (Premium Dark Mode) ---
st.markdown("""
<style>
    /* 1. Global Dark Theme */
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
        font-family: 'Helvetica', sans-serif;
    }

    /* 2. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1f2833;
        border-right: 1px solid #45a29e;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #66fcf1 !important;
    }

    /* 3. Inputs & Text Areas - FORCE TEXT COLOR FOR RENDER */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #2b3542 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #45a29e !important;
        border-radius: 8px;
    }
    
    /* Placeholder Text Visibility */
    ::placeholder {
        color: #a0b4b7 !important;
        opacity: 1 !important;
    }
    
    /* Dropdown Menu Items */
    div[data-baseweb="popover"] div {
        background-color: #1f2833 !important;
        color: #ffffff !important;
    }

    /* 4. Headers */
    .main-title {
        background: -webkit-linear-gradient(45deg, #66fcf1, #45a29e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8892b0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-style: italic;
    }

    /* 5. LinkedIn Preview Card */
    .linkedin-card {
        background: #1b1f23;
        border: 1px solid #383b40;
        border-radius: 12px;
        margin-top: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        color: #e1e9ee;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto;
    }
    .card-header { padding: 12px 16px; display: flex; align-items: center; }
    .avatar { width: 48px; height: 48px; background: linear-gradient(135deg, #66fcf1, #45a29e); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #0b0c10; font-weight: 800; margin-right: 12px; }
    .user-details h4 { margin: 0; font-size: 15px; font-weight: 600; color: #ffffff; }
    .user-details p { margin: 0; font-size: 12px; color: #a0b4b7; }
    .card-body { padding: 4px 16px 16px 16px; font-size: 14px; line-height: 1.6; color: #e1e9ee; white-space: pre-wrap; }
    .card-footer { border-top: 1px solid #383b40; padding: 12px 16px; display: flex; justify-content: space-between; color: #a0b4b7; font-weight: 600; font-size: 14px; }

    /* 6. Hook Selection Cards */
    .hook-option {
        background-color: #161b22;
        border-left: 4px solid #66fcf1;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
        color: #c9d1d9;
    }
    .hook-label {
        font-weight: bold;
        color: #66fcf1;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    /* 7. BUTTON STYLING */
    .primary-btn, .secondary-btn { width: 100%; }
    .stButton button { width: 100%; border-radius: 50px; font-weight: 700; padding: 0.75rem 1rem; transition: transform 0.2s; }
    .primary-btn button { background: linear-gradient(90deg, #45a29e 0%, #66fcf1 100%) !important; color: #0b0c10 !important; border: none !important; }
    .secondary-btn button { background: transparent !important; color: #c5c6c7 !important; border: 2px solid #45a29e !important; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 252, 241, 0.2); }
    code { color: #66fcf1; background-color: #1f2833; }
</style>
""", unsafe_allow_html=True)


# --- SCROLLING JAVASCRIPT FUNCTIONS ---
def scroll_to_top():
    """Scrolls to the top with a delay to ensure the UI has redrawn."""
    js = '''
    <script>
        setTimeout(function() {
            var body = window.parent.document.querySelector('div[data-testid="stAppViewContainer"]');
            if (body) {
                body.scrollTop = 0;
            }
        }, 100); // 100ms delay
    </script>
    '''
    components.html(js, height=0)

def scroll_to_bottom():
    """Scrolls to the bottom with a delay."""
    js = '''
    <script>
        setTimeout(function() {
            var body = window.parent.document.querySelector('div[data-testid="stAppViewContainer"]');
            if (body) {
                body.scrollTop = body.scrollHeight;
            }
        }, 100); // 100ms delay
    </script>
    '''
    components.html(js, height=0)


def main():
    if 'generated_post' not in st.session_state: st.session_state.generated_post = ""
    if 'generated_hashtags' not in st.session_state: st.session_state.generated_hashtags = ""
    if 'reference_content' not in st.session_state: st.session_state.reference_content = ""
    if 'generated_hooks' not in st.session_state: st.session_state.generated_hooks = []
    if 'step' not in st.session_state: st.session_state.step = 1

    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")
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

        has_reference = bool(st.session_state.reference_content.strip())
        use_only_reference = st.checkbox(
            "Strict Mode (Ignore Examples)",
            disabled=not has_reference,
            help="Enable this to use ONLY your provided text style."
        )

        generate_hashtags_option = st.checkbox("Auto-Hashtags", value=True)

        st.markdown("---")
        if st.button("🔄 New Post (Reset)"):
            st.session_state.step = 1
            st.session_state.generated_hooks = []
            st.session_state.generated_post = ""
            st.rerun()

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown('<div class="main-title">LinkedIn Creator</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Turn messy thoughts into viral influence.</div>', unsafe_allow_html=True)

        # 1. URL Importer
        st.markdown("##### 🔗 Import Content (Optional)")
        url_col1, url_col2 = st.columns([3, 1])
        with url_col1:
            url_input = st.text_input("Paste Article URL", placeholder="https://techcrunch.com/...",
                                      label_visibility="collapsed")
        with url_col2:
            if st.button("📥 Load"):
                if url_input:
                    with st.spinner("Scraping..."):
                        text = get_text_from_url(url_input)
                        st.session_state.reference_content = text
                        st.rerun()
                else:
                    st.warning("Paste a URL first.")

        # 2. Text Input
        st.markdown("##### 💡 Source Material / Notes")
        reference_text = st.text_area(
            "Reference Text",
            value=st.session_state.reference_content,
            height=200,
            label_visibility="collapsed",
            placeholder="Paste your rough notes here, or use the URL loader above..."
        )

        if reference_text != st.session_state.reference_content:
            st.session_state.reference_content = reference_text
            st.rerun()

        st.markdown("---")

        # === THE GENERATION LOGIC ===

        # [STEP 1] Two Options: Hooks or Quick Generate
        if st.session_state.step == 1:
            col_btn1, col_btn2 = st.columns([1, 1], gap="small")

            with col_btn1:
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("🧪 Generate Hooks"):
                    if not selected_tag and not reference_text:
                        st.error("Please enter some text or select a topic!")
                    else:
                        with st.spinner("🧠 Brainstorming viral angles..."):
                            hooks = generate_hooks(selected_tag, selected_language, reference_text)
                            st.session_state.generated_hooks = hooks
                            st.session_state.step = 2
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_btn2:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("⚡ Quick Generate"):
                    if not selected_tag and not reference_text:
                        st.error("Input required!")
                    else:
                        generate_final_post(selected_length, selected_language, selected_tag, reference_text,
                                            use_only_reference, None, generate_hashtags_option)
                st.markdown('</div>', unsafe_allow_html=True)

        # [STEP 2] Choose Hook & Generate Post
        elif st.session_state.step == 2:
            # --- FORCE SCROLL BOTTOM ---
            scroll_to_bottom()

            st.info("👇 Choose the best opening line to generate the full post.")

            hooks = st.session_state.generated_hooks

            if len(hooks) > 0:
                st.markdown(
                    f'<div class="hook-option"><div class="hook-label">Option 1: Question Style</div>{hooks[0]}</div>',
                    unsafe_allow_html=True)
                if st.button("🚀 Generate with Option 1"):
                    generate_final_post(selected_length, selected_language, selected_tag, reference_text,
                                        use_only_reference, hooks[0], generate_hashtags_option)

            if len(hooks) > 1:
                st.markdown(
                    f'<div class="hook-option"><div class="hook-label">Option 2: Bold Statement</div>{hooks[1]}</div>',
                    unsafe_allow_html=True)
                if st.button("🚀 Generate with Option 2"):
                    generate_final_post(selected_length, selected_language, selected_tag, reference_text,
                                        use_only_reference, hooks[1], generate_hashtags_option)

            if len(hooks) > 2:
                st.markdown(
                    f'<div class="hook-option"><div class="hook-label">Option 3: Story Opener</div>{hooks[2]}</div>',
                    unsafe_allow_html=True)
                if st.button("🚀 Generate with Option 3"):
                    generate_final_post(selected_length, selected_language, selected_tag, reference_text,
                                        use_only_reference, hooks[2], generate_hashtags_option)

            if st.button("🔙 Go Back"):
                st.session_state.step = 1
                st.rerun()

        # [STEP 3] Finished
        elif st.session_state.step == 3:
            if st.button("🔄 Start Over"):
                st.session_state.step = 1
                st.session_state.generated_post = ""
                st.rerun()

    # === RIGHT COLUMN: Preview ===
    with col2:
        if st.session_state.generated_post:
            # --- FORCE SCROLL TOP ---
            scroll_to_top()

            st.markdown("##### 📱 Dark Mode Preview")

            full_text = st.session_state.generated_post
            if st.session_state.generated_hashtags:
                full_text += f"\n\n{st.session_state.generated_hashtags}"

            st.markdown(f"""
            <div class="linkedin-card">
                <div class="card-header">
                    <div class="avatar">AI</div>
                    <div class="user-details">
                        <h4>Your Name</h4>
                        <p>Thought Leader • 1st</p>
                        <p>Now • 🌐</p>
                    </div>
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

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📋 Copy to Clipboard")
            st.code(full_text, language="markdown")

        else:
            if st.session_state.step == 1:
                # Aligned and styled Instruction Box
                st.markdown("""
<div style="background-color: #161b22; border: 2px dashed #45a29e; border-radius: 12px; padding: 25px; text-align: center;">
    <div style="font-size: 2.5rem; margin-bottom: 10px;">👋</div>
    <h3 style="color: #66fcf1; margin-bottom: 5px; margin-top:0;">Welcome to the Studio</h3>
    <p style="color: #a0b4b7; margin-bottom: 20px; font-size: 0.9rem;">Follow these steps to go viral:</p>
    <div style="text-align: left; display: inline-block; color: #c5c6c7; font-size: 0.9rem;">
        <div style="margin-bottom: 8px;">
            <span style="color: #66fcf1; font-weight: bold;">1.</span> 
            Import a URL or paste your notes.
        </div>
        <div style="margin-bottom: 8px;">
            <span style="color: #66fcf1; font-weight: bold;">2.</span> 
            Select a Topic & Length.
        </div>
        <div>
            <span style="color: #66fcf1; font-weight: bold;">3.</span> 
            Click <b>Generate Hooks</b> to start.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

            elif st.session_state.step == 2:
                st.markdown("""
<div style="background-color: #161b22; border: 2px solid #66fcf1; border-radius: 12px; padding: 25px; text-align: center;">
    <h3 style="color: #66fcf1; margin-bottom: 10px;">👈 Pick your Angle</h3>
    <p style="color: #c5c6c7;">We generated 3 hooks for you.</p>
    <p style="color: #a0b4b7; font-size: 0.9rem;">Select the one that fits your vibe.</p>
</div>
""", unsafe_allow_html=True)


def generate_final_post(length, language, tag, ref_text, strict_mode, hook, hashtags_opt):
    with st.spinner("Writing full post..."):
        post = generate_post(
            length, language, tag,
            reference_text=ref_text,
            use_only_reference=strict_mode,
            selected_hook=hook
        )
        st.session_state.generated_post = post.strip()

        if hashtags_opt:
            st.session_state.generated_hashtags = generate_hashtags_for_post(post)
        else:
            st.session_state.generated_hashtags = ""

        st.session_state.step = 3
        st.rerun()


if __name__ == "__main__":
    main()

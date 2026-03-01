"""CareGuide — healthcare chatbot built with Streamlit + Gemini."""
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

SYSTEM_PROMPT = (
    "You are CareGuide, a friendly healthcare assistant.\n"
    "- Provide clear, concise, and practical health information in plain language.\n"
    "- Never give a definitive diagnosis; always recommend seeing a licensed clinician.\n"
    "- For emergencies (chest pain, stroke signs, severe bleeding, breathing crisis) "
    "immediately tell the user to call emergency services.\n"
    "- When discussing medications, remind users to consult their doctor or pharmacist first.\n"
    "- End responses with a short safety note or a 'When to see a doctor' line where relevant."
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareGuide",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)
# force dark theme for all built-in Streamlit widgets
st._config.set_option("theme.base", "dark")
st._config.set_option("theme.backgroundColor", "#0f1117")
st._config.set_option("theme.secondaryBackgroundColor", "#1f2937")
st._config.set_option("theme.textColor", "#e5e7eb")
st._config.set_option("theme.primaryColor", "#10b981")

# ── Dark-theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* dark background everywhere */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="block-container"] {
    background-color: #0f1117 !important;
    color: #e5e7eb !important;
}
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"]  { display: none !important; }
footer, header { display: none !important; }

/* center column width */
[data-testid="block-container"] {
    max-width: 760px !important;
    padding: 1.5rem 1.5rem 6rem !important;
}

/* header */
.care-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 14px;
    border-bottom: 1px solid #1f2937;
    margin-bottom: 14px;
}
.care-header .hicon { font-size: 2rem; line-height: 1; }
.care-header h1 {
    margin: 0; font-size: 1.25rem; font-weight: 700; color: #34d399;
}
.care-header p { margin: 0; font-size: 0.75rem; color: #6b7280; }

/* chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 6px 0 !important;
}
/* user bubble */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stMarkdownContainer"],
.stChatMessage.user [data-testid="stMarkdownContainer"] {
    background: #1f2937 !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 10px 14px !important;
    color: #e5e7eb !important;
}
/* assistant bubble */
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stMarkdownContainer"],
.stChatMessage.assistant [data-testid="stMarkdownContainer"] {
    background: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 10px 14px !important;
    color: #e5e7eb !important;
}

/* chat input bar */
[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: min(760px, 100%) !important;
    background: #0f1117 !important;
    border-top: 1px solid #1f2937 !important;
    padding: 10px 16px 14px !important;
    z-index: 999 !important;
}
[data-testid="stChatInput"] textarea {
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
    font-size: 0.93rem !important;
    background: #1f2937 !important;
    color: #e5e7eb !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: #10b981 !important;
    border-radius: 8px !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: #059669 !important;
}
/* new chat button */
[data-testid="stBaseButton-secondary"] {
    background: #1f2937 !important;
    color: #9ca3af !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background: #374151 !important;
    color: #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="care-header">
  <span class="hicon">🩺</span>
  <div>
    <h1>Healthcare assistant</h1>
    <p>Your personal Healthcare assistant</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── New chat button ────────────────────────────────────────────────────────────
if st.button("🗑 New chat", type="secondary"):
    st.session_state.messages = []
    st.rerun()

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Gemini client (cached per session) ────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY missing in .env"); st.stop()
    return genai.Client(api_key=api_key)

client = get_client()
MODEL  = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

# ── Render history ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a health question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build full prompt
    history_text = ""
    for m in st.session_state.messages[:-1][-10:]:
        role = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{role}: {m['content']}\n"

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{history_text}"
        f"User: {prompt}\n"
        "Assistant:"
    )

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                result = client.models.generate_content(model=MODEL, contents=full_prompt)
                reply  = (getattr(result, "text", "") or "").strip() or "No response generated."
            except Exception as exc:
                reply = f"Something went wrong: {exc}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

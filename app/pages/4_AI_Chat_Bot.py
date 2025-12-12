import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🤖 AI Chat Bot", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []
if "ai_role" not in st.session_state:
    st.session_state.ai_role = "Cyber Security Specialist"

PERSONAS = {
    "Cyber Security Specialist": (
        "You are a helpful cyber security specialist. Provide clear, practical, and secure advice "
        "about cybersecurity incidents, best practices, threat mitigation, and secure system design. "
        "Keep recommendations safe and avoid enabling harmful or illegal activities."
    ),
    "IT Specialist": (
        "You are an IT support specialist. Provide troubleshooting steps, configuration guidance, "
        "and pragmatic advice for typical IT issues (networks, servers, user support). Be concise and user-friendly."
    ),
    "AI Data Science Specialist": (
        "You are an AI & Data Science expert. Provide guidance on data modelling, ML workflow, "
        "evaluation, tooling, and reproducible experiments. Give clear, actionable suggestions and explain trade-offs."
    ),
}

if not st.session_state.logged_in:
    st.error("You must be logged in to use the AI Chat Bot")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

with st.sidebar:
    st.header("AI Settings")
    # API key securely stored in Streamlit secrets
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.warning("No API key found in secrets. Please add it to .streamlit/secrets.toml")
    model = st.text_input("Model", value="gpt-4o-mini", help="Specify model name", key="ai_model")
    st.markdown("Select Specialist:")
    st.session_state.ai_role = st.radio("", list(PERSONAS.keys()), 
                                        index=list(PERSONAS.keys()).index(st.session_state.ai_role))

st.title("🤖 AI Chat Bot")
st.write(f"Specialist: **{st.session_state.ai_role}**")

if st.session_state.ai_chat_history:
    for msg in st.session_state.ai_chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
else:
    st.info("Start the conversation by typing a message below.")

with st.form("chat_form", clear_on_submit=False):
    user_input = st.text_area("Your message", placeholder="Ask the AI...", key="ai_input", height=120)
    col1, col2, col3 = st.columns([1,1,1])
    send = col1.form_submit_button("Send")
    clear = col2.form_submit_button("Clear Conversation")
    sample = col3.form_submit_button("Sample Prompt")

if clear:
    st.session_state.ai_chat_history = []
    st.experimental_rerun()

if sample:
    st.session_state.ai_chat_history.append({
        "role":"assistant",
        "content":"Try asking: 'How can I secure a public-facing web server?' "
                  "or 'What preprocessing steps for tabular ML would you recommend?'"
    })
    st.experimental_rerun()

if send and user_input:
    if not api_key:
        st.error("No API key configured. Please set it in secrets.")
    else:
        # Build messages
        system_msg = {"role": "system", "content": PERSONAS[st.session_state.ai_role]}
        history_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_chat_history]
        user_msg = {"role": "user", "content": user_input}
        messages = [system_msg] + history_msgs + [user_msg]

        try:
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(model=model, messages=messages)
            assistant_text = resp.choices[0].message.content
        except Exception as e:
            st.error(f"API request failed: {e}")
            assistant_text = None

        # Append to history
        st.session_state.ai_chat_history.append({"role":"user", "content": user_input})
        if assistant_text:
            st.session_state.ai_chat_history.append({"role":"assistant", "content": assistant_text})

        st.experimental_rerun()

st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")
import base64
import io
import os
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import errors, types
from PIL import Image

MASCOT = Image.open(Path(__file__).parent / "mascot.png")

MODEL = "gemini-3.5-flash-lite"  # small, fast model with a free tier
MAX_HISTORY = 10  # only send the last N messages to keep requests small

SYSTEM_PROMPT = """You are Kitchen Helper, a friendly assistant that answers basic
food and cooking questions: substitutions, cooking times, simple recipes, storage,
and food safety.

Rules:
- Keep answers short and practical (under 120 words unless a recipe is requested).
- If a question is not about food or cooking, politely decline and steer the user
  back to food topics.
- For food-safety questions (leftovers, raw meat, allergies), give standard safe
  guidance and suggest checking official sources for anything serious.
- If you are unsure, say so instead of guessing.
"""

# --- Mascot animation -------------------------------------------------------
# CSS keyframes: "idle" = gentle wave/sway, "busy" = bouncing while the bot thinks.
MASCOT_CSS = (
    "<style>"
    "@keyframes mascot-wave{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}"
    "@keyframes mascot-bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}"
    ".mascot{width:110px;transform-origin:50% 90%;}"
    ".mascot.idle{animation:mascot-wave 2.4s ease-in-out infinite;}"
    ".mascot.busy{animation:mascot-bounce 0.5s ease-in-out infinite;}"
    "@media (prefers-reduced-motion: reduce){.mascot{animation:none !important;}}"
    "</style>"
)


@st.cache_data
def mascot_base64():
    """Turn the image into text so it can be embedded directly in the page's HTML."""
    buffer = io.BytesIO()
    MASCOT.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def show_mascot(slot, busy=False):
    """Draw the mascot in `slot`, waving normally or bouncing when busy."""
    mood = "busy" if busy else "idle"
    slot.markdown(
        f'{MASCOT_CSS}<img class="mascot {mood}" '
        f'src="data:image/png;base64,{mascot_base64()}" alt="Kitchen Helper mascot">',
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Kitchen Helper", page_icon=MASCOT)

title_col, img_col = st.columns([4, 1])
with title_col:
    st.title("Kitchen Helper")
    st.caption("Ask me about substitutions, cooking times, simple recipes, and food safety.")
with img_col:
    mascot_slot = st.empty()  # a reserved spot we can redraw later
    show_mascot(mascot_slot)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Set the GEMINI_API_KEY environment variable, then restart the app.")
    st.stop()

client = genai.Client(api_key=api_key)


def build_contents(messages):
    """Convert our chat history into the format Gemini expects (roles: user / model)."""
    recent = messages[-MAX_HISTORY:]
    while recent and recent[0]["role"] != "user":  # history must start with the user
        recent = recent[1:]
    return [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in recent
    ]


def stream_reply(messages):
    """Yield the reply in small text pieces so Streamlit can show it as it arrives."""
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents=build_contents(messages),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=500,
        ),
    ):
        if chunk.text:
            yield chunk.text

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Try asking")
    st.write("- What can I use instead of buttermilk?")
    st.write("- How long do I boil eggs?")
    st.write("- Dinner idea with chicken and rice?")
    st.write("- How long does cooked rice last in the fridge?")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

def avatar_for(role):
    return MASCOT if role == "assistant" else None


for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_for(msg["role"])):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a food question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    show_mascot(mascot_slot, busy=True)  # bounce while the answer is being written
    with st.chat_message("assistant", avatar=MASCOT):
        try:
            reply = st.write_stream(stream_reply(st.session_state.messages))
            if not reply:
                reply = "Sorry, I couldn't come up with an answer. Try rephrasing your question."
                st.markdown(reply)
        except errors.APIError:
            reply = "Sorry, I couldn't reach the AI service. Please try again in a moment."
            st.markdown(reply)
    show_mascot(mascot_slot)  # back to the gentle wave

    st.session_state.messages.append({"role": "assistant", "content": reply})

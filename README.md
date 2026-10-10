# Kitchen Helper

<img src="mascot.png" width="120" alt="Kitchen Helper mascot: a chef avocado holding a whisk">

A small Streamlit chatbot that answers basic food and cooking questions using Google's Gemini API.

## Features
- Answers questions about substitutions, cooking times, simple recipes, and food safety
- System prompt keeps the bot on topic and politely declines non-food questions
- Streaming responses and a short conversation memory (last 10 messages)
- Graceful error handling if the API is unavailable
- Custom mascot used as the page icon, header image, and chat avatar
- Animated mascot (CSS): gently waves when idle and bounces while the bot is answering

## Tech
Python, Streamlit, Google Gemini API (google-genai), Pillow

## Run it
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
streamlit run app.py
```

## Test questions I used
- What can I substitute for buttermilk?
- How long do I boil eggs for a soft yolk?
- Dinner idea with chicken and rice?
- How long does cooked rice last in the fridge?
- Who won the hockey game last night? (should be declined as off-topic)

## What I'd add next
- Save chat history to a file
- Add a small recipe database the bot can look up (retrieval)
- Deploy on Streamlit Community Cloud

# requires having Ollama and having downloaded llama3.2 from Ollama
# first create a virtual environment and activate it (using python venv or conda)
# then do python -m pip install streamlit langchain geopy langchain_ollama
# then run python -m streamlit run test6.py

import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from geopy.geocoders import Nominatim
import random

st.set_page_config(page_title="VISTAA", layout="centered")
st.title("VISTAA")

llm = OllamaLLM(model="llama3.2")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vistaa_stage" not in st.session_state:
    st.session_state.vistaa_stage = 0

if "name_str" not in st.session_state:
    st.session_state.name_str = ""

if "crop_str" not in st.session_state:
    st.session_state.crop_str = ""

if "location_str" not in st.session_state:
    st.session_state.location_str = ""

if "location_good" not in st.session_state:
    st.session_state.location_good = False

if "latitude" not in st.session_state:
    st.session_state.latitude = 0.0

if "longitude" not in st.session_state:
    st.session_state.longitude = 0.0

if "ready_for_sim" not in st.session_state:
    st.session_state.ready_for_sim = False

if "context" not in st.session_state:
    st.session_state.context = ""

greeting_variants = [
    "Hey there! I'm VISTAA, your crop growth simulation assistant. What’s your name?",
    "Hi! I'm your agriculture simulation assistant, VISTAA. What should I call you?",
    "Hello! I'm an agriculture simulation assistant called VISTAA. Before we get started, can you tell me your name?",
    "Nice to meet you! I'm VISTAA, a crop simulation assistant. What's your name?",
    "Hi there, I'm VISTAA, an agriculture simulation assistant! I'm ready to help you grow your crops. First, your name?"
]

confirmation_done_variants = [
    "Got it, I have everything I need to start the crop simulation.",
    "Perfect, I've logged all the details. I will let you know when the simulation is complete!",
    "Awesome, I'm ready to simulate options for your crop!",
    "Great, all the information is in. Let's run some simulations.",
    "Nice! I've got all the information I need. I'll run some simulations and tell you when I'm done."
]

def get_crop_question_variants(name=None):
    base = [
        "What crop are you planning to grow?",
        "What crop are you growing this season?",
        "Which crop do you want help with?",
        "Tell me, what crop are you planning to grow?",
        "Is there a specific crop you want recommendations for?"
    ]
    if name:
        base += [
            f"And what crop are you thinking about growing, {name}?",
            f"{name}, what crop would you like to grow this season?",
            f"Nice to meet you! Now tell me what crop you're growing, {name}.",
        ]
    return base

def get_location_question_variants(name=None):
    base = [
        "Where are you planning to grow this crop? Let me know the city, state, and country.",
        "What's the location for your planting site? Please tell me the city, state, and country.",
        "Can you tell me where you'll be growing your crops? I'll need your city, state, and country.",
        "Where is your planting site located? Your city, state, and country should be good!",
        "And what city, state, and country will you be growing your crops in?"
    ]
    if name:
        base += [
            f"And where will you be growing your crops, {name}? Please let me know the city, state, and country.",
            f"Got it! Now where are you planting, {name}? I'll need your city, state, and country.",
            f"{name}, could you let me know the city, state, and country where you will be growing your crops?",
        ]
    return base

# def likely_correction(text):
#     triggers = ["actually", "i meant", "not", "sorry", "correction", "oops", "my bad", "wait", "incorrect", "wrong"]
#     return any(t in text.lower() for t in triggers)

def extract_with_llm(prompt_template, input_text, context=""):
    chain = ChatPromptTemplate.from_template(prompt_template) | llm
    result = chain.invoke({"input": input_text, "context": context})
    return result.strip().strip('"')

if st.session_state.vistaa_stage == 0:
    with st.spinner("Starting up..."):
        greeting_prompt = ChatPromptTemplate.from_template(
            "You are a friendly assistant named VISTAA who runs agriculture simulations to provide recommendations for growing different types of crops. Introduce yourself and your purpose briefly, then ask for their name to start though you don't need to justify your request. "
            "Greet the user warmly and ask them for their name. Remember to ask them for their name specifically. Please do not forget to ask for their name. Do not be redundant. Keep it very short, to the point, and friendly. Never say Don't Worry to the user. Be simple. Don't be mean or nitpicky or aggresive."
        )
        greeting_chain = greeting_prompt | llm
        greeting_result = greeting_chain.invoke({})
        greeting = greeting_result.content if hasattr(greeting_result, "content") else str(greeting_result)
        greeting = greeting.strip()
        if greeting.startswith('"') and greeting.endswith('"'):
            greeting = greeting[1:-1]
    
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.vistaa_stage += 1

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    print(user_input)
    print(st.session_state.vistaa_stage)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    context = st.session_state.context
    name = st.session_state.name_str.replace("User's name is: ", "").strip() if st.session_state.name_str else None

    if st.session_state.vistaa_stage == 1:
        name_prompt = "Extract the user's first name from the message: 'nice to meet you. my first name is {input}'\nOnly return the name or 'Unknown'. This is the conversation so far:\n{context}"
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Thinking..."):
                name_candidate = extract_with_llm(name_prompt, user_input, context)
                if name_candidate.lower() != "unknown" and len(name_candidate.split(" ")) <= 3:
                    print(name_candidate)
                    st.session_state.name_str = f"User's name is: {name_candidate}"
                    crop_q = random.choice(get_crop_question_variants(name_candidate))
                    response_placeholder.markdown(crop_q)
                    st.session_state.messages.append({"role": "assistant", "content": crop_q})
                    st.session_state.vistaa_stage = 3
                else:
                    fallback_prompt = ChatPromptTemplate.from_template("""
                    You are VISTAA, a friendly agricultural assistant. You're trying to learn the user's name. Talk with the user with the objective of learning their name and ask questions as necessary. Do not ask unrelated questions or discuss unrelated details.
                    Don't be mean or nitpicky or aggresive. Do not make any commentary at all about the user's name. Just confirm or clarify.
                    Conversation so far:
                    {context}
                    User: {question}
                    Assistant:
                    """)
                    reply = (fallback_prompt | llm).invoke({"context": context, "question": user_input})
                    response_placeholder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.session_state.context += f"\nUser: {user_input}\nAI: {reply}"

    elif st.session_state.vistaa_stage == 3:
        crop_prompt = "Extract the name of a specific crop from the message: 'I want to grow this crop: {input}'\nOnly return the full crop name (e.g., cremini mushrooms, wild thyme, French grapes, cherry tomatoes, etc.) or 'Unknown' if no crop is mentioned/the crop listed is not something that can be grown. Do not neglect descriptors if they are provided. Also, if the user says a crop that doesn't make sense, return 'Unknown'. If you observe any crop, please return its name. This is the conversation so far:\n {context}"
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Thinking..."):
                crop = extract_with_llm(crop_prompt, user_input, context)
                print(crop)
                if crop.lower() != "unknown" and len(crop.split(" ")) <= 3:
                    st.session_state.crop_str = f"User is growing this crop: {crop}"
                    loc_q = random.choice(get_location_question_variants(name))
                    response_placeholder.markdown(loc_q)
                    st.session_state.messages.append({"role": "assistant", "content": loc_q})
                    st.session_state.vistaa_stage = 5
                else:
                    fallback_prompt = ChatPromptTemplate.from_template("""
                    You are VISTAA, a helpful agriculture simulation assistant talking with the user about what crop they want to grow. If they have mentioned a crop, quickly clarify that you have the right crop. Talk to the user identify what crop they want to grow, asking follow ups as necessary. Don't discuss other details except what crop they want to grow. If you think you know, just ask for confirmation. Refrain from questioning the user or asking unrelated questions about temeprature, growing conditions, climates, etc.
                    Don't be mean or nitpicky or aggresive.
                    Conversation so far:
                    {context}
                    User: {question}
                    Assistant:
                    """)
                    reply = (fallback_prompt | llm).invoke({"context": context, "question": user_input})
                    response_placeholder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.session_state.context += f"\nUser: {user_input}\nAI: {reply}"

    elif st.session_state.vistaa_stage == 5:
        loc_prompt = "Extract a geocodable city, state, and country from: '{input}'\nReturn full location in the format 'City, State, Country' (just comma separated, no other formatting) or 'Unknown'. Please only return the location with normal comma formatting, no other details or justification."
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Thinking..."):
                location = extract_with_llm(loc_prompt, user_input, context)
                print(location)
                if location.lower() != "unknown" and len(location.split(",")) >= 2:
                    geo = Nominatim(user_agent="vistaa-agent").geocode(location)
                    if geo:
                        st.session_state.location_str = f"User's location is: {location}"
                        st.session_state.latitude = geo.latitude
                        st.session_state.longitude = geo.longitude
                        st.session_state.location_good = True
                        final_msg = random.choice(confirmation_done_variants)
                        response_placeholder.markdown(final_msg)
                        st.session_state.messages.append({"role": "assistant", "content": final_msg})
                        st.session_state.ready_for_sim = True
                        st.session_state.vistaa_stage = 6
                        print(geo)
                    else:
                        fallback_prompt = ChatPromptTemplate.from_template("""
                        You're talking with the user to understand their crop growing location (city, state, country) so you can help simulate growing conditions. Their location needs to be complete so it can be geocoded. Ask the user follow-up questions as needed. Address the user directly.
                        Don't be mean or nitpicky or aggresive.
                        Conversation so far:
                        {context}
                        User: {question}
                        Assistant:
                        """)
                        reply = (fallback_prompt | llm).invoke({"context": context, "question": user_input})
                        response_placeholder.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.session_state.context += f"\nUser: {user_input}\nAI: {reply}"
                else:
                    fallback_prompt = ChatPromptTemplate.from_template("""
                    You're talking with the user to understand their crop growing location (just city, state, country, nothing else) so you can help simulate growing conditions. Their location needs to be complete. Ask follow-up questions if needed to complete the location, but don't ask much beyond the city, state, and country.
                    Don't be mean or nitpicky or aggresive.
                    Conversation so far:
                    {context}
                    User: {question}
                    Assistant:
                    """)
                    reply = (fallback_prompt | llm).invoke({"context": context, "question": user_input})
                    response_placeholder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.session_state.context += f"\nUser: {user_input}\nAI: {reply}"

    elif st.session_state.vistaa_stage >= 6:
        final_prompt = ChatPromptTemplate.from_template("""
        You are VISTAA, a helpful agricultural assistant. You already know:
        {name_str}
        {crop_str}
        {location_str}
        Continue the conversation naturally and answer the user's questions, asking follow ups and providing recommendations as needed.

        Conversation history:
        {context}

        User: {question}
        Assistant:
        """)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Thinking..."):
                response = (final_prompt | llm).invoke({
                    "question": user_input,
                    "context": context,
                    "name_str": st.session_state.name_str,
                    "crop_str": st.session_state.crop_str,
                    "location_str": st.session_state.location_str
                })
                answer = response.content if hasattr(response, "content") else str(response)
                response_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.context += f"\nUser: {user_input}\nAI: {answer}"


# next steps:
# more robust input validation
# confirmation at the end + ability to edit information inputted before proceeding to simulation
# more natural variants for crop and location question (maybe turn this into LLM generated)
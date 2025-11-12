import os
import streamlit as st
from typing import TypedDict, List, Dict
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# configuration
# connect to groq

try:
    groq_api_key= st.secrets['GROQ_API_KEY']

except (KeyError, AttributeError):
    # fallback for local development
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ API KEY not found.Please set it in your Streamlit secrets or .env file")
    st.stop()


llm = ChatGroq(model="llama-3.1-8b-instant")

# prompt template & chain
prompt = ChatPromptTemplate.from_template("""
You are a helpful support assistant.
Classify the question into one of these categories:
- Billing
- Technical Support
- General Inquiry

Then respond with a short, polite message.
Question: {question}
""")

chain = prompt | llm

test_output = chain.invoke({"question": "My payment is not going through, what should I do?"})
print(test_output.content)


# classification and detection logic
class Category(TypedDict):
    name: str
    keywords: List[str]
    response: str

categories: List[Category] = [
    {
        "name": "Billing",
        "keywords": ["payment", "invoice", "bill", "charge"],
        "response": "For billing questions, please check your account settings or contact billing support."
    },
    {
        "name": "Technical Support",
        "keywords": ["error", "problem", "not working", "issue"],
        "response": "Please try restarting your device. If the problem persists, contact technical support."
    },
    {
        "name": "General Inquiry",
        "keywords": ["hours", "location", "contact"],
        "response": "Our business hours are 9 AM to 5 PM, Monday to Friday."
    }
]

# classification
def classify_question(question: str, categories: List[Category]) -> str:
    question_lower = question.lower()
    category_scores: Dict[str, int] = {}

    for category in categories:
        score = sum(keyword in question_lower for keyword in category["keywords"])
        category_scores[category["name"]] = score

    best_match = max(category_scores, key=lambda k:category_scores[k])

    if category_scores[best_match] == 0:
        return "Unknown"

    return best_match

# frustration detection
frustration_keywords = ["angry", "frustrated", "not happy"]

def check_frustration(text: str) -> bool:
    return any(word in text.lower() for word in frustration_keywords)

def format_history(chat_history):
    """
    Turns chat_history list into a single formatted string.
    Example:
    User: Hello
    Bot: Hi there!
    """
    return "\n".join(f"{speaker.capitalize()}: {text}" for speaker, text in chat_history)

# streamlit ui
st.title("Customer Support Chatbot")
st.caption("Using keyword classification and Groq LLM for support responses.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt_input := st.chat_input("Ask a question about billing, technical issues, or general inquiries..."):
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Prepare for bot response
    with st.chat_message("assistant"):
        # The Streamlit flow (replacing the 'while True' loop)
        
        # 1. Frustration Check
        if check_frustration(prompt_input):
            category = classify_question(prompt_input, categories)
            response = f"I can see this is frustrating. I'll connect you to a human in **{category}** support."
        else:
            # 2. Category Check
            category = classify_question(prompt_input, categories)
    
            if category == "Unknown":
                # 3. LLM Path (for unclassified questions)
                # Filter st.session_state.messages to create a simple history for the LLM
                simple_history = [(m['role'], m['content']) for m in st.session_state.messages]
                
                # The latest user input is already in simple_history, but we format the *entire* history
                full_context = format_history(simple_history)

                # Use the chat history as the 'question' input for the chain
                llm_prompt = (
                    f"The following is a conversation between a user and a helpful chatbot.\n"
                    f"{full_context}\n"
                    f"Bot:"
                )
                
                llm_response = chain.invoke({"question": llm_prompt})
                response = llm_response.content
            else:
                # 4. Keyword Path (pre-defined response)
                response = next(c["response"] for c in categories if c["name"] == category)

        # Display bot response and add to history
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

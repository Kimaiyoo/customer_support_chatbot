# 🤖 Customer Support Chatbot

A lightweight customer support chatbot using **LangChain** and **Groq**.  
It classifies questions into categories (Billing, Technical Support, General Inquiry), provides predefined responses, and escalates when frustration is detected.

---

## 🚀 Features

- Classifies questions into **Billing**, **Technical Support** or **General Inquiry**.
- Uses **keyword matching** for fast classification.
- Falls back to **Groq LLM** for more natural responses.
- Detects frustration words (e.g., _angry_, _frustrated_) and suggests escalation.
- Maintains simple conversation history.

---

## 🛠️ Setup

```bash
git clone https://github.com/Kimaiyoo/customer_support_chatbot.git
cd customer_support_chatbot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with:

```env
GROQ_API_KEY=your_api_key_here
```

## 📌 Next Steps

- Add better sentiment analysis.
- Store chat history in a database.
- Explore adding a web UI later.

## 📝 License

MIT License.

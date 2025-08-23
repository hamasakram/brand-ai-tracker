**🤖 Brand Tracker – Gemini + Sentiment Analysis**

A Streamlit-powered application that analyzes brand mentions and sentiment using Google Gemini AI.
Upload your brand definitions and prompts in YAML format, run AI-powered analysis, and export the results to CSV – all in a clean, interactive interface.

**✨ Features**
📂 Upload YAML files (brands.yaml & prompts.yaml) directly in the app.
🔍 Brand Mentions Analysis – detect how often a brand and its competitors are mentioned.
😊 Sentiment Analysis – classify responses as positive, neutral, or negative.
📊 Interactive Results Table – view and explore all analysis results.
📥 Export to CSV – download results with sentiment scores and mentions.
🖥️ Streamlit UI – clean, modern, and easy-to-use interface.


**📋 YAML File Format**
brands.yaml
brands:
  - canonical: "Acme"
    variants: ["Acme Inc", "AcmeCo"]
    competitors: ["Globex", "Umbrella"]

prompts.yaml
prompts:
  - id: "top_brands"
    text: "What are the best project management software brands in 2025?"

**🚀 How to Run**
1) Clone the repository
2) git clone https://github.com/your-username/brand-tracker.git
3) cd brand-tracker
4) Install dependencies
5) pip install -r requirements.txt
6) Set up your Gemini API Key
7) export GEMINI_API_KEY="your_api_key_here"


(Windows CMD: set GEMINI_API_KEY=your_api_key_here)

8) Run the Streamlit app

streamlit run app.py

**📦 Requirements**
Python 3.9+
Streamlit
Google Generative AI SDK
PyYAML
Pandas
TextBlob (or Transformers for advanced sentiment)

Install all via:

pip install -r requirements.txt

**📜 License**
This project is licensed under the MIT License.

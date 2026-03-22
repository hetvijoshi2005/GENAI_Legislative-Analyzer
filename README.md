# ⚖️ AI Legislative Analyzer
**CogniCode | Intel GenAI for GenZ Challenge**

CogniCode is an AI-powered dashboard designed to bridge the gap between complex legal jargon and everyday citizens. By leveraging LLMLingua-2, it simplifies dense legislative documents into role-specific, accessible summaries for students, farmers, businesses, and senior citizens.
# 🛠️ Quick Start & Installation
To run this project locally, execute the following commands in your terminal:

*1. Create and activate a virtual environment*

python -m venv venv

.\venv\Scripts\activate  # Windows

*2. Install all required dependencies*

pip install streamlit llmlingua googletrans==4.0.0-rc1 legacy-cgi torch transformers

pip install streamlit-authenticator==0.3.3

*3. Launch the application*

streamlit run app.py

# 🌟 Key Features
*Context-Aware Summarization:* Uses LLMLingua-2 (BERT-based) to compress legal text by up to 95% while retaining core meaning.

*Multilingual Support:* Instant translation into Hindi and Marathi using the Google Translate API.

*Persona-Based Insights:* Tailors analysis based on the user's role, such as highlighting student benefits or farmer impacts.

*User-Friendly Interface:* A secure, 3-step guided process built with Streamlit and integrated authentication.

# 🛠️ Tech Stack
Frontend: Streamlit

AI Compression: Microsoft LLMLingua-2 (Small & Fast BERT-base)

Translation: Googletrans (4.0.0-rc1)

Database: SQLite3

Language: Python 3.12+

# 📁 Project Structure
app.py: Main Streamlit application and AI logic.

requirements.txt: List of dependencies and version fixes (including legacy-cgi for Python 3.13+ compatibility).

venv/: Local virtual environment (ignored by Git).
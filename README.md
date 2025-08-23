📚 QuizForge

AI-powered Quiz Generator that transforms your documents, articles, or notes into interactive quizzes within seconds.

🚀 Features

📄 Upload Documents – Supports PDF, DOCX, and text files

🤖 AI Quiz Generation – Uses Google Gemini API to create smart, contextual questions

🎯 Customizable Quizzes – Choose difficulty level and question style

🎨 Interactive UI – Built with Streamlit for a smooth experience

☁️ Deploy-Ready – Pre-configured for Replit, Render, and other platforms

🛠️ Tech Stack

Python 3.9+

Streamlit – Frontend web framework

Gemini API – AI quiz generation

pdfplumber / python-docx – File parsing

Replit / Render – Deployment ready

📂 Project Structure
QuizForge/
│── app.py                # Main Streamlit app  
│── quiz_generator.py     # Core quiz logic  
│── gemini_quiz_generator.py # AI integration  
│── file_processor.py     # Document parsing  
│── requirements.txt      # Dependencies  
│── DEPLOYMENT_GUIDE.txt  # Hosting instructions  
│── .streamlit/config.toml # UI settings  

⚡ Quick Start

Clone the repo

git clone https://github.com/your-username/QuizForge.git
cd QuizForge


Install dependencies

pip install -r requirements.txt


Set up environment
Create a .env file with your API key:

GEMINI_API_KEY=your_api_key_here


Run the app

streamlit run app.py

🌐 Deployment

Replit – Works out of the box (.replit + Procfile included)

Render/Heroku – Use requirements.txt & Procfile

Docker – Add a simple Dockerfile for containerization

🎯 Use Cases

Teachers creating quizzes from lecture notes

Students revising study material

Content creators building interactive learning tools

Anyone who wants quick practice questions from reading material

🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss your ideas.

📜 License

MIT License – feel free to use and modify.

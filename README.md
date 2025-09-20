# 🎓 AI-Powered Chatbot for Career Guidance

Welcome to the official repository for the **AI-powered career guidance chatbot**, built with **Django** (Python) for the backend and **HTML/CSS/JavaScript** for the frontend. This project aims to democratize access to high-quality career advice using artificial intelligence, machine learning, and natural language processing (NLP).

🔗 **Live Demo:** [careercounsellor.pythonanywhere.com]

---

## 🧠 Project Overview

The goal of this project is to design and implement an AI chatbot that can:
- Converse with users in natural language
- Understand their interests, skills, and academic background
- Recommend career paths, jobs, or educational resources
- Provide scalable and personalized guidance 24/7

---

## 🔧 Tech Stack

**Frontend:**
- HTML5
- CSS3 (with Bootstrap for styling)
- JavaScript (Vanilla)

**Backend:**
- Python 3.x
- Django Framework
- Django REST Framework (for API handling)

**Database:**
- SQLite (Development)
- PostgreSQL (Production-ready alternative)

**AI/NLP:**
- GitHub Azure OpenAI API (for natural language processing and intent detection)

**Deployment:**
- PythonAnywhere (Production Hosting)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/oladokedamilola/ai-career-chatbot.git
cd ai-career-chatbot

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run initial migrations
python manage.py migrate

# Start development server
python manage.py runserver
````

---

## 📁 Project Structure

```
career_chatbot/
├── chatbot/                # Core app with chat logic, NLP, recommendation engine
├── templates/              # HTML templates (chatbot UI)
├── static/                 # CSS and JS files
├── db.sqlite3              # Development database
├── manage.py
└── requirements.txt
```

---

## 📌 Features (Implemented & Planned)

* [x] Django project setup
* [x] Integration with GitHub Azure OpenAI API
* [x] Frontend chat UI (responsive with Bootstrap)
* [x] AI recommendation system for career paths
* [x] Deployment on PythonAnywhere
* [x] User profiles & authentication


---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## 👤 Author

**Damilola Oladoke**
🔗 [GitHub Profile](https://github.com/oladokedamilola)

---

## 💡 Contributing

Pull requests are welcome! If you'd like to contribute, fork the repository and make your changes, then submit a pull request.

---

## 📬 Contact

For questions or feedback, feel free to open an issue or reach out via GitHub.

```

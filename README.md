# 🎓 AI Personalized Learning Platform

An intelligent, adaptive learning platform that delivers personalized educational content using AI/ML algorithms to assess learner capabilities and curate customized learning paths.

## 📋 Overview

The AI Learning System is a Django-based web application designed to revolutionize online education by moving beyond generic content delivery. The platform intelligently assesses learner performance through dynamic quizzes and generates personalized curricula tailored to individual learning needs and pace.

## ✨ Key Features

- **Adaptive Assessment**: Dynamic quiz generation based on learner performance
- **Personalized Learning Paths**: AI-driven curriculum recommendations
- **Quiz Management**: Automated quiz creation and evaluation system
- **User Authentication**: Secure registration and login functionality
- **Performance Analytics**: Track learner progress and generate insightful reports
- **Resource Curation**: Aggregated free learning resources from multiple sources
- **Responsive UI**: Clean, accessible interface across devices

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: (Configured in settings.py)
- **AI/ML**: Hugging Face Transformers, scikit-learn
- **Additional**: Python virtual environment, pip

## 📁 Project Structure

```
adaptlearn/
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore rules
│
├── adaptlearn/              # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
├── core/                    # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── serializers.py       # DRF serializers
│   ├── admin.py             # Django admin configuration
│   ├── urls.py              # App-level routing
│   ├── utils.py             # Utility functions
│   ├── quiz_generator.py    # Quiz generation logic
│   ├── evaluator.py         # Performance evaluation engine
│   └── migrations/          # Database migrations
│
├── static/
│   ├── css/
│   │   └── style.css        # Application styling
│   └── js/
│       ├── auth.js          # Authentication logic
│       ├── quiz.js          # Quiz functionality
│       └── results.js       # Results display
│
└── templates/
    ├── base.html            # Base template
    ├── index.html           # Home page
    ├── register.html        # Registration page
    ├── login.html           # Login page
    ├── profile.html         # User profile
    ├── courses.html         # Course listing
    ├── assessment.html      # Assessment page
    └── results.html         # Results page
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment tool

### Step 1: Clone Repository

```bash
git clone https://github.com/Mirdula18/AI-Learning-System.git
cd AI-Learning-System
cd adaptlearn
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root and configure:

```env
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=your_database_url
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 📖 Usage

### For Learners

1. **Register** an account on the platform
2. **Complete Initial Assessment** to establish baseline knowledge
3. **View Personalized Dashboard** with recommended courses
4. **Take Adaptive Quizzes** that adjust difficulty based on performance
5. **Review Results** and track progress over time
6. **Access Curated Resources** tailored to learning gaps

### For Administrators

1. Access **Django Admin Panel** at `/admin`
2. Manage user accounts and course content
3. Monitor learner analytics and performance metrics
4. Update quiz templates and assessment criteria

## 🧩 Core Components

### Quiz Generator (`quiz_generator.py`)

Automatically generates quizzes based on:
- Course content
- Learner proficiency levels
- Previous assessment results
- Topic-specific difficulty calibration

### Evaluator (`evaluator.py`)

Assesses learner performance through:
- Real-time score calculation
- Skill gap identification
- Recommendation engine for next learning modules
- Performance trend analysis

### Models (`models.py`)

Key data models include:
- User
- Course
- Quiz
- Assessment
- LearningPath structures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

zed education

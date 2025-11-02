Folder Structure: 

adaptlearn/
│
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
│
├── adaptlearn/                 # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                       # Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── utils.py
│   ├── quiz_generator.py
│   ├── evaluator.py
│   └── migrations/
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js
│       ├── quiz.js
│       └── results.js
│
└── templates/                  # HTML templates
    ├── base.html
    ├── index.html
    ├── register.html
    ├── login.html
    ├── profile.html
    ├── courses.html
    ├── assessment.html
    └── results.html

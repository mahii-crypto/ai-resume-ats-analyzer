# Resume ATS Analyzer — Django Backend

Converted from the original Express/Mongoose (MERN) backend to **Django + Django REST Framework**.

---

## Project Structure

```
django_backend/
├── core/                    # Project config (replaces index.js + conn.js)
│   ├── settings.py
│   ├── urls.py              # Root URL router
│   └── wsgi.py
├── resume_ats/              # Main app
│   ├── models.py            # User + Resume (replaces Models/)
│   ├── serializers.py       # JSON serializers (new in DRF)
│   ├── views/
│   │   ├── user.py          # replaces Controllers/user.js
│   │   ├── resume.py        # replaces Controllers/resume.js
│   │   └── chatbot.py       # replaces Controllers/ChatBot.js
│   └── urls/
│       ├── user.py          # replaces Routes/user.js
│       ├── resume.py        # replaces Routes/resume.js
│       └── chatbot.py       # replaces Routes/ChatBot.js
├── manage.py
├── requirements.txt
└── .env.example
```

---

## MERN → Django Mapping

| MERN (Express)             | Django Equivalent                        |
|---------------------------|------------------------------------------|
| `express` + `cors`        | Django + `django-cors-headers`           |
| `mongoose` + MongoDB      | Django ORM + SQLite (or PostgreSQL)      |
| `Models/user.js`          | `resume_ats/models.py → User`            |
| `Models/resume.js`        | `resume_ats/models.py → Resume`          |
| `Controllers/*.js`        | `resume_ats/views/*.py`                  |
| `Routes/*.js`             | `resume_ats/urls/*.py`                   |
| `multer` (file upload)    | Django `request.FILES` (built-in)        |
| `pdf-parse`               | `pdfplumber`                             |
| `dotenv`                  | `python-dotenv`                          |
| `nodemon`                 | `python manage.py runserver`             |

---

## Setup

### 1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 4. Run migrations
```bash
python manage.py makemigrations resume_ats
python manage.py migrate
```

### 5. Start the development server
```bash
python manage.py runserver 3000
```

---

## API Endpoints

All endpoints are identical to the original Express API so the React frontend needs **no changes**.

| Method | Path                       | Description                      |
|--------|---------------------------|----------------------------------|
| GET    | `/api/health`             | Health check                     |
| POST   | `/api/user/`              | Register / login user            |
| POST   | `/api/resume/addResume`   | Upload PDF + analyze with Cohere |
| GET    | `/api/resume/<user>`      | Get user's resume history        |
| GET    | `/api/resume/admin/all`   | Get all resumes (admin)          |
| POST   | `/api/chat/`              | Chatbot (Cohere)                 |

---

## Switching to PostgreSQL

In `core/settings.py`, replace the `DATABASES` block:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

Then `pip install psycopg2-binary` and run `python manage.py migrate`.

---

## Production Deployment

```bash
pip install gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:3000
```

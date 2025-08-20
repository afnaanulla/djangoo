# Django API Backend

This project is a **Django + Django REST Framework (DRF)** backend with authentication and API endpoints.  
It is designed to serve as the backend for an Angular frontend application.

---

## 🚀 Features
- User authentication (register, login, logout).
- CSRF-protected API endpoints.
- JSON-based responses for easy frontend integration.
- CORS enabled for cross-origin requests.
- Deployed on **Render**.

---

## 🛠 Tech Stack
- **Backend Framework:** Django 5.x  
- **API Layer:** Django REST Framework  
- **Database:** SQLite (default, can switch to PostgreSQL/MySQL)  
- **Frontend (separate repo):** Angular 17  

---

## 📂 Project Structure
```core/
│── manage.py
│── core/ # Project settings & URLs
│── api/ # Main API app
│ ├── auth/ # Authentication routes
│ ├── models.py
│ ├── views.py
│ ├── serializers.py
│── requirements.txt
```
---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```
### 2. Create and activate virtual environment
``` 
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows
```
### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Apply migrations
```
python manage.py migrate
```
### 5. Run the development server
```
python manage.py runserver
```
## 🔑 API Endpoints
### CSRF Token GET /api/auth/csrf/ Returns a CSRF token.

### Register POST /api/auth/register/
```
Body: { 
 "username": "testuser",
 "password": "password123",
 "email": "eamil@eamil.com"
 }
```

### Login POST /api/auth/login/
```
Body: { 
 "username": "testuser",
 "password": "password123",
 "email": "eamil@eamil.com"
 }
```
### Data (Example Endpoint) GET /api/indicators/country=in&codes=ny.gdp.mktp.cd,sp.pop.totl&start=2000&end=2023

### Logout POST /api/auth/logout/
---
## 🌐 CORS & CSRF Notes

- CORS is enabled via django-cors-headers.

- CSRF tokens must be included for state-changing requests.
---

## 📦 Deployment Deployed using Render with Gunicorn.

- Static files handled via Whitenoise.

- Environment variables stored in .env.

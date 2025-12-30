# Custom Django Admin – Portfolio Project

A portfolio project showcasing advanced customization of the Django Admin interface, combining a Django backend with a modern JavaScript frontend to explore more flexible, scalable admin experiences beyond Django’s defaults.

This project focuses on **architecture, extensibility, and developer experience**, rather than purely visual changes.

---

## 🚀 Project Highlights

- Custom Django Admin extensions beyond default templates
- Clear separation between backend (Django) and frontend (JavaScript)
- Data modeling and admin configuration using real Django apps
- Scripted data generation for realistic testing scenarios
- Designed as an extensible foundation for complex internal tools

---

## 🧠 Why This Project Exists

Django Admin is powerful but opinionated.  
This project explores how to:

- Go beyond out-of-the-box admin behavior
- Prepare admin interfaces for complex business workflows
- Integrate frontend-driven experiences with Django-managed data
- Structure a Django project for future scalability and customization

This mirrors real-world internal tools where **admin panels evolve into full operational systems**.

---

## 🛠 Tech Stack

### Backend
- **Python**
- **Django**
- **SQLite** (local development)

### Frontend
- **JavaScript**
- **Node.js**
- **npm / yarn**

---

## 🧩 Architecture Overview

```text
custom-django-admin/
├── helloworld/          # Minimal Django app (sandbox / examples)
├── sample_app/          # Core app used to demonstrate admin customization
├── src/                 # Frontend source code
├── manage.py            # Django entry point
├── createFakeData.py    # Fake data generator for realistic admin testing
├── db.sqlite3           # Local development database
└── package.json         # Frontend tooling

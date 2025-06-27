# Invoice Management System

A robust, multi-tenant invoice management application built with Django and Django REST Framework. This system allows different admins to manage their own users, projects, and pricing securely.

## ✨ Key Features

- **Multi-Tenant Architecture:** Securely separates data between different `admin` users.
- **Role-Based Access Control:**
    - **Super Admin:** Can manage the entire system, including creating and overseeing admins.
    - **Admin:** Can manage their own team of users, client projects, and pricing.
    - **User:** Can only submit their daily work entries for assigned projects.
- **RESTful API:** A secure API built with Django REST Framework for all core functionalities.
- **JWT Authentication:** Secure token-based authentication for the API.
- **Excel Invoice Generation:** Dynamically generates professional invoices in `.xlsx` format based on work entries.
- **Professional Codebase:** Clean, well-documented, and professionally structured Python code.

## 🛠️ Technology Stack

- **Backend:** Python, Django
- **API:** Django REST Framework (DRF)
- **Database:** SQLite (for local development), PostgreSQL (for production)
- **Excel Handling:** Openpyxl
- **Deployment:** Ready for deployment on platforms like Render.com.

## 🚀 Local Setup and Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/aroyslipk/invoice-project.git](https://github.com/aroyslipk/invoice-project.git)
    cd invoice-project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```
    (After creating, use `python manage.py shell` to set the role to `super_admin`).

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## 👤 Author

**AnikRoy**
- **GitHub:** [@aroyslipk](https://github.com/aroyslipk)

---
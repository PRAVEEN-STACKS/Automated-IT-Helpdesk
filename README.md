# 🛠️ IT Helpdesk Ticket Management System

A full-stack web-based IT support ticketing system built for small organizations to manage IT complaints efficiently — replacing manual tracking with an automated, role-based workflow.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-MariaDB-orange?style=flat-square&logo=mysql)
![HTML CSS](https://img.shields.io/badge/HTML-CSS-red?style=flat-square&logo=html5)

---

## 📌 About the Project

Small IT teams often struggle to track and manage employee complaints manually via emails or spreadsheets. This project solves that by providing a structured, automated ticketing platform where:

- Employees can **report issues** and **track their ticket status**
- An **automated response** is sent instantly based on the issue type
- IT admins can **assign, update, and resolve** tickets from a central dashboard

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 User Authentication | Register and login with hashed passwords |
| 📝 Submit Tickets | Title, category, priority, and description |
| ⚡ Auto Responses | Keyword-based instant replies for common issues |
| 📊 Ticket Tracking | Real-time status — Open → In Progress → Resolved → Closed |
| 💬 Comments Thread | Users and admins can communicate per ticket |
| 🛡️ Role-Based Access | Separate User and Admin dashboards |
| 🔍 Admin Filters | Filter tickets by status, priority, and category |
| 👤 Admin Assignment | Assign tickets to specific IT staff |

---

## 🖥️ Screenshots

> *(Add screenshots of your login page, dashboard, submit form, and admin panel here)*

---

## 🗂️ Project Structure

```
helpdesk/
├── app.py                  ← Flask backend (routes, logic, auto-responses)
├── schema.sql              ← MySQL/MariaDB database schema + seed data
├── requirements.txt        ← Python dependencies
├── static/
│   ├── css/
│   │   └── style.css       ← Full dark-theme stylesheet
│   └── js/
│       └── main.js         ← Flash message auto-dismiss
├── templates/
│   ├── base.html           ← Shared layout with sidebar
│   ├── login.html          ← Login page
│   ├── register.html       ← Registration page
│   ├── dashboard.html      ← User ticket list
│   ├── submit.html         ← New ticket form
│   ├── ticket.html         ← Ticket detail + comments
│   └── admin.html          ← Admin panel with filters
└── README.md
```

---

## ⚙️ Tech Stack

- **Backend** — Python, Flask
- **Database** — MySQL / MariaDB
- **Frontend** — HTML, CSS, Jinja2 templating
- **Security** — Werkzeug password hashing, Flask session management

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL or MariaDB
- pip3

---

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/helpdesk.git
cd helpdesk
```

**2. Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

> On Kali Linux / Ubuntu:
> ```bash
> sudo apt install python3-flask python3-mysqldb libmariadb-dev -y
> pip3 install flask-mysqldb --break-system-packages
> ```

**3. Set up the database**
```bash
mysql -u root -p < schema.sql
```

**4. Configure your database password**

Open `app.py` and update:
```python
app.config["MYSQL_PASSWORD"] = "your_password_here"
```

**5. Run the application**
```bash
python3 app.py
```

Open your browser → **http://127.0.0.1:5000**

---

## 🔑 Default Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@helpdesk.local` | `Admin@123` |
| User | Register at `/register` | your choice |

> ⚠️ Change the default admin password before deploying to production.

---

## ⚡ Auto-Response Keywords

The system detects keywords in the ticket title and description to send instant replies:

| Keyword | Auto-Response |
|---|---|
| `network` | Network issue received, diagnosis within 2 hours |
| `password` | Password reset link sent to registered email |
| `hardware` | Technician will contact you to schedule a visit |
| `software` | Restart and update the application |
| `email` | Email issue will be resolved within 1 hour |
| *(default)* | IT team will respond within 4 business hours |

---

## 🔒 Security Notes

- Passwords are hashed using **Werkzeug's** `generate_password_hash`
- Role-based access is enforced on every route
- For production: set `SECRET_KEY` as an environment variable and disable `debug=True`

---

## 🌱 Future Improvements

- [ ] Email notifications on ticket updates (Flask-Mail)
- [ ] File attachments for tickets
- [ ] Dashboard analytics and charts
- [ ] SLA tracking and escalation alerts
- [ ] REST API for mobile app integration

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

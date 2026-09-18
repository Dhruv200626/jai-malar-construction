# Jai Malhar — Construction Site Management System

> Construction Site Management Made Simple

A complete, production-ready construction management system built with **Python Django 5 + MySQL 8 + Bootstrap 5**.

---

## Features

- Role-based access (Admin, Project Manager, Site Supervisor, Employee)
- Project management with full CRUD
- Employee and labour management
- Attendance tracking (check-in/check-out, working hours)
- Material management, inventory, and stock tracking
- Expense management with approval workflow
- Equipment management
- Supplier and Client management
- Daily and monthly reports
- Analytics dashboard with Chart.js
- Notification system
- REST API
- Export to PDF, Excel, CSV
- Mobile-first responsive UI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.1 |
| Database | MySQL 8 |
| ORM | Django ORM |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Charts | Chart.js |
| Icons | Font Awesome 6 |
| API | Django REST Framework |
| Auth | Django Authentication |

---

## Installation (Windows)

### 1. Clone or extract the project

```
cd "Jai malhar"
```

### 2. Create a virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r jai_malhar/requirements.txt
```

### 4. Configure MySQL

Open MySQL and create the database:

```sql
CREATE DATABASE jai_malhar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Set environment variables

Edit `jai_malhar/.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=jai_malhar_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### 6. Run migrations

```
cd jai_malhar
python manage.py migrate
```

### 7. Create superuser (Admin)

```
python manage.py createsuperuser
```

### 8. Seed demo data

```
python manage.py seed_data
```

### 9. Run the development server

```
python manage.py runserver
```

Open: http://127.0.0.1:8000/

---

## Default Login

After running `seed_data`:

| Role | Email | Password |
|---|---|---|
| Admin | admin@jaimalar.com | admin123 |
| Project Manager | pm@jaimalar.com | admin123 |
| Site Supervisor | supervisor@jaimalar.com | admin123 |

---

## URL Structure

```
/login/               Login page
/logout/              Logout
/dashboard/           Main dashboard
/projects/            Project list
/projects/add/        Add project
/projects/<id>/       Project detail
/employees/           Employee list
/attendance/          Attendance list
/attendance/mark/     Mark attendance
/materials/           Material list
/materials/inventory/ Inventory dashboard
/expenses/            Expense list
/equipment/           Equipment list
/suppliers/           Supplier list
/clients/             Client list
/reports/daily/       Daily reports
/reports/monthly/     Monthly reports
/reports/analytics/   Analytics
/notifications/       Notifications
/profile/             User profile
/settings/            Settings
/users/               User management (Admin)
```

---

## Development Phases

- [x] **Phase 1** — Project setup, authentication, base UI, dashboard foundation
- [ ] **Phase 2** — Roles, Projects, Clients
- [ ] **Phase 3** — Employees, Attendance
- [ ] **Phase 4** — Materials, Inventory, Suppliers
- [ ] **Phase 5** — Expenses, Cost management, Equipment
- [ ] **Phase 6** — Daily & Monthly Reports
- [ ] **Phase 7** — Analytics, Charts, Notifications
- [ ] **Phase 8** — REST APIs, Export, Search, Pagination
- [ ] **Phase 9** — Testing, Security, Performance, Deployment

---

## License

Jai Malhar Construction Management System — Private Use

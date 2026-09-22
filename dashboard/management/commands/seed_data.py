"""
python manage.py seed_data

Seeds the Jai Malhar database with realistic demo data:
  - 4 roles
  - 1 admin + 3 staff users
  - 5 clients
  - 5 suppliers
  - 15 materials
  - 4 projects
  - 30 employees / workers
  - 200+ attendance records
  - 15 equipment items
  - 60 expenses
  - 20 daily reports
  - material transactions
"""

import random
from datetime import date, timedelta, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed the database with realistic demo data for Jai Malhar"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing data before seeding (keeps admin user)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n🏗  Jai Malhar — Seeding Demo Data\n"))

        if options['clear']:
            self._clear_data()

        self._seed_roles()
        self._seed_users()
        self._seed_clients()
        self._seed_suppliers()
        self._seed_materials()
        projects = self._seed_projects()
        employees = self._seed_employees(projects)
        self._seed_attendance(employees, projects)
        self._seed_equipment(projects)
        self._seed_expenses(projects)
        self._seed_material_transactions(projects)
        self._seed_daily_reports(projects)

        self.stdout.write(self.style.SUCCESS("\n✅  Seed complete! Login at http://127.0.0.1:8000/\n"))
        self.stdout.write("   Email    : admin@jaimalar.com")
        self.stdout.write("   Password : admin123\n")

    # ── Helpers ──────────────────────────────────────────────────────
    def _rdate(self, start_days_ago, end_days_ago=0):
        """Random date between two day offsets from today."""
        today = date.today()
        d1 = today - timedelta(days=start_days_ago)
        d2 = today - timedelta(days=end_days_ago)
        delta = (d2 - d1).days
        return d1 + timedelta(days=random.randint(0, max(delta, 0)))

    def _clear_data(self):
        self.stdout.write("  Clearing existing data...")
        from reports.models import DailyReport
        from attendance.models import Attendance
        from expenses.models import Expense
        from materials.models import MaterialTransaction, Material
        from equipment.models import Equipment
        from employees.models import Employee
        from projects.models import Project
        from clients.models import Client
        from suppliers.models import Supplier
        from notifications.models import Notification

        for model in [DailyReport, Attendance, Expense, MaterialTransaction,
                      Material, Equipment, Employee, Project, Client, Supplier, Notification]:
            model.objects.all().delete()

        from accounts.models import User
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("  ✓ Data cleared")

    # ── Roles ─────────────────────────────────────────────────────────
    def _seed_roles(self):
        from accounts.models import Role
        roles = [
            ('admin', 'Full system access'),
            ('project_manager', 'Manage assigned projects'),
            ('site_supervisor', 'Site-level operations'),
            ('employee', 'Worker access'),
        ]
        for name, desc in roles:
            Role.objects.get_or_create(name=name, defaults={'description': desc})
        self.stdout.write("  ✓ Roles")

    # ── Users ─────────────────────────────────────────────────────────
    def _seed_users(self):
        from accounts.models import User, Role

        admin_role = Role.objects.get(name='admin')
        pm_role = Role.objects.get(name='project_manager')
        sv_role = Role.objects.get(name='site_supervisor')

        users = [
            dict(username='admin', email='admin@jaimalar.com', first_name='Admin',
                 last_name='User', role=admin_role, is_staff=True, is_superuser=True),
            dict(username='rajesh.pm', email='rajesh@jaimalar.com', first_name='Rajesh',
                 last_name='Kumar', role=pm_role, is_staff=False, is_superuser=False),
            dict(username='suresh.sv', email='suresh@jaimalar.com', first_name='Suresh',
                 last_name='Patil', role=sv_role, is_staff=False, is_superuser=False),
            dict(username='anita.pm', email='anita@jaimalar.com', first_name='Anita',
                 last_name='Sharma', role=pm_role, is_staff=False, is_superuser=False),
        ]
        created = 0
        for u in users:
            if not User.objects.filter(email=u['email']).exists():
                user = User(**{k: v for k, v in u.items()})
                user.set_password('admin123')
                user.save()
                created += 1
        self.stdout.write(f"  ✓ Users ({created} created)")

    # ── Clients ───────────────────────────────────────────────────────
    def _seed_clients(self):
        from clients.models import Client
        data = [
            ('Mehta Developers', 'Mehta Group Pvt Ltd', '9820011111', 'mehta@example.com', 'Andheri, Mumbai'),
            ('Sharma Constructions', 'Sharma Infra Ltd', '9820022222', 'sharma@example.com', 'Bandra, Mumbai'),
            ('Kapoor Realty', 'Kapoor Properties', '9820033333', 'kapoor@example.com', 'Lonavala'),
            ('City Municipal Corp', 'Mumbai Municipal Corporation', '9820044444', 'mmc@example.com', 'Thane'),
            ('Joshi Builders', 'Joshi Real Estate', '9820055555', 'joshi@example.com', 'Pune'),
        ]
        for name, company, phone, email, addr in data:
            Client.objects.get_or_create(phone=phone, defaults={
                'name': name, 'company': company, 'email': email, 'address': addr,
                'gst_number': f'27GST{random.randint(10000,99999)}',
            })
        self.stdout.write("  ✓ Clients")

    # ── Suppliers ─────────────────────────────────────────────────────
    def _seed_suppliers(self):
        from suppliers.models import Supplier
        data = [
            ('ACC Cement Store', 'ACC Ltd', '9910011111', 'Cement, Aggregate', 'Vikhroli, Mumbai'),
            ('Tata Steel Depot', 'Tata Steel Ltd', '9910022222', 'Steel, TMT Bars', 'Kurla, Mumbai'),
            ('Mahesh Sand Supplier', 'Mahesh & Bros', '9910033333', 'Sand, Gravel', 'Navi Mumbai'),
            ('Rathi Electricals', 'Rathi Electric Co', '9910044444', 'Electrical Material', 'Ghatkopar'),
            ('Om Plumbing', 'Om Pipes & Fittings', '9910055555', 'Plumbing Material', 'Thane'),
        ]
        for name, company, phone, materials, addr in data:
            Supplier.objects.get_or_create(phone=phone, defaults={
                'name': name, 'company': company,
                'materials_supplied': materials, 'address': addr,
                'gst_number': f'27GST{random.randint(10000,99999)}',
            })
        self.stdout.write("  ✓ Suppliers")

    # ── Materials ─────────────────────────────────────────────────────
    def _seed_materials(self):
        from materials.models import Material
        from suppliers.models import Supplier

        suppliers = list(Supplier.objects.all())
        data = [
            ('Cement (OPC 53)', 'cement', 'bags', 850, 200, 380),
            ('Steel TMT Bars', 'steel', 'kg', 12000, 2000, 68),
            ('River Sand', 'sand', 'ton', 45, 10, 1800),
            ('M-Sand', 'sand', 'ton', 30, 8, 1200),
            ('Red Bricks', 'bricks', 'pieces', 12000, 3000, 8),
            ('AAC Blocks', 'bricks', 'pieces', 5000, 1000, 45),
            ('Coarse Aggregate 20mm', 'aggregate', 'ton', 60, 15, 1600),
            ('Interior Paint', 'paint', 'litre', 400, 80, 220),
            ('Exterior Paint', 'paint', 'litre', 250, 60, 290),
            ('Floor Tiles 2x2', 'tiles', 'sqft', 3200, 500, 55),
            ('Wall Tiles', 'tiles', 'sqft', 1800, 300, 45),
            ('PVC Pipes', 'plumbing', 'meter', 500, 100, 85),
            ('Copper Wire 6mm', 'electrical', 'meter', 800, 200, 120),
            ('MCB Switches', 'electrical', 'pieces', 150, 30, 350),
            ('Plywood 18mm', 'other', 'pieces', 80, 20, 1800),
        ]
        created = 0
        for name, cat, unit, stock, min_stock, price in data:
            if not Material.objects.filter(name=name).exists():
                Material.objects.create(
                    name=name, category=cat, unit=unit,
                    current_stock=stock, minimum_stock=min_stock,
                    unit_price=price,
                    supplier=random.choice(suppliers) if suppliers else None,
                )
                created += 1
        self.stdout.write(f"  ✓ Materials ({created} created)")

    # ── Projects ──────────────────────────────────────────────────────
    def _seed_projects(self):
        from projects.models import Project
        from clients.models import Client
        from accounts.models import User

        clients = list(Client.objects.all())
        managers = list(User.objects.filter(role__name='project_manager'))
        admin = User.objects.filter(is_superuser=True).first()

        today = date.today()
        projects_data = [
            {
                'name': 'Residential Tower – Andheri',
                'location': 'Andheri West, Mumbai',
                'project_type': 'residential',
                'start_date': today - timedelta(days=180),
                'expected_end_date': today + timedelta(days=180),
                'budget': Decimal('45000000'),
                'progress': 55,
                'status': 'active',
                'description': '12-storey residential tower with 48 units. Currently on 7th floor.',
            },
            {
                'name': 'Commercial Plaza – Bandra',
                'location': 'Bandra East, Mumbai',
                'project_type': 'commercial',
                'start_date': today - timedelta(days=90),
                'expected_end_date': today + timedelta(days=270),
                'budget': Decimal('82000000'),
                'progress': 25,
                'status': 'active',
                'description': 'G+5 commercial complex with retail and office space.',
            },
            {
                'name': 'Villa Project – Lonavala',
                'location': 'Lonavala, Pune',
                'project_type': 'residential',
                'start_date': today - timedelta(days=365),
                'expected_end_date': today - timedelta(days=30),
                'budget': Decimal('18000000'),
                'progress': 100,
                'status': 'completed',
                'actual_end_date': today - timedelta(days=30),
                'description': '5 luxury villas. Project completed.',
            },
            {
                'name': 'School Building – Thane',
                'location': 'Thane West, Maharashtra',
                'project_type': 'infrastructure',
                'start_date': today + timedelta(days=30),
                'expected_end_date': today + timedelta(days=365),
                'budget': Decimal('28000000'),
                'progress': 0,
                'status': 'upcoming',
                'description': 'G+3 school building with 30 classrooms.',
            },
        ]

        created_projects = []
        for i, pd in enumerate(projects_data):
            if not Project.objects.filter(name=pd['name']).exists():
                p = Project(
                    name=pd['name'],
                    location=pd['location'],
                    project_type=pd['project_type'],
                    start_date=pd['start_date'],
                    expected_end_date=pd['expected_end_date'],
                    budget=pd['budget'],
                    progress=pd['progress'],
                    status=pd['status'],
                    description=pd['description'],
                    client=clients[i % len(clients)] if clients else None,
                    project_manager=managers[i % len(managers)] if managers else admin,
                    created_by=admin,
                )
                if 'actual_end_date' in pd:
                    p.actual_end_date = pd['actual_end_date']
                p.save()
                created_projects.append(p)
            else:
                created_projects.append(Project.objects.get(name=pd['name']))

        self.stdout.write(f"  ✓ Projects ({len(created_projects)} total)")
        return created_projects

    # ── Employees ─────────────────────────────────────────────────────
    def _seed_employees(self, projects):
        from employees.models import Employee

        first_names = ['Ramesh', 'Suresh', 'Mahesh', 'Dinesh', 'Ganesh', 'Rajesh',
                       'Prakash', 'Lokesh', 'Rakesh', 'Naresh', 'Santosh', 'Nilesh',
                       'Vijay', 'Sanjay', 'Ajay', 'Uday', 'Mohan', 'Sohan',
                       'Ashok', 'Vinod', 'Pramod', 'Dilip', 'Rajan', 'Kiran',
                       'Arjun', 'Rohan', 'Rohit', 'Amit', 'Sumit', 'Ankit']
        last_names = ['Patil', 'Shinde', 'More', 'Jadhav', 'Gaikwad', 'Deshmukh',
                      'Kadam', 'Salunke', 'Yadav', 'Singh', 'Kumar', 'Shah',
                      'Mehta', 'Joshi', 'Sharma', 'Verma', 'Gupta', 'Tiwari',
                      'Patel', 'Nair', 'Reddy', 'Iyer', 'Pillai', 'Naik',
                      'Sawant', 'Bhosle', 'Mane', 'Wagh', 'Pawar', 'Kale']

        types = ['mason', 'mason', 'mason', 'carpenter', 'carpenter',
                 'electrician', 'plumber', 'labour', 'labour', 'labour',
                 'labour', 'labour', 'supervisor', 'engineer', 'driver']
        salaries = {
            'mason': (700, 900), 'carpenter': (650, 850),
            'electrician': (750, 950), 'plumber': (700, 900),
            'labour': (450, 600), 'supervisor': (1200, 1800),
            'engineer': (2000, 3500), 'driver': (600, 800),
        }

        active_projects = [p for p in projects if p.status in ['active', 'upcoming']]
        employees = []
        created = 0

        for i in range(30):
            fname = first_names[i % len(first_names)]
            lname = last_names[i % len(last_names)]
            emp_type = types[i % len(types)]
            daily_min, daily_max = salaries.get(emp_type, (500, 700))
            salary = random.randint(daily_min, daily_max)
            phone = f'98{random.randint(10000000, 99999999)}'

            if not Employee.objects.filter(phone=phone).exists():
                emp = Employee(
                    full_name=f'{fname} {lname}',
                    phone=phone,
                    email=f'{fname.lower()}.{lname.lower()}{i}@gmail.com',
                    joining_date=date.today() - timedelta(days=random.randint(30, 500)),
                    employee_type=emp_type,
                    department='labour' if emp_type in ['labour', 'mason', 'carpenter', 'plumber', 'electrician'] else 'civil',
                    salary=salary,
                    status='active' if i < 25 else random.choice(['active', 'on_leave']),
                    assigned_project=random.choice(active_projects) if active_projects else None,
                    designation=emp_type.title(),
                )
                emp.save()
                employees.append(emp)
                created += 1
            else:
                existing = Employee.objects.get(phone=phone)
                employees.append(existing)

        self.stdout.write(f"  ✓ Employees ({created} created, {len(employees)} total)")
        return employees

    # ── Attendance ────────────────────────────────────────────────────
    def _seed_attendance(self, employees, projects):
        from attendance.models import Attendance

        active_projects = [p for p in projects if p.status == 'active']
        if not active_projects:
            self.stdout.write("  ✓ Attendance (skipped — no active projects)")
            return

        today = date.today()
        created = 0
        status_weights = ['present', 'present', 'present', 'present', 'present',
                          'present', 'present', 'absent', 'half_day', 'leave']

        # Last 30 days
        for day_offset in range(30):
            att_date = today - timedelta(days=day_offset)
            # Skip Sundays
            if att_date.weekday() == 6:
                continue

            project = random.choice(active_projects)
            project_workers = [e for e in employees if e.assigned_project == project]
            if not project_workers:
                project_workers = employees[:15]

            for emp in project_workers:
                if Attendance.objects.filter(employee=emp, date=att_date).exists():
                    continue

                status = random.choice(status_weights)
                check_in = None
                check_out = None

                if status in ['present', 'half_day']:
                    hour_in = random.randint(7, 9)
                    check_in = datetime.strptime(f'{hour_in}:{random.choice([0,15,30,45]):02d}', '%H:%M').time()
                    if status == 'present':
                        hour_out = random.randint(17, 19)
                    else:
                        hour_out = random.randint(12, 14)
                    check_out = datetime.strptime(f'{hour_out}:{random.choice([0,15,30,45]):02d}', '%H:%M').time()

                try:
                    Attendance.objects.create(
                        employee=emp,
                        project=project,
                        date=att_date,
                        status=status,
                        check_in=check_in,
                        check_out=check_out,
                        marked_by='Admin (seed)',
                    )
                    created += 1
                except Exception:
                    pass

        self.stdout.write(f"  ✓ Attendance ({created} records)")

    # ── Equipment ─────────────────────────────────────────────────────
    def _seed_equipment(self, projects):
        from equipment.models import Equipment

        active = [p for p in projects if p.status == 'active']
        items = [
            ('JCB Excavator', 'earthmoving', 8500, 'day', 'Tata Hitachi Rentals'),
            ('Tower Crane 10T', 'lifting', 15000, 'day', 'Liebherr India'),
            ('Concrete Mixer 500L', 'concrete', 3500, 'day', 'Self Owned'),
            ('Concrete Pump', 'concrete', 12000, 'day', 'Putzmeister Rentals'),
            ('Tractor Trailer', 'transport', 4500, 'day', 'Ajay Transport'),
            ('Dump Truck', 'transport', 5500, 'day', 'Patil Vehicles'),
            ('Plate Compactor', 'compaction', 1500, 'day', 'Self Owned'),
            ('Vibrator Needle', 'concrete', 800, 'day', 'Self Owned'),
            ('Welding Machine', 'other', 1200, 'day', 'Self Owned'),
            ('Generator 25KVA', 'other', 2500, 'day', 'Kirloskar Rentals'),
        ]
        created = 0
        for name, cat, cost, per, vendor in items:
            if not Equipment.objects.filter(name=name).exists():
                Equipment.objects.create(
                    name=name, category=cat,
                    rental_cost=cost, rental_per=per,
                    owner_vendor=vendor,
                    project=random.choice(active) if active else None,
                    status=random.choice(['in_use', 'in_use', 'available', 'available', 'maintenance']),
                    start_date=date.today() - timedelta(days=random.randint(10, 60)),
                )
                created += 1
        self.stdout.write(f"  ✓ Equipment ({created} items)")

    # ── Expenses ──────────────────────────────────────────────────────
    def _seed_expenses(self, projects):
        from expenses.models import Expense
        from accounts.models import User

        admin = User.objects.filter(is_superuser=True).first()
        today = date.today()

        expense_data = [
            ('labour', 85000, 'Patil Labour Contractor', 'bank_transfer'),
            ('labour', 72000, 'Singh Labour Services', 'bank_transfer'),
            ('material', 125000, 'ACC Cement Store', 'cheque'),
            ('material', 89000, 'Tata Steel Depot', 'cheque'),
            ('material', 45000, 'Mahesh Sand Supplier', 'cash'),
            ('equipment', 68000, 'Tata Hitachi Rentals', 'bank_transfer'),
            ('equipment', 45000, 'Liebherr India', 'cheque'),
            ('transport', 18000, 'Ajay Transport', 'cash'),
            ('transport', 22000, 'Patil Vehicles', 'cash'),
            ('electricity', 8500, 'MSEDCL', 'upi'),
            ('water', 3200, 'BWSSB', 'upi'),
            ('contractor', 95000, 'Raje Civil Works', 'cheque'),
            ('salary', 180000, 'Staff Salaries Oct', 'bank_transfer'),
            ('other', 12000, 'Site Office Expenses', 'cash'),
            ('material', 67000, 'Rathi Electricals', 'cheque'),
        ]

        active_projects = [p for p in projects if p.status in ['active', 'completed']]
        created = 0

        for project in active_projects:
            for i, (cat, base_amt, vendor, payment) in enumerate(expense_data):
                amt = base_amt + random.randint(-5000, 5000)
                exp_date = today - timedelta(days=random.randint(0, 90))
                status = random.choice(['approved', 'approved', 'approved', 'pending', 'rejected'])

                Expense.objects.create(
                    project=project,
                    category=cat,
                    amount=Decimal(str(max(amt, 1000))),
                    date=exp_date,
                    vendor=vendor,
                    payment_method=payment,
                    description=f'{cat.title()} expense for {project.name}',
                    approval_status=status,
                    approved_by=admin if status == 'approved' else None,
                    created_by=admin,
                )
                created += 1

        self.stdout.write(f"  ✓ Expenses ({created} records)")

    # ── Material Transactions ─────────────────────────────────────────
    def _seed_material_transactions(self, projects):
        from materials.models import Material, MaterialTransaction
        from suppliers.models import Supplier
        from accounts.models import User

        admin = User.objects.filter(is_superuser=True).first()
        materials = list(Material.objects.all())
        suppliers = list(Supplier.objects.all())
        active = [p for p in projects if p.status in ['active', 'completed']]

        if not materials or not active:
            self.stdout.write("  ✓ Material Transactions (skipped)")
            return

        today = date.today()
        created = 0

        for project in active:
            for mat in random.sample(materials, min(8, len(materials))):
                # Purchase
                qty = random.randint(50, 300)
                MaterialTransaction.objects.create(
                    material=mat, project=project,
                    transaction_type='purchase',
                    quantity=qty,
                    unit_price=mat.unit_price,
                    date=today - timedelta(days=random.randint(30, 90)),
                    supplier=random.choice(suppliers) if suppliers else None,
                    created_by=admin,
                    remarks='Bulk purchase',
                )
                created += 1

                # Usage
                used = random.randint(10, int(qty * 0.7))
                MaterialTransaction.objects.create(
                    material=mat, project=project,
                    transaction_type='usage',
                    quantity=used,
                    unit_price=mat.unit_price,
                    date=today - timedelta(days=random.randint(0, 29)),
                    created_by=admin,
                    remarks='Site consumption',
                )
                created += 1

        self.stdout.write(f"  ✓ Material Transactions ({created} records)")

    # ── Daily Reports ─────────────────────────────────────────────────
    def _seed_daily_reports(self, projects):
        from reports.models import DailyReport
        from accounts.models import User

        admin = User.objects.filter(is_superuser=True).first()
        active = [p for p in projects if p.status in ['active', 'completed']]
        today = date.today()

        weather_opts = ['sunny', 'cloudy', 'sunny', 'sunny', 'rainy']
        work_notes = [
            'Foundation work completed for Grid C.',
            'Column casting done up to 3rd floor.',
            'Shuttering work in progress for 4th floor.',
            'Brick masonry completed in Block A.',
            'Plastering work on east wing.',
            'Waterproofing work on terrace.',
            'Internal wiring work in progress.',
            'Flooring work completed in 2nd floor.',
        ]
        created = 0

        for project in active:
            # 10 reports per active project over last 20 days
            report_dates = set()
            attempts = 0
            while len(report_dates) < 10 and attempts < 30:
                d = today - timedelta(days=random.randint(0, 20))
                if d.weekday() != 6:  # skip Sunday
                    report_dates.add(d)
                attempts += 1

            for rep_date in report_dates:
                if DailyReport.objects.filter(project=project, report_date=rep_date).exists():
                    continue
                total = random.randint(15, 35)
                present = random.randint(int(total * 0.7), total)
                DailyReport.objects.create(
                    project=project,
                    report_date=rep_date,
                    weather=random.choice(weather_opts),
                    total_workers=total,
                    present_workers=present,
                    work_completed=random.choice(work_notes),
                    work_in_progress=random.choice(work_notes),
                    materials_used=f'Cement: {random.randint(10,40)} Bags, Sand: {random.randint(1,5)} Ton',
                    equipment_used='Concrete Mixer, Vibrator',
                    issues='' if random.random() > 0.3 else 'Minor delay due to material shortage.',
                    supervisor_remarks='Work progressing as per schedule.',
                    submitted_by=admin,
                )
                created += 1

        self.stdout.write(f"  ✓ Daily Reports ({created} records)")

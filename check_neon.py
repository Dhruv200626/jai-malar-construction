import os
import django

# Point to Neon database
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_62mwsFpIlTyE@ep-long-fire-b3phtbht-pooler.c-4.ap-southeast-1.aws.neon.tech/jai-malar-db?sslmode=require&channel_binding=require'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from django.db import connection

# Check tables
cursor = connection.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
""")
tables = cursor.fetchall()
print(f'✅ Total tables in Neon: {len(tables)}')
for t in tables:
    print(f'   - {t[0]}')

# Check users
print(f'\n✅ Total users: {User.objects.count()}')
for u in User.objects.all():
    print(f'   - {u.username} ({u.email}) | Superuser: {u.is_superuser}')

#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5431,
        user='odoo',
        password='odoo',
        dbname='odoo_fitdnu'
    )
    cur = conn.cursor()
    
    # Reset password cho user admin (id=2)
    cur.execute("UPDATE res_users SET login='admin', password='admin' WHERE id=2")
    conn.commit()
    
    print("✅ Password đã được reset!")
    print("Login: admin")
    print("Password: admin")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Lỗi: {e}")

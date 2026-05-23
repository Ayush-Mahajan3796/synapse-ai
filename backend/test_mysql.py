import pymysql

credentials = [
    ('root', 'Ayush2026Mongo'),
    ('ss7716801_db_user', 'Ayush2026Mongo'),
    ('ss7716801_db_user', ''),
]
success = False

for u, p in credentials:
    try:
        pymysql.connect(host='localhost', user=u, password=p)
        print(f"SUCCESS: user={u}, password={p}")
        success = True
        break
    except Exception as e:
        pass

if not success:
    print("ALL FAILED")

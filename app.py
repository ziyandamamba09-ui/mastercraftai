from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from datetime import datetime, date
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mastercraft2026secret')

# ============================================================
# DATABASE — uses environment variables on Railway
# ============================================================
def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'mastercraft'),
        port=int(os.environ.get('DB_PORT', 3306))
    )

def query(sql, params=None):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        results = cursor.fetchall()
        db.close()
        return results
    except Exception as e:
        print("DB Error:", e)
        return []

def execute(sql, params=None):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(sql, params or ())
        db.commit()
        lid = cursor.lastrowid
        db.close()
        return lid or True
    except Exception as e:
        print("DB Error:", e)
        return False

# ============================================================
# USERS
# ============================================================
USERS = {
    'admin':     {'password': 'admin123',  'role': 'Admin',              'name': 'System Administrator'},
    'inventory': {'password': 'inv123',    'role': 'Inventory Manager',  'name': 'Inventory Manager'},
    'accounting':{'password': 'acc123',    'role': 'Accountant',         'name': 'Senior Accountant'},
    'sales':     {'password': 'sales123',  'role': 'Sales Manager',      'name': 'Sales Manager'},
    'logistics': {'password': 'log123',    'role': 'Logistics Officer',  'name': 'Logistics Officer'},
    'it':        {'password': 'it123',     'role': 'IT Administrator',   'name': 'IT Administrator'},
    'management':{'password': 'mgmt123',   'role': 'Operations Director','name': 'Operations Director'},
}

def generate_response(message, role):
    msg = message.lower()
    if any(w in msg for w in ['inventory','stock','item','product','supplier']):
        if any(w in msg for w in ['value','worth','total']):
            items = query('SELECT item, quantity, unit_price, department FROM inventory')
            total = sum(i['quantity'] * float(i['unit_price']) for i in items)
            lines = '\n'.join([f"- {i['item']}: {i['quantity']} units x E{float(i['unit_price']):,.2f} = E{i['quantity']*float(i['unit_price']):,.2f}" for i in items])
            return f"Total inventory value: E{total:,.2f}\n\n{lines}"
        if any(w in msg for w in ['low','lowest','least']):
            items = query('SELECT item, quantity, department FROM inventory ORDER BY quantity ASC LIMIT 1')
            if items:
                i = items[0]
                return f"Lowest stock: {i['item']} - only {i['quantity']} units left in {i['department']} department."
        items = query('SELECT item, quantity, unit_price, department, supplier FROM inventory')
        lines = '\n'.join([f"- {i['item']} - {i['quantity']} units @ E{float(i['unit_price']):,.2f} ({i['department']}) - Supplier: {i['supplier']}" for i in items])
        return f"Mastercraft Inventory:\n\n{lines}"
    if any(w in msg for w in ['sale','sales','revenue','invoice','monthly']):
        if any(w in msg for w in ['best','highest','top']):
            rows = query('SELECT month, amount, invoices FROM sales ORDER BY amount DESC LIMIT 1')
            if rows: r=rows[0]; return f"Best sales month: {r['month']} with E{float(r['amount']):,.2f} from {r['invoices']} invoices."
        if any(w in msg for w in ['total','all','overall']):
            rows = query('SELECT SUM(amount) as total, SUM(invoices) as inv FROM sales')
            if rows: return f"Total sales: E{float(rows[0]['total']):,.2f} across {rows[0]['inv']} total invoices."
        rows = query('SELECT month, amount, invoices FROM sales ORDER BY id')
        lines = '\n'.join([f"- {r['month']}: E{float(r['amount']):,.2f} - {r['invoices']} invoices" for r in rows])
        return f"Monthly Sales Report:\n\n{lines}"
    if any(w in msg for w in ['staff','employee','worker','people','team','who','attendance']):
        if any(w in msg for w in ['attendance','present','today']):
            rows = query("SELECT staff_name, department, time_in, status FROM attendance WHERE date = CURDATE()")
            if rows:
                lines = '\n'.join([f"- {r['staff_name']} ({r['department']}): {r['status']} - In at {r['time_in']}" for r in rows])
                return f"Today's Attendance:\n\n{lines}"
            return "No attendance records for today yet."
        if any(w in msg for w in ['count','how many','number']):
            rows = query('SELECT COUNT(*) as total FROM staff')
            return f"Mastercraft currently has {rows[0]['total']} staff members."
        if any(w in msg for w in ['salary','salaries','earn','pay']):
            if role in ['Admin','Operations Director','Accountant']:
                rows = query('SELECT name, role, salary FROM staff ORDER BY salary DESC')
                lines = '\n'.join([f"- {r['name']} ({r['role']}): E{float(r['salary']):,.2f}/month" for r in rows])
                return f"Staff Salaries:\n\n{lines}"
            return "Salary information is restricted to Admin, Management and Accounting only."
        rows = query('SELECT name, department, role, start_date FROM staff')
        lines = '\n'.join([f"- {r['name']} - {r['role']} ({r['department']}) since {r['start_date']}" for r in rows])
        return f"Mastercraft Staff Directory:\n\n{lines}"
    if any(w in msg for w in ['expense','expenses','cost','spending']):
        if role in ['Admin','Accountant','Operations Director','Management']:
            rows = query('SELECT category, amount, approved_by FROM expenses')
            total = sum(float(r['amount']) for r in rows)
            lines = '\n'.join([f"- {r['category']}: E{float(r['amount']):,.2f} (approved by {r['approved_by']})" for r in rows])
            return f"April 2026 Expenses - Total: E{total:,.2f}\n\n{lines}"
        return "Expense details are restricted to Accounting and Management roles only."
    if any(w in msg for w in ['summary','overview','full','report','dashboard']):
        inv = query('SELECT SUM(quantity * unit_price) as total FROM inventory')
        sales = query('SELECT SUM(amount) as total FROM sales')
        staff = query('SELECT COUNT(*) as total FROM staff')
        best = query('SELECT month, amount FROM sales ORDER BY amount DESC LIMIT 1')
        low = query('SELECT item, quantity FROM inventory ORDER BY quantity ASC LIMIT 1')
        att = query("SELECT COUNT(*) as total FROM attendance WHERE date = CURDATE() AND status='Present'")
        result = "Mastercraft Business Summary\n" + "="*30 + "\n"
        result += f"Staff: {staff[0]['total']} employees\n"
        result += f"Present Today: {att[0]['total']}\n"
        result += f"Inventory Value: E{float(inv[0]['total']):,.2f}\n"
        result += f"Total Sales (Jan-Apr 2026): E{float(sales[0]['total']):,.2f}\n"
        result += f"Best Month: {best[0]['month']} (E{float(best[0]['amount']):,.2f})\n"
        result += f"Low Stock: {low[0]['item']} ({low[0]['quantity']} units)\n"
        if role in ['Admin','Accountant','Operations Director']:
            exp = query('SELECT SUM(amount) as total FROM expenses')
            result += f"April Expenses: E{float(exp[0]['total']):,.2f}\n"
        result += f"\nLogged in as: {role}"
        return result
    if any(w in msg for w in ['hello','hi','hey','help']):
        return f"Hello! I am MastercraftAI.\n\nAs {role}, ask me about:\n- Inventory and stock\n- Sales and revenue\n- Staff and attendance\n- Business overview"
    return "Ask me about inventory, sales, staff or expenses. Try:\n- Show inventory value\n- Monthly sales\n- List all staff\n- Business overview"

# ============================================================
# ROUTES
# ============================================================
@app.route('/')
def home():
    if 'username' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username','').lower().strip()
    password = data.get('password','').strip()
    if username in USERS and USERS[username]['password'] == password:
        session['username'] = username
        session['role'] = USERS[username]['role']
        session['name'] = USERS[username]['name']
        return jsonify({'success': True, 'role': USERS[username]['role'], 'name': USERS[username]['name']})
    return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('home'))
    return render_template('dashboard.html', role=session['role'], name=session['name'])

@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session: return jsonify({'error': 'Not logged in'}), 401
    try:
        data = request.json
        reply = generate_response(data.get('message',''), session.get('role','Staff'))
        return jsonify({'reply': reply, 'timestamp': datetime.now().strftime('%H:%M')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data-summary')
def data_summary():
    if 'username' not in session: return jsonify({'error': 'Not logged in'}), 401
    try:
        inv = query('SELECT SUM(quantity * unit_price) as total FROM inventory')
        sales = query('SELECT SUM(amount) as total FROM sales')
        staff = query('SELECT COUNT(*) as total FROM staff')
        att = query("SELECT COUNT(*) as total FROM attendance WHERE date = CURDATE() AND status='Present'")
        return jsonify({
            'inventory_value': float(inv[0]['total'] or 0),
            'total_sales': float(sales[0]['total'] or 0),
            'staff_count': staff[0]['total'],
            'present_today': att[0]['total'],
            'role': session.get('role'),
            'name': session.get('name')
        })
    except: return jsonify({'inventory_value':0,'total_sales':0,'staff_count':0,'present_today':0})

@app.route('/api/inventory')
def api_inventory():
    if 'username' not in session: return jsonify([])
    return jsonify(query('SELECT id, item, quantity, unit_price, department, supplier FROM inventory'))

@app.route('/api/sales')
def api_sales():
    if 'username' not in session: return jsonify([])
    return jsonify(query('SELECT id, month, amount, invoices, customer FROM sales ORDER BY id'))

@app.route('/api/staff')
def api_staff():
    if 'username' not in session: return jsonify([])
    return jsonify(query('SELECT id, name, department, role, salary, start_date FROM staff'))

@app.route('/api/expenses')
def api_expenses():
    if 'username' not in session: return jsonify([])
    role = session.get('role','')
    if role in ['Admin','Accountant','Operations Director','Management']:
        return jsonify(query('SELECT id, category, amount, month, approved_by FROM expenses'))
    return jsonify([{'category':'Restricted','amount':0,'month':'-','approved_by':'Contact Management'}])

@app.route('/api/attendance')
def api_attendance():
    if 'username' not in session: return jsonify([])
    return jsonify(query('SELECT id, staff_name, department, date, time_in, time_out, status FROM attendance ORDER BY date DESC, time_in DESC LIMIT 50'))

@app.route('/api/notifications')
def api_notifications():
    if 'username' not in session: return jsonify([])
    try:
        return jsonify(query('SELECT id, type, message, severity, is_read, DATE_FORMAT(created_at, "%Y-%m-%d %H:%i:%s") as created_at FROM notifications ORDER BY created_at DESC LIMIT 10'))
    except: return jsonify([])

@app.route('/api/notifications/read/<int:notif_id>', methods=['POST'])
def mark_read(notif_id):
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    execute('UPDATE notifications SET is_read = 1 WHERE id = %s', (notif_id,))
    return jsonify({'success': True})

@app.route('/api/notifications/add', methods=['POST'])
def add_notification():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    d = request.json
    execute('INSERT INTO notifications (type,message,severity) VALUES (%s,%s,%s)',
        (d.get('type','INFO'), d.get('message',''), d.get('severity','info')))
    return jsonify({'success': True})

@app.route('/api/charts')
def api_charts():
    if 'username' not in session: return jsonify({})
    sales = query('SELECT month, amount FROM sales ORDER BY id')
    inv = query('SELECT department, SUM(quantity * unit_price) as val FROM inventory GROUP BY department')
    exp = query('SELECT category, amount FROM expenses')
    att = query("SELECT status, COUNT(*) as cnt FROM attendance WHERE date = CURDATE() GROUP BY status")
    return jsonify({
        'sales': {'labels': [r['month'] for r in sales], 'data': [float(r['amount']) for r in sales]},
        'inventory': {'labels': [r['department'] for r in inv], 'data': [float(r['val']) for r in inv]},
        'expenses': {'labels': [r['category'] for r in exp], 'data': [float(r['amount']) for r in exp]},
        'attendance': {'labels': [r['status'] for r in att], 'data': [r['cnt'] for r in att]}
    })

@app.route('/api/purchase-orders')
def api_po():
    if 'username' not in session: return jsonify([])
    return jsonify(query('SELECT * FROM purchase_orders ORDER BY created_at DESC'))

@app.route('/api/invoices')
def api_invoices():
    if 'username' not in session: return jsonify([])
    return jsonify(query('SELECT * FROM invoices ORDER BY created_at DESC'))

@app.route('/api/inventory/add', methods=['POST'])
def add_inventory():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    if session.get('role') not in ['Admin','Inventory Manager','Logistics Officer']:
        return jsonify({'error':'Permission denied'}), 403
    d = request.json
    lid = execute('INSERT INTO inventory (item,quantity,unit_price,department,supplier) VALUES (%s,%s,%s,%s,%s)',
        (d['item'],d['quantity'],d['unit_price'],d['department'],d['supplier']))
    return jsonify({'success': bool(lid)})

@app.route('/api/inventory/update', methods=['POST'])
def update_inventory():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    if session.get('role') not in ['Admin','Inventory Manager','Logistics Officer']:
        return jsonify({'error':'Permission denied'}), 403
    d = request.json
    ok = execute('UPDATE inventory SET quantity=%s, unit_price=%s WHERE id=%s', (d['quantity'],d['unit_price'],d['id']))
    return jsonify({'success': bool(ok)})

@app.route('/api/sales/add', methods=['POST'])
def add_sale():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    if session.get('role') not in ['Admin','Sales Manager']:
        return jsonify({'error':'Permission denied'}), 403
    d = request.json
    lid = execute('INSERT INTO sales (month,amount,invoices,customer) VALUES (%s,%s,%s,%s)',
        (d['month'],d['amount'],d['invoices'],d.get('customer','Various Clients')))
    return jsonify({'success': bool(lid)})

@app.route('/api/attendance/checkin', methods=['POST'])
def checkin():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    d = request.json
    existing = query('SELECT id FROM attendance WHERE staff_name=%s AND date=CURDATE()', (d['staff_name'],))
    if existing: return jsonify({'success': False, 'message': 'Already checked in today'})
    lid = execute('INSERT INTO attendance (staff_name,department,date,time_in,status) VALUES (%s,%s,CURDATE(),%s,"Present")',
        (d['staff_name'],d['department'],datetime.now().strftime('%H:%M:%S')))
    return jsonify({'success': bool(lid)})

@app.route('/api/attendance/checkout', methods=['POST'])
def checkout():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    d = request.json
    ok = execute('UPDATE attendance SET time_out=%s WHERE staff_name=%s AND date=CURDATE() AND time_out IS NULL',
        (datetime.now().strftime('%H:%M:%S'),d['staff_name']))
    return jsonify({'success': bool(ok)})

@app.route('/api/po/add', methods=['POST'])
def add_po():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    d = request.json
    lid = execute('INSERT INTO purchase_orders (po_number,supplier,item,quantity,unit_price,total_amount,department,requested_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
        (d['po_number'],d['supplier'],d['item'],d['quantity'],d['unit_price'],d['total_amount'],d['department'],d['requested_by']))
    return jsonify({'success': bool(lid)})

@app.route('/api/invoice/add', methods=['POST'])
def add_invoice():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    d = request.json
    lid = execute('INSERT INTO invoices (invoice_number,customer_name,customer_email,items,subtotal,tax,total,due_date,created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (d['invoice_number'],d['customer_name'],d['customer_email'],d['items'],d['subtotal'],d['tax'],d['total'],d['due_date'],d['created_by']))
    return jsonify({'success': bool(lid)})

@app.route('/api/stock/move', methods=['POST'])
def stock_move():
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    d = request.json
    item_rows = query('SELECT id, quantity FROM inventory WHERE item = %s', (d['item'],))
    if not item_rows: return jsonify({'success': False, 'error': 'Item not found'})
    item = item_rows[0]
    prev_qty = item['quantity']
    new_qty = prev_qty + int(d['quantity']) if d['movement_type'] == 'IN' else prev_qty - int(d['quantity'])
    execute('UPDATE inventory SET quantity = %s WHERE id = %s', (new_qty, item['id']))
    execute('INSERT INTO stock_movements (item,movement_type,quantity,previous_qty,new_qty,reason,department,recorded_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
        (d['item'],d['movement_type'],d['quantity'],prev_qty,new_qty,d.get('reason',''),d.get('department','General'),d.get('recorded_by','')))
    return jsonify({'success': True})

@app.route('/api/export/csv/<table>')
def export_csv(table):
    if 'username' not in session: return jsonify({'error':'Not logged in'}), 401
    allowed = ['inventory','sales','staff','expenses','attendance','purchase_orders','invoices']
    if table not in allowed: return jsonify({'error':'Invalid table'}), 400
    rows = query(f'SELECT * FROM {table}')
    if not rows: return jsonify({'error':'No data'}), 404
    cols = list(rows[0].keys())
    csv = ','.join(cols) + '\n'
    for row in rows:
        csv += ','.join([str(v) if v is not None else '' for v in row.values()]) + '\n'
    response = make_response(csv)
    response.headers['Content-Disposition'] = f'attachment; filename={table}_{date.today()}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)

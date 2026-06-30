import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = 'billing.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== BILLING ENDPOINTS ====================

@app.route('/api/billing/create', methods=['POST'])
def create_billing():
    """Create a new billing record"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO billing (patient_id, patient_name, gender, age, phone, email, 
                               appointment_date, department, doctor_name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('patient_id', ''),
            data.get('patient_name', ''),
            data.get('gender', ''),
            data.get('age', 0),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('appointment_date', ''),
            data.get('department', ''),
            data.get('doctor_name', ''),
            'Pending Payment'
        ))
        
        conn.commit()
        billing_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'billing_id': billing_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/billing/<int:billing_id>', methods=['GET'])
def get_billing(billing_id):
    """Get billing details with all items"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get billing info
        cursor.execute('SELECT * FROM billing WHERE id = ?', (billing_id,))
        billing = cursor.fetchone()
        
        if not billing:
            return jsonify({'success': False, 'error': 'Billing not found'}), 404
        
        # Get pharmacy items
        cursor.execute('SELECT * FROM pharmacy_items WHERE billing_id = ?', (billing_id,))
        pharmacy_items = [dict(row) for row in cursor.fetchall()]
        
        # Get lab tests
        cursor.execute('SELECT * FROM lab_tests WHERE billing_id = ?', (billing_id,))
        lab_tests = [dict(row) for row in cursor.fetchall()]
        
        # Get payment history
        cursor.execute('SELECT * FROM payment_history WHERE billing_id = ?', (billing_id,))
        payments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'billing': dict(billing),
            'pharmacy_items': pharmacy_items,
            'lab_tests': lab_tests,
            'payments': payments
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/billing/<int:billing_id>/add-pharmacy', methods=['POST'])
def add_pharmacy_item(billing_id):
    """Add pharmacy item to billing"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        item_name = data.get('item_name', '')
        quantity = data.get('quantity', 1)
        unit_price = data.get('unit_price', 0)
        total_price = quantity * unit_price
        
        cursor.execute('''
            INSERT INTO pharmacy_items (billing_id, item_name, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (billing_id, item_name, quantity, unit_price, total_price))
        
        conn.commit()
        
        # Update billing totals
        update_billing_totals(cursor, billing_id)
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pharmacy item added'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/billing/<int:billing_id>/add-lab', methods=['POST'])
def add_lab_test(billing_id):
    """Add lab test to billing"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        test_name = data.get('test_name', '')
        test_price = data.get('test_price', 0)
        
        cursor.execute('''
            INSERT INTO lab_tests (billing_id, test_name, test_price)
            VALUES (?, ?, ?)
        ''', (billing_id, test_name, test_price))
        
        conn.commit()
        
        # Update billing totals
        update_billing_totals(cursor, billing_id)
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Lab test added'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/billing/<int:billing_id>/update-totals', methods=['PUT'])
def update_totals(billing_id):
    """Recalculate and update billing totals"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Calculate pharmacy total
        cursor.execute('SELECT SUM(total_price) FROM pharmacy_items WHERE billing_id = ?', (billing_id,))
        pharmacy_total = cursor.fetchone()[0] or 0
        
        # Calculate lab total
        cursor.execute('SELECT SUM(test_price) FROM lab_tests WHERE billing_id = ?', (billing_id,))
        lab_total = cursor.fetchone()[0] or 0
        
        subtotal = pharmacy_total + lab_total
        discount = subtotal * 0.05  # 5% discount
        gst = (subtotal - discount) * 0.18  # 18% GST
        grand_total = subtotal - discount + gst
        
        cursor.execute('''
            UPDATE billing 
            SET pharmacy_total = ?, lab_total = ?, subtotal = ?, 
                discount = ?, gst = ?, grand_total = ?, updated_at = ?
            WHERE id = ?
        ''', (pharmacy_total, lab_total, subtotal, discount, gst, grand_total, datetime.now(), billing_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'pharmacy_total': pharmacy_total,
            'lab_total': lab_total,
            'subtotal': subtotal,
            'discount': discount,
            'gst': gst,
            'grand_total': grand_total
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/billing/<int:billing_id>/process-payment', methods=['POST'])
def process_payment(billing_id):
    """Process payment for billing"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        amount_paid = data.get('amount_paid', 0)
        payment_method = data.get('payment_method', 'Cash')
        transaction_id = data.get('transaction_id', '')
        
        # Add payment record
        cursor.execute('''
            INSERT INTO payment_history (billing_id, amount_paid, payment_method, transaction_id, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (billing_id, amount_paid, payment_method, transaction_id, 'Success'))
        
        conn.commit()
        
        # Check if fully paid
        cursor.execute('SELECT grand_total FROM billing WHERE id = ?', (billing_id,))
        grand_total = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(amount_paid) FROM payment_history WHERE billing_id = ?', (billing_id,))
        total_paid = cursor.fetchone()[0] or 0
        
        if total_paid >= grand_total:
            cursor.execute('UPDATE billing SET status = ? WHERE id = ?', ('Paid', billing_id))
        else:
            cursor.execute('UPDATE billing SET status = ? WHERE id = ?', ('Partially Paid', billing_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Payment recorded',
            'total_paid': total_paid,
            'remaining': max(0, grand_total - total_paid)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/billing/patient/<patient_id>', methods=['GET'])
def get_patient_billings(patient_id):
    """Get all billings for a patient"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM billing WHERE patient_id = ? ORDER BY created_at DESC', (patient_id,))
        billings = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({'success': True, 'billings': billings}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== HELPER FUNCTIONS ====================

def update_billing_totals(cursor, billing_id):
    """Helper function to update billing totals"""
    # Calculate pharmacy total
    cursor.execute('SELECT SUM(total_price) FROM pharmacy_items WHERE billing_id = ?', (billing_id,))
    pharmacy_total = cursor.fetchone()[0] or 0
    
    # Calculate lab total
    cursor.execute('SELECT SUM(test_price) FROM lab_tests WHERE billing_id = ?', (billing_id,))
    lab_total = cursor.fetchone()[0] or 0
    
    subtotal = pharmacy_total + lab_total
    discount = subtotal * 0.05  # 5% discount
    gst = (subtotal - discount) * 0.18  # 18% GST
    grand_total = subtotal - discount + gst
    
    cursor.execute('''
        UPDATE billing 
        SET pharmacy_total = ?, lab_total = ?, subtotal = ?, 
            discount = ?, gst = ?, grand_total = ?, updated_at = ?
        WHERE id = ?
    ''', (pharmacy_total, lab_total, subtotal, discount, gst, grand_total, datetime.now(), billing_id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

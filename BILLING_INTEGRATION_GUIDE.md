# Billing Database Integration Guide

## 📋 Overview
The billing system now connects Pharmacy, Lab, and Billing databases using SQLite3. All patient charges are tracked and stored in the database.

## 🗄️ Database Setup

### Files Created:
1. **billing.db** - SQLite3 database file
2. **create_billing_db.py** - Database initialization script
3. **billing_manager.py** - Flask backend API
4. **js/billing-integration.js** - Frontend integration script

### Database Tables:

#### 1. billing (Main Billing Records)
```sql
- id (PRIMARY KEY)
- patient_id (UNIQUE)
- patient_name
- gender, age
- phone, email
- appointment_date
- department, doctor_name
- pharmacy_items (JSON)
- lab_tests (JSON)
- pharmacy_total, lab_total
- subtotal, discount (5%), gst (18%), grand_total
- status (Pending Payment, Partially Paid, Paid)
- payment_method
- created_at, updated_at
```

#### 2. payment_history (Transaction Logs)
```sql
- id (PRIMARY KEY)
- billing_id (FOREIGN KEY)
- amount_paid
- payment_date
- payment_method
- transaction_id
- status
```

#### 3. pharmacy_items (Individual Items)
```sql
- id (PRIMARY KEY)
- billing_id (FOREIGN KEY)
- item_name
- quantity, unit_price, total_price
- added_at
```

#### 4. lab_tests (Individual Tests)
```sql
- id (PRIMARY KEY)
- billing_id (FOREIGN KEY)
- test_name, test_price
- added_at
```

## 🚀 Setup Instructions

### Step 1: Install Required Packages
```bash
pip install flask flask-cors
```

### Step 2: Start Backend Server
```bash
python billing_manager.py
```
Server runs on: `http://localhost:5000`

### Step 3: Add Script to billing.html
```html
<script src="js/billing-integration.js"></script>
```

## 📡 API Endpoints

### Create Billing Record
```javascript
POST /api/billing/create
{
  "patient_id": "P123",
  "patient_name": "John Doe",
  "gender": "Male",
  "age": 30,
  "phone": "9876543210",
  "email": "john@email.com",
  "appointment_date": "2025-11-22",
  "department": "Cardiology",
  "doctor_name": "Dr. Smith"
}
```

### Add Pharmacy Item
```javascript
POST /api/billing/{billing_id}/add-pharmacy
{
  "item_name": "Aspirin",
  "quantity": 2,
  "unit_price": 50
}
```

### Add Lab Test
```javascript
POST /api/billing/{billing_id}/add-lab
{
  "test_name": "Blood Test",
  "test_price": 500
}
```

### Process Payment
```javascript
POST /api/billing/{billing_id}/process-payment
{
  "amount_paid": 1000,
  "payment_method": "Cash",
  "transaction_id": "TXN123456"
}
```

### Get Billing Details
```javascript
GET /api/billing/{billing_id}
```

### Get All Patient Billings
```javascript
GET /api/billing/patient/{patient_id}
```

## 💻 Frontend Integration

### Usage in billing.html:

```javascript
// Create new billing
const billingId = await billingManager.createBilling({
  patient_id: "P123",
  patient_name: "John Doe",
  gender: "Male",
  age: 30,
  phone: "9876543210",
  email: "john@email.com",
  appointment_date: "2025-11-22",
  department: "Cardiology",
  doctor_name: "Dr. Smith"
});

// Add pharmacy item
addPharmacyItemToBilling("Aspirin", 2, 50);

// Add lab test
addLabTestToBilling("Blood Test", 500);

// Update totals (automatic calculation of discount & GST)
billingManager.updateBillingTotals();

// Process payment
billingManager.processPayment();

// Download invoice
billingManager.downloadInvoice();
```

## 🔌 Integration with Pharmacy & Lab Pages

### From Pharmacy Page:
```javascript
// When item added to cart
const event = new CustomEvent('pharmacyItemAdded', {
  detail: {
    item_name: 'Aspirin',
    quantity: 2,
    unit_price: 50
  }
});
document.dispatchEvent(event);
```

### From Lab Page:
```javascript
// When test added to cart
const event = new CustomEvent('labTestAdded', {
  detail: {
    test_name: 'Blood Test',
    test_price: 500
  }
});
document.dispatchEvent(event);
```

## 💰 Calculations

- **Subtotal** = Pharmacy Total + Lab Total
- **Discount** = Subtotal × 5%
- **GST** = (Subtotal - Discount) × 18%
- **Grand Total** = Subtotal - Discount + GST

## 📊 Example Workflow

1. Patient selects appointment and department
2. Billing record created with patient info
3. Patient adds pharmacy items → stored in `pharmacy_items` table
4. Patient adds lab tests → stored in `lab_tests` table
5. Totals automatically calculated (5% discount + 18% GST)
6. Payment processed → recorded in `payment_history`
7. Billing status updated (Pending/Partially Paid/Paid)
8. Invoice can be downloaded

## 🔐 Status Tracking

- **Pending Payment** - Billing created, no payment yet
- **Partially Paid** - Some amount paid but not complete
- **Paid** - Full amount paid

## 📝 Notes

- All prices in INR (₹)
- Automatic 5% discount applied
- 18% GST applied automatically
- Timestamps tracked for all transactions
- Each billing is linked to patient via patient_id
- Multiple payments can be made for single billing

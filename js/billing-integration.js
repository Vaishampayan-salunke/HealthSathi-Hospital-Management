/**
 * Billing Integration Script
 * Connects Pharmacy, Lab, and Billing Database
 * Communicates with billing_manager.py backend
 */

const BILLING_API = 'http://localhost:5000/api/billing';

class BillingManager {
    constructor() {
        this.currentBilling = null;
        this.init();
    }

    init() {
        // Initialize billing system
        console.log('✅ Billing Manager Initialized');
        this.setupEventListeners();
        this.loadBillingData();
    }

    setupEventListeners() {
        // Listen for pharmacy items added
        document.addEventListener('pharmacyItemAdded', (e) => {
            this.addPharmacyItem(e.detail);
        });

        // Listen for lab tests added
        document.addEventListener('labTestAdded', (e) => {
            this.addLabTest(e.detail);
        });

        // Process payment button
        const paymentBtn = document.getElementById('processPaymentBtn');
        if (paymentBtn) {
            paymentBtn.addEventListener('click', () => this.processPayment());
        }

        // Download invoice button
        const invoiceBtn = document.getElementById('downloadInvoiceBtn');
        if (invoiceBtn) {
            invoiceBtn.addEventListener('click', () => this.downloadInvoice());
        }
    }

    /**
     * Create a new billing record
     */
    async createBilling(patientData) {
        try {
            const response = await fetch(`${BILLING_API}/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(patientData)
            });
            const result = await response.json();
            if (result.success) {
                this.currentBilling = result.billing_id;
                console.log('✅ Billing created:', result.billing_id);
                return result.billing_id;
            }
        } catch (error) {
            console.error('❌ Error creating billing:', error);
        }
    }

    /**
     * Get billing details from database
     */
    async getBilling(billingId) {
        try {
            const response = await fetch(`${BILLING_API}/${billingId}`);
            const result = await response.json();
            if (result.success) {
                this.displayBilling(result);
                return result;
            }
        } catch (error) {
            console.error('❌ Error fetching billing:', error);
        }
    }

    /**
     * Add pharmacy item to billing
     */
    async addPharmacyItem(item) {
        if (!this.currentBilling) {
            console.warn('⚠️ No billing selected');
            return;
        }

        try {
            const response = await fetch(`${BILLING_API}/${this.currentBilling}/add-pharmacy`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item)
            });
            const result = await response.json();
            if (result.success) {
                console.log('✅ Pharmacy item added');
                this.updateBillingTotals();
            }
        } catch (error) {
            console.error('❌ Error adding pharmacy item:', error);
        }
    }

    /**
     * Add lab test to billing
     */
    async addLabTest(test) {
        if (!this.currentBilling) {
            console.warn('⚠️ No billing selected');
            return;
        }

        try {
            const response = await fetch(`${BILLING_API}/${this.currentBilling}/add-lab`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(test)
            });
            const result = await response.json();
            if (result.success) {
                console.log('✅ Lab test added');
                this.updateBillingTotals();
            }
        } catch (error) {
            console.error('❌ Error adding lab test:', error);
        }
    }

    /**
     * Update billing totals (5% discount, 18% GST)
     */
    async updateBillingTotals() {
        if (!this.currentBilling) return;

        try {
            const response = await fetch(`${BILLING_API}/${this.currentBilling}/update-totals`, {
                method: 'PUT'
            });
            const result = await response.json();
            if (result.success) {
                this.displayTotals(result);
                console.log('✅ Totals updated');
            }
        } catch (error) {
            console.error('❌ Error updating totals:', error);
        }
    }

    /**
     * Process payment
     */
    async processPayment() {
        const amount = parseFloat(document.getElementById('paymentAmount')?.value || 0);
        const method = document.getElementById('paymentMethod')?.value || 'Cash';
        const transactionId = document.getElementById('transactionId')?.value || '';

        if (amount <= 0) {
            alert('❌ Please enter a valid amount');
            return;
        }

        try {
            const response = await fetch(`${BILLING_API}/${this.currentBilling}/process-payment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount_paid: amount,
                    payment_method: method,
                    transaction_id: transactionId
                })
            });
            const result = await response.json();
            if (result.success) {
                alert('✅ Payment processed successfully!');
                this.getBilling(this.currentBilling);
            }
        } catch (error) {
            console.error('❌ Error processing payment:', error);
        }
    }

    /**
     * Display billing information
     */
    displayBilling(data) {
        const billingContainer = document.getElementById('billingContainer');
        if (!billingContainer) return;

        const { billing, pharmacy_items, lab_tests } = data;

        let html = `
            <div class="bill-summary">
                <h3>📋 Patient Information</h3>
                <p><strong>Patient ID:</strong> ${billing.patient_id}</p>
                <p><strong>Name:</strong> ${billing.patient_name}</p>
                <p><strong>Phone:</strong> ${billing.phone || 'N/A'}</p>
                <p><strong>Status:</strong> <span class="status-${billing.status.toLowerCase()}">${billing.status}</span></p>
            </div>
        `;

        // Pharmacy items
        if (pharmacy_items.length > 0) {
            html += '<div class="bill-section"><h4>💊 Pharmacy Charges</h4>';
            pharmacy_items.forEach(item => {
                html += `
                    <div class="item-row">
                        <span>${item.item_name} × ${item.quantity}</span>
                        <span>₹${item.total_price.toFixed(2)}</span>
                    </div>
                `;
            });
            html += '</div>';
        }

        // Lab tests
        if (lab_tests.length > 0) {
            html += '<div class="bill-section"><h4>🧪 Lab Test Charges</h4>';
            lab_tests.forEach(test => {
                html += `
                    <div class="item-row">
                        <span>${test.test_name}</span>
                        <span>₹${test.test_price.toFixed(2)}</span>
                    </div>
                `;
            });
            html += '</div>';
        }

        billingContainer.innerHTML = html;
    }

    /**
     * Display billing totals
     */
    displayTotals(totals) {
        const totalsContainer = document.getElementById('totalsContainer');
        if (!totalsContainer) return;

        const html = `
            <div class="totals">
                <div class="total-row">
                    <span>Subtotal:</span>
                    <strong>₹${totals.subtotal.toFixed(2)}</strong>
                </div>
                <div class="total-row discount">
                    <span>Discount (5%):</span>
                    <strong>-₹${totals.discount.toFixed(2)}</strong>
                </div>
                <div class="total-row">
                    <span>GST (18%):</span>
                    <strong>₹${totals.gst.toFixed(2)}</strong>
                </div>
                <div class="total-row grand-total">
                    <span>Grand Total:</span>
                    <strong>₹${totals.grand_total.toFixed(2)}</strong>
                </div>
            </div>
        `;

        totalsContainer.innerHTML = html;
    }

    /**
     * Download invoice as PDF
     */
    downloadInvoice() {
        if (!this.currentBilling) {
            alert('❌ No billing selected');
            return;
        }
        
        alert('📥 Invoice feature - Download functionality can be integrated with jsPDF library');
        console.log('Downloading invoice for billing:', this.currentBilling);
    }

    /**
     * Load billing data from localStorage or server
     */
    loadBillingData() {
        const storedBillingId = localStorage.getItem('currentBillingId');
        if (storedBillingId) {
            this.currentBilling = storedBillingId;
            this.getBilling(storedBillingId);
        }
    }

    /**
     * Save billing ID to localStorage
     */
    saveBillingId(billingId) {
        localStorage.setItem('currentBillingId', billingId);
    }

    /**
     * Clear billing data
     */
    clearBilling() {
        this.currentBilling = null;
        localStorage.removeItem('currentBillingId');
        console.log('✅ Billing cleared');
    }
}

// Initialize billing manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.billingManager = new BillingManager();
    console.log('✅ Billing system ready');
});

// Export functions for use in HTML
function addPharmacyItemToBilling(itemName, quantity, price) {
    const event = new CustomEvent('pharmacyItemAdded', {
        detail: {
            item_name: itemName,
            quantity: quantity,
            unit_price: price
        }
    });
    document.dispatchEvent(event);
}

function addLabTestToBilling(testName, price) {
    const event = new CustomEvent('labTestAdded', {
        detail: {
            test_name: testName,
            test_price: price
        }
    });
    document.dispatchEvent(event);
}

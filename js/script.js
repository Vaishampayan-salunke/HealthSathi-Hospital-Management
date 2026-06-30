document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("appointment-form");
  const tableBody = document.querySelector("#appointments-table tbody");

  // Example doctors by department
  const doctorsByDept = {
    Cardiology: ["Dr. Anil Kumar", "Dr. Priya Sharma"],
    Orthopedics: ["Dr. Rakesh Nair", "Dr. Meera Menon"],
    Dentistry: ["Dr. Kavita Rao", "Dr. Ashwin Patil"],
    Neurology: ["Dr. Sandeep Rao", "Dr. Neha Gupta"],
    Dermatology: ["Dr. Sunita Mehta", "Dr. Rajesh Bansal"],
    Gynecology: ["Dr. Anjali Sharma", "Dr. Kavya Reddy"],
    Pediatrics: ["Dr. Amit Jain", "Dr. Rekha Nair"],
    "General Medicine": ["Dr. Vinod Kumar", "Dr. Shruti Desai"]
  };

  // Populate doctors dynamically
  const deptSelect = document.getElementById("department");
  const docSelect = document.getElementById("doctor");

  deptSelect.addEventListener("change", function () {
    docSelect.innerHTML = "<option value=''>Select Doctor</option>";
    const selectedDept = this.value;
    if (doctorsByDept[selectedDept]) {
      doctorsByDept[selectedDept].forEach(doc => {
        const option = document.createElement("option");
        option.textContent = doc;
        docSelect.appendChild(option);
      });
    }
  });

  // Handle form submit
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const dept = deptSelect.value;
    const doctor = docSelect.value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;

    const row = `<tr>
      <td>${name}</td>
      <td>${dept}</td>
      <td>${doctor}</td>
      <td>${date}</td>
      <td>${time}</td>
    </tr>`;

    tableBody.innerHTML += row;
    form.reset();
  });
});

// Redirect with doctor + department info
function bookDoctor(card) {
  const dept = card.getAttribute("data-department");
  const doc = card.getAttribute("data-doctor");

  // Redirect with query params
  window.location.href = `appointments.html?dept=${encodeURIComponent(dept)}&doctor=${encodeURIComponent(doc)}`;
}

// Auto-fill department & doctor if query params exist
const params = new URLSearchParams(window.location.search);
const preDept = params.get("dept");
const preDoc = params.get("doctor");

if (preDept) {
  deptSelect.value = preDept;

  // Populate doctors for that department
  docSelect.innerHTML = "<option value=''>Select Doctor</option>";
  doctorsByDept[preDept].forEach(doc => {
    const option = document.createElement("option");
    option.textContent = doc;
    option.value = doc;
    docSelect.appendChild(option);
  });

  if (preDoc) {
    docSelect.value = preDoc;
  }
}

// Doctor options by department
const doctorsByDept = {
  "Cardiology": ["Dr. Anil Kumar", "Dr. Priya Sharma", "Dr. Rakesh Nair"],
  "Neurology": ["Dr. Meera Iyer", "Dr. Vikram Patel", "Dr. Arjun Reddy"],
  "Orthopedics": ["Dr. Sneha Rao", "Dr. Rajesh Gupta", "Dr. Kavya Menon"],
  "Pediatrics": ["Dr. Nisha Kapoor", "Dr. Sunil Jain", "Dr. Harsha Gowda"],
  "Dermatology": ["Dr. Manisha Joshi", "Dr. Rohit Desai", "Dr. Neha Verma"],
  "General Medicine": ["Dr. Suresh Pillai", "Dr. Rekha Nambiar", "Dr. Aditya Rao"]
};

const deptSelect = document.getElementById("dept");
const docSelect = document.getElementById("doctor");

// Populate doctors when dept changes
deptSelect.addEventListener("change", () => {
  const dept = deptSelect.value;
  docSelect.innerHTML = "<option value=''>Select Doctor</option>";
  if (dept && doctorsByDept[dept]) {
    doctorsByDept[dept].forEach(doc => {
      const option = document.createElement("option");
      option.value = doc;
      option.textContent = doc;
      docSelect.appendChild(option);
    });
  }
});

// Handle form submission
document.getElementById("appointmentForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const pname = document.getElementById("pname").value;
  const gender = document.getElementById("gender").value;
  const age = document.getElementById("age").value;
  const phone = document.getElementById("phone").value;
  const email = document.getElementById("email").value;
  const dept = deptSelect.value;
  const doctor = docSelect.value;
  const date = document.getElementById("date").value;
  const time = document.getElementById("time").value;

  const table = document.getElementById("appointmentsTable").querySelector("tbody");
  const row = table.insertRow();
  row.innerHTML = `
    <td>${pname}</td>
    <td>${gender}</td>
    <td>${age}</td>
    <td>${phone}</td>
    <td>${email}</td>
    <td>${dept}</td>
    <td>${doctor}</td>
    <td>${date}</td>
    <td>${time}</td>
  `;

  // Show popup
  document.getElementById("popup").style.display = "block";

  // Reset form
  this.reset();
});

// Close popup
function closePopup() {
  document.getElementById("popup").style.display = "none";
}

document.getElementById("appointmentForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const appointment = {
    name: document.getElementById("name").value,
    gender: document.getElementById("gender").value,
    age: document.getElementById("age").value,
    phone: document.getElementById("phone").value,
    email: document.getElementById("email").value,
    department: document.getElementById("department").value,
    doctor: document.getElementById("doctor").value,
    timeslot: document.getElementById("timeslot").value,
    date: document.getElementById("date").value,
    price: 500, // Fixed consultation fee
    img: "img/doctors/default.jpg",
    desc: "Doctor Consultation Fee"
  };

  // Save to localStorage for billing
  let appointmentBill = JSON.parse(localStorage.getItem("appointmentBill")) || [];
  appointmentBill.push(appointment);
  localStorage.setItem("appointmentBill", JSON.stringify(appointmentBill));

  alert("✅ Appointment booked! ₹500 consultation fee added to Billing.");
  window.location.href = "dashboard.html";
});

// Appointments
const appointmentBill = JSON.parse(localStorage.getItem("appointmentBill")) || [];
appointmentBill.forEach(addBillItem);

// ---------------- Pharmacy ----------------
const medicines = [
  { name: "Paracetamol", price: 25, desc: "Relieves mild pain & fever.", img: "img/meds/paracetamol.jpg" },
  { name: "Augmentin", price: 120, desc: "Antibiotic for bacterial infections.", img: "img/meds/augmentin.jpg" },
  { name: "Insulin", price: 350, desc: "Controls blood sugar in diabetes.", img: "img/meds/insulin.jpg" },
  { name: "Vitamin D", price: 50, desc: "Improves bone health & immunity.", img: "img/meds/vitamind.jpg" },
  { name: "Cough Syrup", price: 90, desc: "Soothes cough & throat irritation.", img: "img/meds/coughsyrup.jpg" },
  { name: "Aspirin", price: 40, desc: "Relieves pain, reduces fever.", img: "img/meds/aspirin.jpg" },
  { name: "Metformin", price: 200, desc: "Helps manage type 2 diabetes.", img: "img/meds/metformin.jpg" },
  { name: "Antacid", price: 60, desc: "Relieves acidity & indigestion.", img: "img/meds/antacid.jpg" },
  { name: "Ibuprofen", price: 75, desc: "Reduces pain, swelling & fever.", img: "img/meds/ibuprofen.jpg" },
  { name: "Amoxicillin", price: 150, desc: "Antibiotic for bacterial infections.", img: "img/meds/amoxicillin.jpg" },
  { name: "ORS Solution", price: 30, desc: "Prevents dehydration.", img: "img/meds/ors.jpg" },
  { name: "Cetirizine", price: 20, desc: "Relieves allergy & cold symptoms.", img: "img/meds/cetirizine.jpg" }
];

const medicineList = document.getElementById("medicineList");
const cartTable = document.querySelector("#cartTable tbody");
const totalPriceEl = document.getElementById("totalPrice");
let cart = [];

// Load medicines into grid
function loadMedicines(list = medicines) {
  medicineList.innerHTML = "";
  list.forEach((med, index) => {
    const div = document.createElement("div");
    div.className = "medicine-item";
    div.innerHTML = `
      <img src="${med.img}" alt="${med.name}">
      <h3>${med.name}</h3>
      <p class="desc">${med.desc}</p>
      <p class="price">₹${med.price}</p>
      <button onclick="addToCart(${index})">Add to Cart</button>
    `;
    medicineList.appendChild(div);
  });
}

// Search medicines
function searchMedicine() {
  const query = document.getElementById("medicineSearch").value.toLowerCase();
  const filtered = medicines.filter(med => med.name.toLowerCase().includes(query));
  loadMedicines(filtered);
}

// Add to cart
function addToCart(index) {
  cart.push(medicines[index]);
  renderCart();
}

// Render cart
function renderCart() {
  cartTable.innerHTML = "";
  let total = 0;
  cart.forEach((item, i) => {
    total += item.price;
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.name}</td>
      <td>₹${item.price}</td>
      <td><button onclick="removeFromCart(${i})">❌</button></td>
    `;
    cartTable.appendChild(row);
  });
  totalPriceEl.textContent = total;
}

// Remove from cart
function removeFromCart(i) {
  cart.splice(i, 1);
  renderCart();
}

// Checkout → Save cart to localStorage → Redirect to billing
function checkout() {
  if (cart.length === 0) {
    alert("Cart is empty!");
    return;
  }
  localStorage.setItem("pharmacyCart", JSON.stringify(cart));
  alert("✅ Order placed successfully! Redirecting to Billing...");
  window.location.href = "billing.html";
}

// Initialize
if (medicineList) {
  loadMedicines();
}



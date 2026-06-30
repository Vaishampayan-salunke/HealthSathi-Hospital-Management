# HealthSathi Hospital Management System

## Project Overview

HealthSathi is a hospital management system built as a web-based interface for managing key hospital operations. It provides navigation to appointments, departments, pharmacy, lab services, billing, AI chatbot support, emergency contacts, and nearby hospitals. The project includes a polished dashboard experience with responsive design, multilingual support, and interactive department navigation.

## Key Features

- Responsive hospital dashboard with department access cards
- Navigation links for common hospital services
- Language selector with support for English, Hindi, Tamil, Telugu, and Kannada
- Floating emergency phone icon for quick calls
- Clean, modern UI with animation and gradient styling
- Billing integration scripts and database utilities
- Dedicated pages for appointments, departments, pharmacy, lab, billing, chatbot, nearby hospitals, and emergency services

## Project Structure

- `admin.html` - Admin interface page
- `appointments.html` - Appointment scheduling and information page
- `billing.html` - Billing interface page
- `chatbot.html` - AI chatbot interface page
- `create_billing_db.py` - Script to create the billing database
- `dashboard.html` - Main dashboard page with navigation and department cards
- `departments.html` - Department details and service information
- `emergency.html` - Emergency contact page
- `lab.html` - Laboratory services page
- `nearbyhospital.html` - Nearby hospitals and location page
- `main.PY` - Main Python script for backend operations or administration tasks
- `billing_manager.py` - Billing logic and management script
- `tempCodeRunnerFile.PY` - Temporary script file used during development
- `css/` - Stylesheet folder
  - `style.css` - Global styling for the site
- `data/` - Data assets folder
  - `doctors.json` - Doctor information data
  - `hospitals-merged.json` - Hospital location and details data
- `img/` - Image assets for dashboard, doctors, icons, lab, and medicines
- `js/` - JavaScript folder
  - `billing-integration.js` - Billing integration logic
  - `language-config.js` - Language translation and UI localization
  - `script.js` - General page behavior and interactive scripts

## Technologies Used

- HTML5 for page structure
- CSS3 for layout, typography, and responsive design
- JavaScript for language selection and interactive behavior
- Python for backend billing logic and database utilities
- JSON data for doctors and hospitals

## How to Use

1. Open `dashboard.html` in a web browser to launch the main hospital dashboard.
2. Use the navigation menu to access appointments, departments, pharmacy, lab, billing, chatbot, nearby hospitals, and emergency pages.
3. Use the language selector to switch between supported languages and update content labels.
4. For backend billing setup, run `create_billing_db.py` to generate the billing database.

## Notes

- The dashboard is designed to be visually engaging and accessible across desktop and mobile devices.
- `language-config.js` handles multilingual UI text updates and flag display.
- The project is ideal for a hospital management demonstration or prototype with static front-end pages and Python billing utilities.

## License

This project is provided as-is for demonstration and learning purposes.

# Car Rental System

A full-featured car rental system with admin and user dashboards, built with Flask, SQLAlchemy, and Jinja templates.

## Features

- User authentication (login/registration)
- Admin dashboard for managing cars and car models
- User dashboard for browsing and renting cars
- Comprehensive car management system
- Rental history tracking
- Responsive design with Bootstrap

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional, can use SQLite for local development)

### Installation

1. Clone the repository or extract the zip file
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - MacOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set environment variables:
   - For PostgreSQL (recommended for production):
     ```
     export DATABASE_URL=postgresql://username:password@localhost/car_rental_db
     export SESSION_SECRET=your_secret_key
     ```
   - For SQLite (quick local development):
     The app will default to SQLite if no DATABASE_URL is provided

### Running the Application

1. Run the application:
   ```
   python main.py
   ```
2. Open a web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

### Admin Credentials

- Username: admin
- Password: admin123

## Database Structure

- **User**: Stores user information, authentication details
- **Car**: Represents car brands and basic information
- **CarModel**: Detailed car model specs (belongs to a Car)
- **Rental**: Rental records with date ranges and status

## License

This project is open source and available for personal and educational use.
# Movie Ticket Booking System

A web-based movie ticket booking system built with Django. Users can browse movies, view showtimes, select seats, make bookings. Admins can perform full CRUD operations on movies and showtimes.

---

## Features

- Movie listing
- Showtime selection per movie
- Seat booking with real-time availability
- User login and registration
- Booking confirmation (QR code)
- Django Admin for managing all data (Movies, Showtimes, Bookings)

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- virtualenv (recommended)

---

### 1. Clone the repository

```bash
git clone https://github.com/NeesaPandeyy/Movie-Ticket-Booking-System.git
```

### 2. Create and activate virtual environment

```bash
python -m venv myenv
source myenv/bin/activate  # For Linux/macOS
myenv\Scripts\activate  # For Windows
```

### 3. Install required packages

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Running the Application

```bash
python manage.py runserver or http://127.0.0.1:8000/
Admin Panel: http://127.0.0.1:8000/admin/
```

## Python Version & Libraries Used

- Python 3.10+
- Django 4.x
- SQLite (default DB)
- Pillow (image/QR support)
- qrcode (QR code generation)

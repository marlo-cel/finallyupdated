# Multi-Domain Intelligence Platform

**Student:** Asher Atubra  
**ID:** M01096929  
**Course:** CST1510 - CW2

---

## Project Overview

A comprehensive web-based intelligence platform integrating three critical operational domains:

- **🛡️ Cybersecurity Domain** - Incident tracking, threat analysis, security analytics
- **📊 Data Science Domain** - Dataset management, size analytics, metadata cataloging  
- **🎫 IT Operations Domain** - Support ticket management, SLA monitoring, resolution tracking

Built with modern **Object-Oriented Programming** principles, featuring secure authentication, real-world CSV data integration, and interactive visualizations.

---

## 🏗️ Architecture & OOP Design

### System Architecture

```
┌─────────────────────────────────────────┐
│     Presentation Layer (Streamlit)      │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │  Cyber  │ │  Data   │ │    IT    │ │
│  │Dashboard│ │ Science │ │Operations│ │
│  └─────────┘ └─────────┘ └──────────┘ │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│      Business Logic Layer               │
│  ┌────────────────────────────────┐    │
│  │   Repository Pattern            │    │
│  │  (Data Access Abstraction)      │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │   Service Layer                 │    │
│  │  (User Authentication, etc.)    │    │
│  └────────────────────────────────┘    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│         Model Layer (Domain)            │
│  ┌──────┐ ┌──────────┐ ┌──────────┐   │
│  │ User │ │ Incident │ │ Dataset  │   │
│  └──────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌─────────────────┐     │
│  │  Ticket  │ │  Enumerations   │     │
│  └──────────┘ └─────────────────┘     │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│          Data Layer                     │
│  ┌────────────┐      ┌────────────┐    │
│  │  SQLite    │◄────►│  CSV Files │    │
│  │  Database  │      │   (Import) │    │
│  └────────────┘      └────────────┘    │
└─────────────────────────────────────────┘
```

### Key OOP Concepts Demonstrated

1. **Encapsulation** - Data and methods bundled in classes
2. **Abstraction** - Complex operations hidden behind simple interfaces
3. **Validation** - Self-validating objects ensure data integrity
4. **Type Safety** - Enums prevent invalid values
5. **Separation of Concerns** - Clear boundaries between layers

---

## 📦 Project Structure

```
CW2_M01096929_CST1510/
│
├── app.py                          # Main application entry
├── import_csv_data.py             # CSV import script (run this first!)
├── requirements.txt               # Python dependencies
│
├── DATA/                          # CSV source files
│   ├── cyber_incidents.csv       # 115 security incidents
│   ├── datasets_metadata.csv     # 5 datasets
│   ├── it_tickets.csv            # 150 IT tickets
│   └── users.txt                 # Initial user data
│
├── app/                          # Application code
│   │
│   ├── models/                   # OOP Model Classes (NEW!)
│   │   ├── __init__.py
│   │   ├── user.py              # User entity with auth
│   │   ├── security_incident.py # SecurityIncident class
│   │   ├── dataset.py           # Dataset class
│   │   └── it_ticket.py         # ITTicket class
│   │
│   ├── repositories/             # Data Access Layer (NEW!)
│   │   └── base_repository.py   # Repository pattern
│   │
│   ├── utils/                    # Utilities (NEW!)
│   │   └── csv_data_loader.py   # CSV import utility
│   │
│   ├── services/                 # Business Logic
│   │   └── user_service.py      # Authentication
│   │
│   └── data/                     # Database Layer
│       ├── db.py                # Connection management
│       ├── schema.py            # Table definitions
│       ├── incidents.py         # Incident operations
│       ├── datasets.py          # Dataset operations
│       └── tickets.py           # Ticket operations
│
├── pages/                        # Streamlit Pages
│   ├── Cybersecurity.py         # Security dashboard
│   ├── Data_Science.py          # Dataset analytics
│   └── IT_Operations.py         # Ticket management
│
└── docs/                         # Documentation
    ├── README.md                # This file
    └── [other docs]
```

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `bcrypt==4.2.0` - Password hashing
- `streamlit>=1.28.0` - Web framework
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.17.0` - Visualizations

### Step 2: Import CSV Data (IMPORTANT!)

**This step loads all your CSV data into the database:**

```bash
python import_csv_data.py
```

This will import:
- ✅ **115 cyber incidents** from `cyber_incidents.csv`
- ✅ **5 datasets** from `datasets_metadata.csv`
- ✅ **150 IT tickets** from `it_tickets.csv`

**Expected output:**
```
=== Importing Cyber Incidents ===
✅ Loaded 115 rows from cyber_incidents.csv
   Imported 20 incidents...
   Imported 40 incidents...
   ...
✅ Successfully imported 115 cyber incidents

=== Importing Datasets ===
✅ Loaded 5 rows from datasets_metadata.csv
✅ Successfully imported 5 datasets

=== Importing IT Tickets ===
✅ Loaded 150 rows from it_tickets.csv
   Imported 20 tickets...
   ...
✅ Successfully imported 150 IT tickets

📊 Database Contents:
   - Cyber Incidents: 115
   - Datasets: 5
   - IT Tickets: 150
   - Total Records: 270
```

### Step 3: Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Step 4: Login

**Default user:**
- Username: `Alex`
- Password: (check `DATA/users.txt` - hashed with bcrypt)

Or create a new account using the Register tab!

---

## 💡 Understanding the OOP Structure

### Before (Procedural) vs After (OOP)

**Old Way - Procedural:**
```python
# Data scattered, manual validation
from data import incidents

title = "Attack"
severity = "High"  # Could be typo: "high", "HIGH", "Hihg"!
date = "2024-01-01"

# Manual validation everywhere
if not title:
    raise ValueError("Title required")
if severity not in ["Low", "Medium", "High", "Critical"]:
    raise ValueError("Invalid severity")

# Direct database access
incident_id = incidents.create_incident(title, "", severity, date)
```

**New Way - Object-Oriented:**
```python
# Everything bundled, automatic validation
from models.security_incident import SecurityIncident, Severity

# Create object (validates automatically!)
incident = SecurityIncident(
    incident_id=None,
    title="Attack",
    description="Details",
    severity=Severity.HIGH.value  # Type-safe! Can't typo!
)

# Save using repository
from repositories.base_repository import SecurityIncidentRepository
repo = SecurityIncidentRepository()
incident_id = repo.create(incident)
```

**Benefits:**
- ✅ **Less code** - No repetitive validation
- ✅ **Type safety** - Enums prevent typos
- ✅ **Self-validating** - Objects check themselves
- ✅ **Testable** - Easy to unit test
- ✅ **Maintainable** - Clear structure

### Real-World Analogy 🎓

**Classes are like Blueprints:**
- **Blueprint (Class)** = Plan for a house
- **House (Object)** = Actual built house
- **Methods** = What the house can do (open door, turn on lights)

```python
class House:  # Blueprint
    def open_door(self):
        print("Door opened!")

my_house = House()  # Build the house
my_house.open_door()  # Use it!
```

**Repository is like a Librarian:**
- You don't search bookshelves yourself
- You ask the librarian (repository) to find books
- Librarian knows where everything is stored

```python
# Instead of: searching_database_yourself()
# You do:
incidents = repository.get_all()  # Librarian fetches for you!
```

---

## 📊 Features & Capabilities

### 1. Cybersecurity Dashboard 🛡️

**Data:** 115 real security incidents from CSV

**Features:**
- **Analytics Dashboard**
  - Time series analysis with interactive charts
  - Severity distribution (pie charts, bar charts)
  - Monthly trend analysis
  - Critical incident tracking
  
- **Incident Management**
  - Create, view, update, delete incidents
  - Search and filter by severity
  - Link incidents to user accounts
  
- **Smart Visualizations**
  - Color-coded severity levels
  - Date range analytics
  - Incident frequency metrics

**CSV Columns Used:**
- `incident_id`, `timestamp`, `severity`, `category`, `status`, `description`

### 2. Data Science Module 📊

**Data:** 5 dataset records from CSV

**Features:**
- **Dataset Analytics**
  - Size comparison charts
  - Distribution analysis (pie, treemap)
  - Statistical summaries
  
- **Dataset Management**
  - Add/edit/delete datasets
  - Track rows and metadata
  - Link to owners
  
- **Insights**
  - Total rows across all datasets
  - Average dataset size
  - Largest/smallest datasets

**CSV Columns Used:**
- `dataset_id`, `name`, `rows`, `columns`, `uploaded_by`, `upload_date`

### 3. IT Operations Center 🎫

**Data:** 150 support tickets from CSV

**Features:**
- **Ticket Analytics**
  - Status distribution
  - Priority breakdown
  - Resolution tracking
  
- **Ticket Management**
  - Create/edit/delete tickets
  - Status updates
  - Priority assignment
  
- **Metrics**
  - Open vs resolved counts
  - Priority distribution
  - Support team assignments

**CSV Columns Used:**
- `ticket_id`, `priority`, `description`, `status`, `assigned_to`, `created_at`, `resolution_time_hours`

---

## 🔒 Security Features

### Password Security
- **Bcrypt Hashing** - Military-grade one-way encryption
- **Automatic Salting** - Each password uniquely encrypted
- **No Plain Text Storage** - Passwords never stored readable

```python
# Plain password NEVER stored
plain = "mypassword123"
hashed = User.hash_password(plain)  
# Result: "$2b$12$vNLZU6EORZWiW0loB0H0NueyaDRM..."

# Verification without storing plain text
User.verify_password(plain, hashed)  # Returns True/False
```

### SQL Injection Prevention
- **Parameterized Queries** - Never concatenate SQL strings
- **SQLite Row Factory** - Built-in injection protection

```python
# ❌ BAD: f"SELECT * FROM users WHERE name = '{username}'"
# ✅ GOOD: "SELECT * FROM users WHERE name = ?", (username,)
```

### Input Validation
- **Model-Level** - Validated when object created
- **Length Checks** - Minimum requirements enforced
- **Character Restrictions** - No special characters in usernames

---

## 📈 Visualizations

### Cybersecurity Dashboard
1. **Time Series** - Incidents over time by severity
2. **Pie Chart** - Severity distribution
3. **Bar Charts** - Incident counts
4. **Monthly Trends** - Volume patterns

### Data Science Module
1. **Size Comparison** - Bar charts
2. **Treemap** - Visual size representation
3. **Statistics** - Min, max, median, std dev

### IT Operations
1. **Status Pie Chart** - Open/resolved distribution
2. **Priority Bars** - Urgency breakdown

---

## 🧪 Testing Your Setup

### Verify CSV Import

After running `import_csv_data.py`, check:

```python
# In Python console or new script:
import sys
sys.path.insert(0, 'app')

from data.db import get_connection

with get_connection() as conn:
    incidents = conn.execute("SELECT COUNT(*) FROM cyber_incidents").fetchone()[0]
    datasets = conn.execute("SELECT COUNT(*) FROM datasets_metadata").fetchone()[0]
    tickets = conn.execute("SELECT COUNT(*) FROM it_tickets").fetchone()[0]
    
    print(f"Incidents: {incidents}")  # Should be 115
    print(f"Datasets: {datasets}")    # Should be 5
    print(f"Tickets: {tickets}")      # Should be 150
```

### Test in Web App

1. Login to app
2. Navigate to Cybersecurity dashboard
3. Check "Analytics & Visualizations" - should see 115 incidents
4. Navigate to Data Science dashboard
5. Check analytics - should see 5 datasets
6. Navigate to IT Operations
7. Should see 150 tickets

---

## 🐛 Troubleshooting

### Problem: "No incidents found"

**Solution:** Run the CSV import script
```bash
python import_csv_data.py
```

### Problem: "CSV file not found"

**Solution:** Ensure CSV files are in `DATA/` directory:
```
DATA/
├── cyber_incidents.csv
├── datasets_metadata.csv
└── it_tickets.csv
```

### Problem: "Module not found"

**Solution:** Install requirements
```bash
pip install -r requirements.txt
```

### Problem: Database locked

**Solution:** Close any open database connections and restart Streamlit
```bash
# Stop Streamlit (Ctrl+C)
# Delete database
rm app/data/db/incidents.db
# Reimport
python import_csv_data.py
# Restart
streamlit run app.py
```

---

## 📚 Learning Resources

### OOP Concepts

**Encapsulation Example:**
```python
class SecurityIncident:
    def __init__(self, title):
        self.title = title  # Data
    
    def is_critical(self):  # Method
        return self.severity == "Critical"
```

**Validation Example:**
```python
class User:
    def __init__(self, username):
        if len(username) < 3:
            raise ValueError("Username too short")
        self.username = username
```

**Enum Example:**
```python
class Severity(Enum):
    LOW = "Low"
    HIGH = "High"

# Usage
incident.severity = Severity.HIGH.value  # Type-safe!
```

### Design Patterns Used

1. **Repository Pattern** - Data access abstraction
2. **Factory Methods** - Object creation with logic
3. **Enumerations** - Type-safe constants
4. **MVC-like** - Separation of concerns

---

## 🎓 For Your Report

### Key Points to Highlight

1. **OOP Transformation**
   - From procedural to object-oriented
   - Models with self-validation
   - Repository pattern for data access

2. **Real Data Integration**
   - 270+ records from CSV files
   - Automated import process
   - Three integrated domains

3. **Security Implementation**
   - Bcrypt password hashing
   - SQL injection prevention
   - Input validation

4. **User Experience**
   - Interactive dashboards
   - Real-time visualizations
   - Responsive design

### Diagrams to Include

1. **System Architecture** - 4-layer diagram (see above)
2. **Class Hierarchy** - Show model relationships
3. **Data Flow** - CSV → Database → UI
4. **Security Flow** - Authentication process

---

## 🚀 Future Enhancements

1. **Advanced Analytics**
   - Machine learning predictions
   - Anomaly detection
   - Trend forecasting

2. **Real-Time Features**
   - Live dashboards
   - WebSocket notifications
   - Auto-refresh

3. **API Development**
   - RESTful endpoints
   - Mobile app support
   - Third-party integrations

---

## 📞 Support

**Student:** Asher Atubra  
**ID:** M01096929  
**Course:** CST1510 - CW2

For issues or questions, contact through the course portal.

---

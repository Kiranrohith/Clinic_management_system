

````
# 🏥 Clinic Appointment Management System

A full-stack clinic appointment management system designed to manage doctor schedules, patient appointments, walk-in consultations, prescriptions, waiting lists, contact enquiries, and role-based hospital operations.

The application provides separate dashboards and permissions for **Admin, Front Desk, and Doctor** users, while patients can access the public booking system without creating a traditional account.

---

## 📌 Overview

The Clinic Appointment Management System is designed to digitize the daily operations of a hospital/clinic.

The system supports two major sides:

### Public / Patient Side

Patients can:

- Browse doctors
- Filter doctors by specialization
- View available appointment slots
- Book appointments using mobile OTP verification
- Book appointments for themselves or family members during the authenticated session
- View appointment-related notifications
- Receive doctor cancellation notifications
- Receive follow-up reminders
- Submit contact/enquiry forms
- Join a waiting list when required

### Hospital Staff Side

The hospital has three authenticated roles:

- **Admin**
- **Front Desk**
- **Doctor**

After login, the user's role is identified and the corresponding dashboard is displayed.

```
Login
  │
  ▼
Authenticate Email + Password
  │
  ▼
Identify User Role
  │
  ├── ADMIN ───────► Admin Dashboard
  │
  ├── FRONTDESK ──► Front Desk Dashboard
  │
  └── DOCTOR ─────► Doctor Dashboard
````

Patients are maintained separately from the staff `users` system because they do not require permanent staff accounts.

---

# 🎯 Key Features

## 🔐 Role-Based Authentication

The application uses role-based access control.

Staff users authenticate using:

* Email
* Password

After successful authentication, the backend determines the user's role and provides access to the appropriate module.

### Roles

| Role       |                          | Responsibilities |
                                                                         |
---------------------------------------------------------------------------------------- |
| Admin      | Manage hospital configuration, staff accounts, doctors, specializations and      
                master slots |
| Front Desk | Manage appointments, walk-ins, contact enquiries and patient-facing operational 
                tasks    |
| Doctor     | Manage availability, appointments, consultations, prescriptions and follow-ups           |

---

# 👨‍💼 Admin Module

The Admin is responsible for configuring and managing the hospital system.

### Admin capabilities

* View administrative dashboard
* Create doctor accounts
* Create Front Desk accounts
* Manage staff accounts
* Activate/deactivate users
* Manage doctor specializations
* Configure hospital master time slots
* Configure clinic working hours
* Configure morning and afternoon breaks
* Configure lunch break
* Configure advance booking period
* View contact enquiries when required
* Manage own profile

### Clinic Scheduling Configuration

The Admin defines hospital-wide scheduling rules.

For example:

```
Hospital Working Hours
09:00 AM → 07:00 PM

Morning Break
11:00 AM → 11:20 AM

Lunch Break
01:00 PM → 02:20 PM

Afternoon Break
04:00 PM → 04:20 PM
```

The system does not create appointment slots during these break periods.

The Admin also maintains the hospital's static master slots.

---

# 👨‍⚕️ Doctor Module

The Doctor dashboard is focused on daily consultations and schedule management.

### Doctor sidebar

```
Dashboard
Availability
History Calendar
Profile
```

### Doctor Dashboard

The dashboard displays the doctor's appointments for the current day.

The doctor can select a booked appointment/slot to view:

* Patient basic information
* Previous prescriptions
* Previous consultation history
* Prescribing doctors
* Current appointment details

The doctor can then conduct the consultation and create a new prescription.

---

## Doctor Availability

Doctors can configure their availability for **five days at a time**:

```
Today
Day 2
Day 3
Day 4
Day 5
```

The system follows a rolling five-day booking window.

For example:

```
Today       → Day 1
Tomorrow    → Day 2
Day +2      → Day 3
Day +3      → Day 4
Day +4      → Day 5
```

The sixth day becomes available when the next day becomes the current day.

For each date, the doctor can:

* Enable availability
* Disable availability
* Select a start time
* Select an end time

The system then opens only the hospital's predefined master slots that fall inside the doctor's selected availability period.

For example:

```
Doctor Availability

09:00 → 13:00
```

If the hospital has:

```
09:00
09:15
09:30
09:45
10:00
...
```

those valid slots become available to patients.

Slots falling outside the doctor's availability or inside hospital break periods are not opened.

---

# 🚨 Doctor Emergency Cancellation

Doctors can cancel their availability because of an emergency.

They can either:

### Cancel the entire day

```
Entire Day
    ↓
All affected slots cancelled
```

or:

### Cancel a time range

```
14:00 → 17:00
```

Only the remaining affected slots are cancelled.

Cancelled slots are **not reopened for booking**.

Instead, their status becomes:

```
CANCELLED_BY_DOCTOR
```

The slot remains visible as unavailable/booked so patients cannot accidentally book it again.

Affected patients receive a notification such as:

```
We are sorry. Your appointment has been cancelled
due to an unexpected change in the doctor's availability.

Please reschedule your appointment using our booking link.
```

The notification includes the hospital booking link.

---

# 📅 Doctor History Calendar

Doctors have a calendar-based consultation history.

They can navigate:

* Previous days
* Previous months
* Previous years

Selecting a historical date displays the doctor's activity for that date.

The doctor can view:

* Available slots
* Booked patients
* Appointment history
* Consultation details
* Prescriptions
* Prescription date
* Doctor who prescribed the treatment

This provides a historical view of the doctor's consultations.

---

# 💊 Prescriptions

After consulting a patient, the doctor can create a prescription containing information such as:

* Diagnosis
* Medicines
* Dosage
* Frequency
* Duration
* Doctor advice
* Internal notes
* Follow-up date

A prescription is associated with the corresponding appointment, patient and doctor.

The patient's previous prescriptions are displayed when the doctor opens the patient's appointment.

### Prescription Editing Rule

A prescription can be edited on the same day through the consultation workflow.

After the consultation day, the prescription becomes historical data and is accessed through the history calendar.

---

# 🔄 Follow-Up

Doctors can specify a follow-up date during consultation.

For example:

```
Follow-up Date:
15 August 2026
```

The system can send the patient a reminder such as:

```
Your doctor has recommended a follow-up
consultation on 15 August 2026.

Please book your appointment using our booking link.
```

This allows follow-up recommendations to become part of the appointment workflow.

---

# 🧑‍💼 Front Desk Module

The Front Desk handles the clinic's day-to-day operational activities.

### Front Desk sidebar

```
Dashboard
Appointments
Walk-in Tokens
Contact Queries
Profile
```

---

## Front Desk Dashboard

The dashboard provides a real-time view of today's operations.

It can display:

* Today's appointments
* Upcoming appointments
* Walk-in tokens
* Waiting list information
* New contact enquiries

The dashboard is designed to help reception/front-desk staff quickly understand the current workload.

---

# 📅 Appointment Management

The Front Desk can:

* View today's appointments
* Filter appointments by doctor
* View patient information
* Book appointments for patients
* Handle appointment-related operations
* View appointment history
* Cancel appointments when permitted

Appointments can originate from different sources:

```
ONLINE
FRONTDESK
WALKIN
```

---

# 🚶 Walk-In Token Management

Patients who arrive without an online appointment can be registered as walk-ins.

The Front Desk can:

* Create walk-in tokens
* Assign a doctor
* View today's tokens
* Track token status
* Update token status
* View historical walk-in records

Example token lifecycle:

```
WAITING
   ↓
IN_PROGRESS
   ↓
COMPLETED
```

A walk-in can also be cancelled when necessary.

---

# 📩 Contact Queries

Patients can submit a contact form from the public website.

Example:

```
Name
Phone
Email
Subject
Message
```

The request is stored as a contact query.

The Front Desk can:

* View enquiries
* Search enquiries
* Filter by status
* Add internal notes
* Handle enquiries
* Track who is handling the enquiry
* Close completed enquiries

The contact query lifecycle is:

```
NEW
 ↓
IN_PROGRESS
 ↓
CLOSED
```

The purpose is to allow the Front Desk to contact patients and understand their requirements or connect them with the appropriate hospital staff.

---

# 📋 Waiting List

The system supports a waiting-list mechanism for appointment slots.

If a desired appointment slot is unavailable, a patient can be placed into the waiting list.

A waiting entry contains:

* Patient
* Requested availability/slot
* Position
* Status
* Notification time
* Expiration time
* Confirmation time

Waiting-list states include:

```
WAITING
NOTIFIED
CONFIRMED
EXPIRED
CANCELLED
```

When a slot becomes available, the system can notify eligible waiting-list patients.

---

# 👤 Patient Booking

Patients do not require a traditional staff account.

The public booking flow is:

```
Patient Website
      │
      ▼
Choose Specialization
      │
      ▼
Choose Doctor
      │
      ▼
Choose Date
      │
      ▼
View Available Slots
      │
      ▼
Select Slot
      │
      ▼
Enter Patient Details
      │
      ▼
OTP Verification
      │
      ▼
Appointment Created
```

The patient can authenticate through mobile OTP.

After successful OTP verification, the patient can continue booking appointments during the session without repeatedly verifying their phone for every booking.

---

# 📆 Five-Day Booking Window

Patients can book doctors only within the current five-day window:

```
Today
Tomorrow
Day +2
Day +3
Day +4
```

The system does not expose dates beyond this booking window.

This keeps the scheduling model similar to the intended hospital booking experience.

---

# 🔔 Notifications & SSE

The application uses **Server-Sent Events (SSE)** for real-time notifications.

Instead of repeatedly refreshing the browser, connected users can receive server-generated events immediately.

Example:

```
Backend Event
      │
      ▼
SSE Connection
      │
      ▼
Connected Front Desk / Patient
      │
      ▼
Notification
```

SSE can be used for events such as:

* New contact enquiry
* Appointment cancellation
* Doctor emergency cancellation
* Appointment updates
* Waiting-list notifications
* Follow-up reminders

For example, when a patient submits a contact form:

```
Patient
   │
   ▼
POST Contact Query
   │
   ▼
Save to Database
   │
   ▼
Broadcast SSE Event
   │
   ▼
Front Desk Browser
   │
   ▼
"New Contact Request"
```

The Front Desk UI can then refresh the relevant TanStack Query data without manually refreshing the page.

---

# 🗄️ Database Design

The system uses PostgreSQL as its relational database.

Major entities include:

```
roles
users
doctors
specializations
doctor_specializations
patients
slots
doctor_availability
appointments
waiting_list
prescriptions
walk_in_tokens
otp_verifications
notifications
contact_queries
clinic_settings
```

### Important relationships

```
users
  │
  ├── roles
  │
  └── doctors
        │
        └── doctor_specializations
                │
                └── specializations

doctors
  │
  └── doctor_availability
          │
          └── slots

doctor_availability
  │
  └── appointments
          │
          ├── patients
          │
          └── prescriptions
```

The appointment references the doctor's availability rather than storing a separate doctor reference because the availability record already identifies the doctor.

---

# 🏗️ Architecture

The backend follows a layered architecture.

```
Frontend
React + TypeScript
        │
        ▼
TanStack Query / Router
        │
        ▼
FastAPI API
        │
        ▼
Routes
        │
        ▼
Services
        │
        ▼
Repositories
        │
        ▼
SQLAlchemy ORM
        │
        ▼
PostgreSQL
```

### Backend responsibilities

#### Routes

Responsible for:

* HTTP endpoints
* Request/response handling
* Authentication dependencies
* Calling services

#### Services

Responsible for:

* Business logic
* Validation
* Workflow coordination
* Calling repositories

#### Repositories

Responsible for:

* Database queries
* CRUD operations
* SQLAlchemy operations

#### Models

Represent database tables using SQLAlchemy ORM.

#### Schemas

Pydantic models validate API requests and responses.

---

# 🧰 Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* PostgreSQL
* SSE-Starlette

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* TanStack Query
* TanStack Router

## Infrastructure

* Docker
* Docker Compose
* PostgreSQL
* pgAdmin

---

# 🔄 Example End-to-End Appointment Flow

A typical online appointment follows this workflow:

```
Patient
   │
   ▼
Hospital Website
   │
   ▼
Select Specialization
   │
   ▼
Select Doctor
   │
   ▼
Select Date
   │
   ▼
Backend checks:
   ├── Five-day booking window
   ├── Doctor availability
   ├── Hospital working hours
   ├── Hospital breaks
   └── Slot status
   │
   ▼
Available Slots
   │
   ▼
Patient Selects Slot
   │
   ▼
Enter Patient Details
   │
   ▼
OTP Verification
   │
   ▼
Create Appointment
   │
   ├── Appointment record
   ├── Slot becomes BOOKED
   └── Notification generated
   │
   ▼
Doctor / Front Desk receive update
```

---

# 🚨 Example Doctor Cancellation Flow

```
Doctor
   │
   ▼
Select Availability
   │
   ▼
Cancel Entire Day
       OR
Cancel Time Range
   │
   ▼
Affected Slots
   │
   ▼
Slot Status = CANCELLED_BY_DOCTOR
   │
   ▼
Appointments remain historically traceable
   │
   ▼
Affected Patients Identified
   │
   ▼
Notification Sent
   │
   ▼
Patient receives:
   "Sorry, your appointment was cancelled.
    Please reschedule."
   │
   ▼
Booking Link
```

Cancelled slots are **not reopened**, preventing patients from booking a doctor who is unavailable.

---

# 🔐 Security

The system uses role-based authorization to protect hospital operations.

Authenticated staff requests contain a JWT.

```
Request
   │
   ▼
JWT
   │
   ▼
Authentication
   │
   ▼
User
   │
   ▼
Role
   │
   ├── ADMIN
   ├── FRONTDESK
   └── DOCTOR
   │
   ▼
Authorization
   │
   ▼
Endpoint
```

Patients use OTP verification for applicable public booking workflows.

Passwords are stored as hashes rather than plain text.

---

# 🐳 Docker Architecture

The application can be run using Docker Compose.

The main services are:

```
┌───────────────────────────────┐
│          Frontend              │
│       React + Vite             │
│          :5173                 │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│           Backend              │
│          FastAPI               │
│           :8000                │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│         PostgreSQL             │
│            :5432               │
└───────────────────────────────┘

┌───────────────────────────────┐
│           pgAdmin              │
│            :5050               │
└───────────────────────────────┘
```

---

# 🧱 Database Migration

Database schema changes are managed using **Alembic**.

Typical workflow:

```
Modify SQLAlchemy Model
        │
        ▼
Create Alembic Migration
        │
        ▼
Review Migration
        │
        ▼
Run Migration
        │
        ▼
PostgreSQL Schema Updated
```

This keeps database changes version-controlled and reproducible.

---

# 📁 High-Level Project Structure

```
project/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── admin/
│   │   │   ├── frontdesk/
│   │   │   └── doctor/
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── core/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── alembic.ini
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   │
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── admin/
│   │   │   ├── frontdesk/
│   │   │   └── doctor/
│   │   │
│   │   ├── components/
│   │   ├── routes/
│   │   ├── hooks/
│   │   └── main.tsx
│   │
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

# 🚀 Main System Workflow

The complete system can be summarized as:

```
                         CLINIC SYSTEM
                              │
              ┌───────────────┴────────────────┐
              │                                │
        PUBLIC PATIENT SIDE              STAFF SIDE
              │                                │
              │                     ┌──────────┼──────────┐
              │                     │          │          │
              │                   ADMIN    FRONT DESK   DOCTOR
              │                     │          │          │
              │                     ▼          ▼          ▼
              │                  Manage     Daily      Clinical
              │                  System    Operations   Workflow
              │
              ▼
        Find Doctor
              │
              ▼
       Select Availability
              │
              ▼
        Select Slot
              │
              ▼
        OTP Verification
              │
              ▼
        Book Appointment
              │
              ▼
        Doctor Consultation
              │
              ▼
         Prescription
              │
              ▼
         Follow-up
```

---

# 💡 What This Project Demonstrates

This project demonstrates practical implementation of:

* Role-Based Access Control (RBAC)
* REST API design
* Layered backend architecture
* Authentication and authorization
* JWT-based authentication
* OTP verification
* Database normalization and relational modeling
* SQLAlchemy ORM
* PostgreSQL
* Alembic migrations
* Pydantic validation
* React application architecture
* TanStack Query server-state management
* TanStack Router
* Real-time Server-Sent Events
* Appointment scheduling
* Doctor availability management
* Waiting-list management
* Prescription management
* Walk-in token management
* Docker containerization
* Role-specific dashboards
* Transactional database operations

---

# 🎯 Project Goal

The goal of this application is to provide a centralized digital platform for managing clinic operations while providing a simple appointment-booking experience for patients.

The system separates responsibilities between Admin, Front Desk, and Doctor roles while maintaining a common database and backend architecture.

It combines traditional CRUD-based hospital management with real-time communication through SSE and automated scheduling workflows.


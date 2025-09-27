# Uni Buddy - University Student Management System

A comprehensive web application built with Flask that helps university students manage their academic life by providing tools for event management, resource sharing, personal scheduling, and notifications.

## Table of Contents
1. [System Flow](#system-flow)
2. [Features & Functionalities](#features--functionalities)
3. [Non-Functional Requirements](#non-functional-requirements)
4. [Installation & Setup](#installation--setup)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Usage Guide](#usage-guide)

## System Flow

### High-Level Architecture
```
User Authentication → Dashboard → Module Access → Database Operations → UI Updates
```

### Detailed Application Flow

1. **User Registration/Login**
   - New users register with username, email, password, full name, and student ID
   - Existing users login with username/email and password
   - Session management handles user state across the application

2. **Dashboard Access**
   - After successful login, users are directed to the main dashboard
   - Dashboard displays personalized summary information:
     - Upcoming events (next 7 days)
     - Recent notifications
     - Today's schedule items

3. **Module Navigation**
   - Users can access different modules through navigation:
     - Events (Global - shared across all users)
     - Resources (Personal - user-specific)
     - Schedule (Personal - user-specific)
     - Notifications (User-specific)
     - Profile (User account information)

4. **Data Flow**
   - All user interactions are authenticated through session management
   - Database operations are performed with user context
   - Real-time updates through notifications system
   - File uploads handled securely with timestamp and user ID prefixes

## Features & Functionalities

### 1. User Authentication System
**Purpose**: Secure user access and session management

**Features**:
- User registration with validation
- Secure password hashing using Werkzeug
- Login/logout functionality
- Session management
- User profile management with statistics

**Key Components**:
- Password strength validation (minimum 6 characters)
- Duplicate username/email/student ID prevention
- Automatic login after registration
- Welcome notification for new users

### 2. Event Management Module (Global)
**Purpose**: University-wide event coordination and RSVP management

**Features**:
- **Event Creation**: Users can create events with title, description, date, time, and location
- **Event Viewing**: All users can see all events in chronological order
- **RSVP System**: Users can RSVP to events and cancel RSVPs
- **RSVP Tracking**: Real-time count of attendees for each event
- **Event Notifications**: Broadcast notifications when new events are created

**Access Level**: Global (all users can view and interact with events)

**Key Components**:
- Event creation form with validation
- RSVP/Cancel RSVP functionality
- Event creator information display
- Automatic notification system for new events

### 3. Resource Access Module (Personal)
**Purpose**: Personal document and file management for academic resources

**Features**:
- **File Upload**: Secure file upload with automatic naming convention
- **Categorization**: Organize resources by course and category
- **Search Functionality**: Search resources by title, description, or course
- **Category Filtering**: Filter resources by category
- **File Download**: Secure file download with access control
- **Resource Management**: View uploaded resources with metadata

**Access Level**: Personal (users can only access their own uploaded resources)

**Key Components**:
- Secure file upload with `secure_filename()`
- Timestamp and user ID prefixed filenames
- Search and filter capabilities
- Category-based organization
- Upload notifications

### 4. Personal Schedule Module (Personal)
**Purpose**: Individual academic and personal schedule management

**Features**:
- **Schedule Creation**: Add schedule items with title, description, date, time, and type
- **Date Filtering**: View schedule for specific dates
- **Schedule Types**: Categorize items (academic, personal, etc.)
- **Schedule Management**: View and delete schedule items
- **Today's Schedule**: Quick view of current day's schedule on dashboard

**Access Level**: Personal (users can only manage their own schedule)

**Key Components**:
- Date-based filtering
- Schedule type categorization
- Delete functionality with access control
- Dashboard integration for today's items

### 5. Notification System (User-Specific)
**Purpose**: Real-time communication and updates for users

**Features**:
- **Personal Notifications**: User-specific messages and updates
- **Broadcast Notifications**: System-wide announcements (visible to all users)
- **Notification Types**: Different types (info, success, warning, danger) with visual indicators
- **Read/Unread Status**: Mark notifications as read
- **Automatic Notifications**: System-generated notifications for various actions
- **Test Notifications**: Manual notification creation for testing

**Access Level**: User-specific (users see their personal notifications plus broadcast messages)

**Key Components**:
- Automatic notification generation for events, uploads, RSVPs
- Read status management
- Type-based visual indicators
- Broadcast capability for system-wide messages

### 6. Dashboard & Analytics
**Purpose**: Centralized overview of user activity and upcoming items

**Features**:
- **Activity Summary**: Quick stats on resources, schedule items, events
- **Upcoming Events**: Next 7 days preview
- **Today's Schedule**: Current day's schedule items
- **Recent Notifications**: Latest 3 notifications
- **User Statistics**: Count of created events, RSVPs, resources, schedule items

## Non-Functional Requirements

### Security & Authorization
- **Authentication Required**: All application features require user login
- **Session Management**: Secure session handling with automatic expiration detection
- **Data Isolation**: Personal modules (Resources, Schedule) enforce user-level access control
  - Users can only view and manage their own resources
  - Users can only access their personal schedule items
  - File downloads are restricted to resource owners
- **Password Security**: Passwords are hashed using Werkzeug's secure hashing
- **File Security**: Uploaded files are renamed with timestamps and user IDs to prevent conflicts and unauthorized access

### Data Privacy
- **User Context**: All database operations maintain user context
- **Access Control**: Database queries filter results by user ownership
- **Personal Information**: User profiles and personal data are protected
- **File Isolation**: Uploaded files are user-specific and access-controlled

### Performance & Scalability
- **Database Optimization**: Indexed queries and efficient database design
- **File Management**: Organized file storage with systematic naming
- **Session Efficiency**: Minimal session data storage
- **Responsive Design**: Bootstrap-based responsive UI

### Usability
- **Intuitive Navigation**: Clear module separation and navigation
- **Visual Feedback**: Flash messages for user actions
- **Real-time Updates**: Notification system for immediate feedback
- **Error Handling**: Graceful error handling with user-friendly messages

## Installation & Setup

### Prerequisites
- Python 3.7+
- Flask and dependencies
- SQLite3 (included with Python)

### Installation Steps

1. **Clone/Download the project files**

2. **Install required packages**:
```bash
pip install flask werkzeug
```

3. **Create required directories**:
```bash
mkdir uploads data templates
```

4. **Run the application**:
```bash
python app.py
```

5. **Access the application**:
   - Open browser to `http://localhost:5000`
   - Register a new account or login

### Project Structure
```
uni_buddy/
│
├── app.py                 # Main Flask application
├── data/
│   └── uni_buddy.db      # SQLite database (auto-created)
├── uploads/              # User uploaded files
├── templates/            # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── events.html
│   ├── resources.html
│   ├── schedule.html
│   ├── notifications.html
│   ├── profile.html
│   └── auth/
│       ├── login.html
│       └── register.html
└── README.md
```

## Database Schema

### Users Table
- `id` (PRIMARY KEY): Unique user identifier
- `username` (UNIQUE): User's login name
- `email` (UNIQUE): User's email address
- `password_hash`: Hashed password
- `full_name`: User's full name
- `student_id` (UNIQUE): University student ID
- `created_at`: Account creation timestamp

### Events Table (Global)
- `id` (PRIMARY KEY): Event identifier
- `title`: Event name
- `description`: Event details
- `date`: Event date
- `time`: Event time
- `location`: Event venue
- `created_by` (FOREIGN KEY): Creator's user ID
- `rsvp_count`: Number of RSVPs
- `created_at`: Event creation timestamp

### Event RSVPs Table
- `id` (PRIMARY KEY): RSVP identifier
- `event_id` (FOREIGN KEY): Associated event
- `user_id` (FOREIGN KEY): User who RSVP'd
- `rsvp_date`: RSVP timestamp
- UNIQUE constraint on (event_id, user_id)

### Resources Table (Personal)
- `id` (PRIMARY KEY): Resource identifier
- `title`: Resource name
- `description`: Resource description
- `filename`: Stored file name
- `course`: Associated course
- `category`: Resource category
- `user_id` (FOREIGN KEY): Owner's user ID
- `uploaded_at`: Upload timestamp

### Schedule Table (Personal)
- `id` (PRIMARY KEY): Schedule item identifier
- `title`: Schedule item name
- `description`: Item details
- `date`: Scheduled date
- `time`: Scheduled time
- `type`: Item type (academic, personal, etc.)
- `user_id` (FOREIGN KEY): Owner's user ID
- `created_at`: Creation timestamp

### Notifications Table (User-Specific)
- `id` (PRIMARY KEY): Notification identifier
- `title`: Notification title
- `message`: Notification content
- `type`: Notification type (info, success, warning, danger)
- `read`: Read status (0/1)
- `user_id` (FOREIGN KEY): Target user ID (NULL for broadcast)
- `created_at`: Creation timestamp

## API Endpoints

### Authentication Routes
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET /profile` - User profile and statistics

### Dashboard
- `GET /` - Main dashboard with summary information

### Event Management (Global)
- `GET /events` - View all events
- `GET/POST /events/create` - Create new event
- `GET /events/rsvp/<event_id>` - RSVP to event
- `GET /events/cancel_rsvp/<event_id>` - Cancel RSVP

### Resource Management (Personal)
- `GET /resources` - View user's resources (with search/filter)
- `GET/POST /resources/upload` - Upload new resource
- `GET /resources/download/<resource_id>` - Download resource file

### Schedule Management (Personal)
- `GET /schedule` - View user's schedule (with date filter)
- `GET/POST /schedule/add` - Add schedule item
- `GET /schedule/delete/<item_id>` - Delete schedule item

### Notification System
- `GET /notifications` - View user notifications
- `GET /notifications/mark_read/<notification_id>` - Mark as read
- `POST /notifications/create` - Create test notification
- `GET /api/notifications/unread` - Get unread count (JSON)

## Usage Guide

### Getting Started
1. **Register**: Create account with university details
2. **Dashboard**: View personalized summary after login
3. **Explore Modules**: Navigate through different features

### Managing Events
1. **View Events**: See all university events
2. **Create Events**: Add new events for others to see
3. **RSVP**: Confirm attendance to events
4. **Track Attendance**: View RSVP counts

### Managing Resources
1. **Upload Files**: Add study materials, notes, documents
2. **Organize**: Categorize by course and type
3. **Search**: Find specific resources quickly
4. **Download**: Access your uploaded files

### Managing Schedule
1. **Add Items**: Create schedule entries
2. **View by Date**: Filter schedule by specific dates
3. **Track Today**: See today's schedule on dashboard
4. **Manage**: Delete completed or outdated items

### Staying Updated
1. **Notifications**: Check for new messages and updates
2. **Dashboard**: Monitor upcoming events and today's schedule
3. **Profile**: Track your activity statistics

## Technical Notes

- **Database**: SQLite for simplicity and portability
- **Security**: Session-based authentication with password hashing
- **File Storage**: Local file system with secure naming
- **Frontend**: Bootstrap for responsive design
- **Error Handling**: Comprehensive error management with user feedback

## Future Enhancements

Potential improvements could include:
- Email notifications
- Calendar integration
- Group messaging
- Mobile app development
- Advanced search capabilities
- File sharing between users
- Event categories and filtering
- Reminder system for schedule items

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
import uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload and data directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('data/uni_buddy.db')

def init_db():
    """Initialize the database with tables"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  full_name TEXT NOT NULL,
                  student_id TEXT UNIQUE,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # Events table (global - all users can see)
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  date TEXT NOT NULL,
                  time TEXT NOT NULL,
                  location TEXT,
                  created_by INTEGER NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  rsvp_count INTEGER DEFAULT 0,
                  FOREIGN KEY (created_by) REFERENCES users (id))''')
    
    # RSVPs table
    c.execute('''CREATE TABLE IF NOT EXISTS event_rsvps
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_id INTEGER NOT NULL,
                  user_id INTEGER NOT NULL,
                  rsvp_date TEXT DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(event_id, user_id),
                  FOREIGN KEY (event_id) REFERENCES events (id),
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Resources table (personal - user specific)
    c.execute('''CREATE TABLE IF NOT EXISTS resources
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  filename TEXT NOT NULL,
                  course TEXT,
                  category TEXT,
                  user_id INTEGER NOT NULL,
                  uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Schedule table (personal - user specific)
    c.execute('''CREATE TABLE IF NOT EXISTS schedule
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  date TEXT NOT NULL,
                  time TEXT NOT NULL,
                  type TEXT DEFAULT 'academic',
                  user_id INTEGER NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Notifications table (user specific)
    c.execute('''CREATE TABLE IF NOT EXISTS notifications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  message TEXT NOT NULL,
                  type TEXT DEFAULT 'info',
                  read INTEGER DEFAULT 0,
                  user_id INTEGER,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        # Additional check - verify user still exists in database
        user = get_current_user()
        if user is None:
            session.clear()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user details"""
    if 'user_id' not in session:
        return None
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, username, email, full_name, student_id FROM users WHERE id = ?', 
              (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'student_id': user[4]
        }
    return None

# Initialize database on startup
init_db()

# AUTH ROUTES
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        student_id = request.form['student_id']
        
        # Basic validation
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if username or email already exists
        c.execute('SELECT id FROM users WHERE username = ? OR email = ? OR student_id = ?', 
                  (username, email, student_id))
        if c.fetchone():
            flash('Username, email, or student ID already exists.', 'error')
            conn.close()
            return render_template('auth/register.html')
        
        # Create user
        password_hash = generate_password_hash(password)
        c.execute('''INSERT INTO users (username, email, password_hash, full_name, student_id)
                     VALUES (?, ?, ?, ?, ?)''',
                  (username, email, password_hash, full_name, student_id))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Auto login after registration
        session['user_id'] = user_id
        session['username'] = username
        
        # Welcome notification
        create_notification("Welcome to Uni Buddy!", 
                          "Welcome to Uni Buddy! Start by exploring events and managing your schedule.", 
                          'success', user_id)
        
        flash('Registration successful! Welcome to Uni Buddy!', 'success')
        return redirect(url_for('home'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ? OR email = ?', 
                  (username, username))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    
    # Get user stats
    conn = get_db_connection()
    c = conn.cursor()
    
    # Count user's resources
    c.execute('SELECT COUNT(*) FROM resources WHERE user_id = ?', (user['id'],))
    resource_count = c.fetchone()[0]
    
    # Count user's schedule items
    c.execute('SELECT COUNT(*) FROM schedule WHERE user_id = ?', (user['id'],))
    schedule_count = c.fetchone()[0]
    
    # Count user's events created
    c.execute('SELECT COUNT(*) FROM events WHERE created_by = ?', (user['id'],))
    events_created = c.fetchone()[0]
    
    # Count user's event RSVPs
    c.execute('SELECT COUNT(*) FROM event_rsvps WHERE user_id = ?', (user['id'],))
    events_rsvpd = c.fetchone()[0]
    
    conn.close()
    
    stats = {
        'resources': resource_count,
        'schedule_items': schedule_count,
        'events_created': events_created,
        'events_rsvpd': events_rsvpd
    }
    
    return render_template('profile.html', user=user, stats=stats)

@app.route('/')
@login_required
def home():
    """Dashboard with summary information"""
    user = get_current_user()
    
    # Add this check - if user is None, clear session and redirect to login
    if user is None:
        session.clear()
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get upcoming events (next 7 days)
    today = datetime.now().strftime('%Y-%m-%d')
    week_later = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    c.execute('''SELECT e.title, e.date, e.time, u.username as creator 
                 FROM events e 
                 JOIN users u ON e.created_by = u.id
                 WHERE e.date BETWEEN ? AND ? 
                 ORDER BY e.date, e.time LIMIT 3''', (today, week_later))
    upcoming_events = c.fetchall()
    
    # Get user's recent notifications
    c.execute('''SELECT title, message, created_at FROM notifications 
                 WHERE user_id = ? OR user_id IS NULL
                 ORDER BY created_at DESC LIMIT 3''', (user['id'],))
    recent_notifications = c.fetchall()
    
    # Get user's today's schedule
    c.execute('''SELECT title, time FROM schedule 
                 WHERE date = ? AND user_id = ? ORDER BY time LIMIT 3''', 
              (today, user['id']))
    today_schedule = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         upcoming_events=upcoming_events,
                         recent_notifications=recent_notifications,
                         today_schedule=today_schedule,
                         user=user)
# EVENT MANAGEMENT MODULE (Global - all users can see)
@app.route('/events')
@login_required
def events():
    """Display all events"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT e.id, e.title, e.description, e.date, e.time, e.location, 
                        e.rsvp_count, u.username as creator, u.full_name as creator_name
                 FROM events e
                 JOIN users u ON e.created_by = u.id
                 ORDER BY e.date, e.time''')
    events_list = c.fetchall()
    
    # Check which events current user has RSVP'd to
    user_rsvps = []
    if events_list:
        event_ids = [str(event[0]) for event in events_list]
        c.execute(f'''SELECT event_id FROM event_rsvps 
                     WHERE user_id = ? AND event_id IN ({','.join(['?'] * len(event_ids))})''',
                  [session['user_id']] + event_ids)
        user_rsvps = [row[0] for row in c.fetchall()]
    
    conn.close()
    return render_template('events.html', events=events_list, user_rsvps=user_rsvps)

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO events (title, description, date, time, location, created_by)
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                  (title, description, date, time, location, session['user_id']))
        conn.commit()
        conn.close()
        
        # Create notification for all users about new event
        broadcast_notification(f"New Event: {title}", 
                             f"Event '{title}' scheduled for {date} at {time}. Created by {session['username']}.")
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events'))
    
    return render_template('create_event.html')

@app.route('/events/rsvp/<int:event_id>')
@login_required
def rsvp_event(event_id):
    """RSVP to an event"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if user already RSVP'd
    c.execute('SELECT id FROM event_rsvps WHERE event_id = ? AND user_id = ?',
              (event_id, session['user_id']))
    if c.fetchone():
        flash('You have already RSVP\'d to this event!', 'warning')
        conn.close()
        return redirect(url_for('events'))
    
    # Add RSVP
    c.execute('INSERT INTO event_rsvps (event_id, user_id) VALUES (?, ?)',
              (event_id, session['user_id']))
    
    # Update RSVP count
    c.execute('UPDATE events SET rsvp_count = rsvp_count + 1 WHERE id = ?', (event_id,))
    
    # Get event title for notification
    c.execute('SELECT title FROM events WHERE id = ?', (event_id,))
    event_title = c.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    # Create personal notification
    create_notification("RSVP Confirmed", 
                       f"You have successfully RSVP'd to '{event_title}'", 
                       'success', session['user_id'])
    
    flash('RSVP successful!', 'success')
    return redirect(url_for('events'))

@app.route('/events/cancel_rsvp/<int:event_id>')
@login_required
def cancel_rsvp(event_id):
    """Cancel RSVP to an event"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Remove RSVP
    c.execute('DELETE FROM event_rsvps WHERE event_id = ? AND user_id = ?',
              (event_id, session['user_id']))
    
    if c.rowcount > 0:
        # Update RSVP count
        c.execute('UPDATE events SET rsvp_count = rsvp_count - 1 WHERE id = ?', (event_id,))
        flash('RSVP cancelled successfully!', 'info')
    else:
        flash('You have not RSVP\'d to this event.', 'warning')
    
    conn.commit()
    conn.close()
    return redirect(url_for('events'))



# Add user context to all templates
@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

"""
GearTrade API Backend
FastAPI server with authentication, car management, matching, and real-time features
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import psycopg2
import psycopg2.extras
import hashlib
import secrets
from datetime import datetime, timedelta
import os
from pathlib import Path

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="GearTrade API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Security
security = HTTPBearer()

# Database connection
def get_db():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    return conn

# Password hashing
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_hex(32)

# Pydantic Models
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    location: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    price: int
    mileage: int
    condition: str
    listing_type: str
    description: str
    emoji: str = "🚗"

class CarUpdate(BaseModel):
    price: Optional[int] = None
    mileage: Optional[int] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class SwipeAction(BaseModel):
    car_id: int
    action: str  # 'like' or 'nope'

# Auth dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_token = %s 
        AND created_at + INTERVAL '7 days' > NOW()
    """, (token,))
    
    result = cursor.fetchone()
    db.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return result['user_id']

# Initialize database
def init_database():
    db = get_db()
    cursor = db.cursor()
    
    # Create all tables - execute separately for PostgreSQL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            location TEXT,
            bio TEXT,
            profile_photo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id SERIAL PRIMARY KEY,
            owner_id INTEGER NOT NULL REFERENCES users(id),
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price INTEGER NOT NULL,
            mileage INTEGER,
            condition TEXT,
            listing_type TEXT DEFAULT 'both',
            description TEXT,
            emoji TEXT DEFAULT '🚗',
            is_active BOOLEAN DEFAULT TRUE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_photos (
            id SERIAL PRIMARY KEY,
            car_id INTEGER NOT NULL REFERENCES cars(id) ON DELETE CASCADE,
            photo_path TEXT NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            car_id INTEGER NOT NULL REFERENCES cars(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, car_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dismissals (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            car_id INTEGER NOT NULL REFERENCES cars(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, car_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender_id INTEGER NOT NULL REFERENCES users(id),
            receiver_id INTEGER NOT NULL REFERENCES users(id),
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            user1_id INTEGER NOT NULL REFERENCES users(id),
            user2_id INTEGER NOT NULL REFERENCES users(id),
            car1_id INTEGER NOT NULL REFERENCES cars(id),
            car2_id INTEGER NOT NULL REFERENCES cars(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id)
        )
    ''')
    
    db.commit()
    db.close()

# API Endpoints

@app.on_event("startup")
async def startup():
    init_database()
    print("✅ Database initialized")

@app.get("/")
async def root():
    return {"message": "GearTrade API v1.0", "status": "running"}

# ============== AUTH ENDPOINTS ==============

@app.post("/api/auth/signup")
async def signup(user: UserSignup):
    db = get_db()
    cursor = db.cursor()
    
    try:
        password_hash = hash_password(user.password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, location, bio)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (user.username, user.email, password_hash, user.location, user.bio))
        
        user_id = cursor.fetchone()['id']
        
        # Create session
        session_token = generate_token()
        cursor.execute("""
            INSERT INTO sessions (user_id, session_token)
            VALUES (%s, %s)
        """, (user_id, session_token))
        
        db.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "username": user.username,
            "token": session_token
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        db.close()

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT id, username, password_hash 
        FROM users 
        WHERE username = %s
    """, (credentials.username,))
    
    user = cursor.fetchone()
    
    if not user or user['password_hash'] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create new session
    session_token = generate_token()
    cursor.execute("""
        INSERT INTO sessions (user_id, session_token)
        VALUES (%s, %s)
    """, (user['id'], session_token))
    
    db.commit()
    db.close()
    
    return {
        "success": True,
        "user_id": user['id'],
        "username": user['username'],
        "token": session_token
    }

@app.post("/api/auth/logout")
async def logout(user_id: int = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    db.commit()
    db.close()
    return {"success": True}

@app.get("/api/auth/me")
async def get_me(user_id: int = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT id, username, email, location, bio, profile_photo, created_at
        FROM users WHERE id = %s
    """, (user_id,))
    
    user = cursor.fetchone()
    db.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)

# ============== CAR ENDPOINTS ==============

@app.get("/api/cars/marketplace")
async def get_marketplace(user_id: int = Depends(get_current_user)):
    """Get cars for swiping - excludes own cars, liked, and dismissed"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            c.id, c.make, c.model, c.year, c.price, c.mileage,
            c.condition, c.listing_type, c.description, c.emoji, c.view_count,
            u.username as owner_username,
            u.location as owner_location,
            u.id as owner_id,
            (SELECT photo_path FROM car_photos WHERE car_id = c.id AND is_primary = 1 LIMIT 1) as primary_photo
        FROM cars c
        JOIN users u ON c.owner_id = u.id
        WHERE c.is_active = 1
        AND c.owner_id != %s
        AND c.id NOT IN (SELECT car_id FROM likes WHERE user_id = %s)
        AND c.id NOT IN (SELECT car_id FROM dismissals WHERE user_id = %s)
        ORDER BY c.created_at DESC
        LIMIT 20
    """, (user_id, user_id, user_id))
    
    cars = [dict(row) for row in cursor.fetchall()]

    # Attach all photos for each car
    for car in cars:
        cursor.execute(
            "SELECT photo_path FROM car_photos WHERE car_id = ? ORDER BY is_primary DESC, id ASC",
            (car['id'],)
        )
        car['photos'] = [r['photo_path'] for r in cursor.fetchall()]

    db.close()
    
    return {"cars": cars}

@app.get("/api/cars/my-garage")
async def get_my_garage(user_id: int = Depends(get_current_user)):
    """Get current user's cars"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            c.*,
            (SELECT photo_path FROM car_photos WHERE car_id = c.id AND is_primary = 1 LIMIT 1) as primary_photo,
            (SELECT COUNT(*) FROM likes WHERE car_id = c.id) as like_count
        FROM cars c
        WHERE c.owner_id = %s AND c.is_active = 1
        ORDER BY c.created_at DESC
    """, (user_id,))
    
    cars = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return {"cars": cars}

@app.post("/api/cars")
async def create_car(car: CarCreate, user_id: int = Depends(get_current_user)):
    """Add a new car to garage"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO cars (owner_id, make, model, year, price, mileage, condition, listing_type, description, emoji)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (user_id, car.make, car.model, car.year, car.price, car.mileage, 
          car.condition, car.listing_type, car.description, car.emoji))
    
    car_id = cursor.fetchone()['id']
    db.commit()
    db.close()
    
    return {"success": True, "car_id": car_id}

@app.put("/api/cars/{car_id}")
async def update_car(car_id: int, updates: CarUpdate, user_id: int = Depends(get_current_user)):
    """Update a car (only owner can update)"""
    db = get_db()
    cursor = db.cursor()
    
    # Verify ownership
    cursor.execute("SELECT owner_id FROM cars WHERE id = ?", (car_id,))
    car = cursor.fetchone()
    
    if not car or car['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Build update query
    update_fields = []
    values = []
    
    for field, value in updates.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = ?")
        values.append(value)
    
    if update_fields:
        values.append(car_id)
        cursor.execute(f"""
            UPDATE cars SET {', '.join(update_fields)}
            WHERE id = %s
        """, values)
        db.commit()
    
    db.close()
    return {"success": True}

@app.delete("/api/cars/{car_id}")
async def delete_car(car_id: int, user_id: int = Depends(get_current_user)):
    """Soft delete a car"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("UPDATE cars SET is_active = FALSE WHERE id = %s AND owner_id = %s", (car_id, user_id))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=403, detail="Not authorized or car not found")
    
    db.commit()
    db.close()
    
    return {"success": True}

@app.post("/api/cars/{car_id}/view")
async def increment_view(car_id: int, user_id: int = Depends(get_current_user)):
    """Increment view count"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE cars SET view_count = view_count + 1 WHERE id = ?", (car_id,))
    db.commit()
    db.close()
    return {"success": True}

# ============== SWIPE ENDPOINTS ==============

@app.post("/api/swipe")
async def swipe(swipe: SwipeAction, user_id: int = Depends(get_current_user)):
    """Handle swipe action (like or nope)"""
    db = get_db()
    cursor = db.cursor()
    
    if swipe.action == 'like':
        # Add like
        cursor.execute("""
            INSERT INTO likes (user_id, car_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (user_id, swipe.car_id))
        
        # Check for match
        cursor.execute("""
            SELECT c.owner_id, c.id as their_car_id
            FROM cars c
            WHERE c.id = %s
        """, (swipe.car_id,))
        
        their_car = cursor.fetchone()
        
        if their_car:
            # Check if they liked any of our cars
            cursor.execute("""
                SELECT l.car_id as my_car_id
                FROM likes l
                JOIN cars c ON l.car_id = c.id
                WHERE l.user_id = %s AND c.owner_id = %s
                LIMIT 1
            """, (their_car['owner_id'], user_id))
            
            my_liked_car = cursor.fetchone()
            
            if my_liked_car:
                # It's a match!
                try:
                    cursor.execute("""
                        INSERT INTO matches (user1_id, user2_id, car1_id, car2_id)
                        VALUES (%s, %s, %s, %s)
                    """, (min(user_id, their_car['owner_id']), 
                          max(user_id, their_car['owner_id']),
                          my_liked_car['my_car_id'], 
                          their_car['their_car_id']))
                except Exception:
                    pass  # Match already exists
                
                db.commit()
                
                # Get match details
                cursor.execute("SELECT username FROM users WHERE id = ?", (their_car['owner_id'],))
                other_user = cursor.fetchone()
                
                db.close()
                
                return {
                    "success": True,
                    "match": True,
                    "matched_user": other_user['username'],
                    "matched_user_id": their_car['owner_id']
                }
    
    elif swipe.action == 'nope':
        # Add dismissal
        cursor.execute("""
            INSERT INTO dismissals (user_id, car_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (user_id, swipe.car_id))
    
    db.commit()
    db.close()
    
    return {"success": True, "match": False}

# ============== MATCH ENDPOINTS ==============

@app.get("/api/matches")
async def get_matches(user_id: int = Depends(get_current_user)):
    """Get all matches for current user"""
    db = get_db()
    cursor = db.cursor()

    # Subquery resolves the CASE aliases first so the correlated
    # unread subquery can reference matched_user_id without error.
    cursor.execute("""
        SELECT
            base.matched_user_id,
            base.their_car_id,
            base.my_car_id,
            u.username  AS matched_username,
            u.location  AS matched_location,
            c.make || ' ' || c.model AS their_car,
            c.emoji     AS their_emoji,
            (SELECT COUNT(*) FROM messages
             WHERE sender_id   = base.matched_user_id
               AND receiver_id = %s
               AND is_read     = 0) AS unread_count,
            base.matched_at
        FROM (
            SELECT
                CASE WHEN m.user1_id = %s THEN m.user2_id ELSE m.user1_id END AS matched_user_id,
                CASE WHEN m.user1_id = %s THEN m.car2_id  ELSE m.car1_id  END AS their_car_id,
                CASE WHEN m.user1_id = %s THEN m.car1_id  ELSE m.car2_id  END AS my_car_id,
                m.created_at AS matched_at
            FROM matches m
            WHERE %s IN (m.user1_id, m.user2_id)
        ) AS base
        JOIN users u ON u.id = base.matched_user_id
        JOIN cars  c ON c.id = base.their_car_id
        ORDER BY base.matched_at DESC
    """, (user_id, user_id, user_id, user_id, user_id))

    matches = [dict(row) for row in cursor.fetchall()]
    db.close()

    return {"matches": matches}

# ============== MESSAGE ENDPOINTS ==============

@app.get("/api/messages/unread/count")
async def get_unread_count(user_id: int = Depends(get_current_user)):
    """Get total unread message count"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM messages
        WHERE receiver_id = %s AND is_read = 0
    """, (user_id,))
    
    result = cursor.fetchone()
    db.close()
    
    return {"unread_count": result['count']}

@app.get("/api/messages/{other_user_id}")
async def get_messages(other_user_id: int, user_id: int = Depends(get_current_user)):
    """Get message history with another user"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            id, sender_id, receiver_id, content, is_read, created_at
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY created_at ASC
    """, (user_id, other_user_id, other_user_id, user_id))
    
    messages = [dict(row) for row in cursor.fetchall()]
    
    # Mark messages as read
    cursor.execute("""
        UPDATE messages 
        SET is_read = 1 
        WHERE sender_id = %s AND receiver_id = %s AND is_read = 0
    """, (other_user_id, user_id))
    
    db.commit()
    db.close()
    
    return {"messages": messages}

@app.post("/api/messages")
async def send_message(message: MessageCreate, user_id: int = Depends(get_current_user)):
    """Send a message to another user"""
    db = get_db()
    cursor = db.cursor()
    
    # Verify they're matched
    cursor.execute("""
        SELECT id FROM matches
        WHERE (user1_id = %s AND user2_id = %s)
           OR (user1_id = %s AND user2_id = %s)
    """, (min(user_id, message.receiver_id), max(user_id, message.receiver_id),
          min(user_id, message.receiver_id), max(user_id, message.receiver_id)))
    
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="Not matched with this user")
    
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (%s, %s, %s) RETURNING id
    """, (user_id, message.receiver_id, message.content))
    
    message_id = cursor.fetchone()['id']
    db.commit()
    db.close()
    
    return {"success": True, "message_id": message_id}

# ============== STATS ENDPOINTS ==============

@app.get("/api/stats")
async def get_stats(user_id: int = Depends(get_current_user)):
    """Get user statistics"""
    db = get_db()
    cursor = db.cursor()
    
    # Total matches
    cursor.execute("""
        SELECT COUNT(*) as count FROM matches
        WHERE %s IN (user1_id, user2_id)
    """, (user_id,))
    matches_count = cursor.fetchone()['count']
    
    # Total likes given
    cursor.execute("SELECT COUNT(*) as count FROM likes WHERE user_id = ?", (user_id,))
    likes_given = cursor.fetchone()['count']
    
    # Total likes received (on my cars)
    cursor.execute("""
        SELECT COUNT(*) as count FROM likes l
        JOIN cars c ON l.car_id = c.id
        WHERE c.owner_id = %s
    """, (user_id,))
    likes_received = cursor.fetchone()['count']
    
    # Total cars
    cursor.execute("SELECT COUNT(*) as count FROM cars WHERE owner_id = ? AND is_active = 1", (user_id,))
    cars_count = cursor.fetchone()['count']
    
    # Total views on my cars
    cursor.execute("SELECT SUM(view_count) as total FROM cars WHERE owner_id = ?", (user_id,))
    total_views = cursor.fetchone()['total'] or 0
    
    db.close()
    
    return {
        "matches": matches_count,
        "likes_given": likes_given,
        "likes_received": likes_received,
        "cars": cars_count,
        "total_views": total_views
    }

# ============== FILE UPLOAD ==============

@app.post("/api/upload/car-photo/{car_id}")
async def upload_car_photo(
    car_id: int, 
    file: UploadFile = File(...),
    is_primary: bool = False,
    user_id: int = Depends(get_current_user)
):
    """Upload a car photo"""
    db = get_db()
    cursor = db.cursor()
    
    # Verify ownership
    cursor.execute("SELECT owner_id FROM cars WHERE id = ?", (car_id,))
    car = cursor.fetchone()
    
    if not car or car['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Save file
    file_ext = file.filename.split('.')[-1]
    filename = f"car_{car_id}_{secrets.token_hex(8)}.{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # If primary, unset other primary photos
    if is_primary:
        cursor.execute("UPDATE car_photos SET is_primary = 0 WHERE car_id = ?", (car_id,))
    
    # Add to database
    cursor.execute("""
        INSERT INTO car_photos (car_id, photo_path, is_primary)
        VALUES (%s, %s, %s)
    """, (car_id, str(file_path), is_primary))
    
    db.commit()
    db.close()
    
    return {"success": True, "photo_path": f"/uploads/{filename}"}

@app.post("/api/upload/profile-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user)
):
    """Upload profile photo"""
    db = get_db()
    cursor = db.cursor()
    
    # Save file
    file_ext = file.filename.split('.')[-1]
    filename = f"profile_{user_id}_{secrets.token_hex(8)}.{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Update user
    cursor.execute("""
        UPDATE users SET profile_photo = %s
        WHERE id = %s
    """, (str(file_path), user_id))
    
    db.commit()
    db.close()
    
    return {"success": True, "photo_path": f"/uploads/{filename}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

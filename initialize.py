#!/usr/bin/env python3
"""
GearTrade Fresh Start
Creates a brand new database with all the enhanced features
"""

import sqlite3
import os

def fresh_start():
    """Create a completely fresh database"""
    
    print("🚗 GearTrade Fresh Start")
    print("=" * 50)
    print()
    
    # Remove old database if it exists
    if os.path.exists('geartrade.db'):
        print("🗑️  Removing old database...")
        os.remove('geartrade.db')
        print("✅ Old database removed")
    
    print("🔨 Creating new database...")
    
    conn = sqlite3.connect('geartrade.db')
    c = conn.cursor()
    
    # 1. Users Table
    print("  Creating users table...")
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY, 
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        location TEXT,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 2. Cars Table (complete schema)
    print("  Creating cars table...")
    c.execute('''CREATE TABLE cars (
        id INTEGER PRIMARY KEY, 
        owner_id INTEGER NOT NULL,
        model TEXT NOT NULL,
        make TEXT,
        emoji TEXT DEFAULT '🚗',
        year INTEGER DEFAULT 2020,
        description TEXT DEFAULT '',
        mileage INTEGER,
        price INTEGER,
        listing_type TEXT DEFAULT 'both',
        condition TEXT DEFAULT 'Good',
        is_active BOOLEAN DEFAULT 1,
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id)
    )''')
    
    # 3. Likes Table
    print("  Creating likes table...")
    c.execute('''CREATE TABLE likes (
        id INTEGER PRIMARY KEY, 
        sender_id INTEGER NOT NULL,
        target_car_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(sender_id, target_car_id),
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (target_car_id) REFERENCES cars(id)
    )''')
    
    # 4. Dismissals Table
    print("  Creating dismissals table...")
    c.execute('''CREATE TABLE dismissals (
        id INTEGER PRIMARY KEY, 
        user_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, car_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (car_id) REFERENCES cars(id)
    )''')
    
    # 5. Messages Table
    print("  Creating messages table...")
    c.execute('''CREATE TABLE messages (
        id INTEGER PRIMARY KEY,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )''')
    
    # 6. Favorites Table
    print("  Creating favorites table...")
    c.execute('''CREATE TABLE favorites (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, car_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (car_id) REFERENCES cars(id)
    )''')
    
    print()
    print("📝 Adding sample data...")
    
    # Add Users
    c.execute("""INSERT INTO users (id, username, location, bio) VALUES 
        (1, 'Me', 'Los Angeles, CA', 'Car enthusiast and collector'),
        (2, 'Bob', 'Miami, FL', 'Love German engineering'),
        (3, 'Alice', 'Austin, TX', 'EV fanatic and early adopter'),
        (4, 'Carlos', 'San Diego, CA', 'JDM collector'),
        (5, 'Diana', 'Seattle, WA', 'Classic car restoration expert')
    """)
    
    # Add Cars
    c.execute("""INSERT INTO cars 
        (owner_id, model, make, emoji, year, description, mileage, price, condition, listing_type) 
        VALUES 
        (1, '911 Turbo', 'Porsche', '🏎️', 2022, 
         'Stunning Guards Red with full carbon package. Never tracked, garage kept. PDK transmission, Sport Chrono, and all the options.', 
         8500, 185000, 'Excellent', 'both'),
        
        (2, 'M3 Competition', 'BMW', '🚙', 2023, 
         'Isle of Man Green, 6-speed manual, carbon bucket seats. One owner, perfect condition. All maintenance records.', 
         12000, 82000, 'Excellent', 'both'),
        
        (2, 'F100', 'Ford', '🛻', 1967, 
         'Restored classic pickup. Numbers matching 352 V8. Show quality paint and chrome. Runs and drives excellent.', 
         45000, 35000, 'Good', 'sale'),
        
        (3, 'Model S Plaid', 'Tesla', '⚡', 2024, 
         'Ludicrous speed! Full Self-Driving included. Under warranty. White interior, 21" wheels. Only 5k miles.', 
         5000, 89000, 'Excellent', 'both'),
        
        (4, 'Skyline GT-R', 'Nissan', '🏎️', 1999, 
         'R34 GT-R V-Spec. Imported and federalized. Bayside Blue. Stock and pristine. Dream car for JDM enthusiasts.', 
         32000, 175000, 'Excellent', 'trade'),
        
        (4, 'Supra', 'Toyota', '🚗', 1998, 
         'MK4 Supra Turbo 6-speed. All original, no modifications. Renaissance Red. Collector quality.', 
         28000, 125000, 'Excellent', 'both'),
        
        (5, 'Mustang', 'Ford', '🏎️', 1969, 
         'Mach 1 428 Cobra Jet. Fully documented restoration. Numbers matching. Show winner. Investment grade.', 
         12000, 145000, 'Excellent', 'sale'),
        
        (5, 'Corvette', 'Chevrolet', '🏎️', 1963, 
         'Split-window Coupe. Frame-off restoration. 327/340hp, 4-speed. Tuxedo Black. One of the most iconic Corvettes.', 
         8000, 165000, 'Excellent', 'both')
    """)
    
    # Add some sample likes (Bob likes your Porsche)
    c.execute("INSERT INTO likes (sender_id, target_car_id) VALUES (2, 1)")
    # Alice likes your Porsche too
    c.execute("INSERT INTO likes (sender_id, target_car_id) VALUES (3, 1)")
    
    conn.commit()
    
    # Verify
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM cars")
    car_count = c.fetchone()[0]
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    print()
    print("✅ Database created successfully!")
    print()
    print("📊 Summary:")
    print(f"   • {len(tables)} tables created")
    print(f"   • {user_count} users added")
    print(f"   • {car_count} cars added")
    print()
    print("🎯 Next step:")
    print("   streamlit run app_enhanced.py")
    print()
    print("💡 Login as 'Me' (user ID 1) to test all features")
    print("   You already have 2 likes from Bob and Alice!")
    print()

if __name__ == "__main__":
    fresh_start()

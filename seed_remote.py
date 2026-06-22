"""
One-time seed script to populate Railway PostgreSQL
"""
import hashlib
import psycopg2
import psycopg2.extras

DATABASE_URL = "postgresql://postgres:GkNWpQrlmEZGdlyZmOtMCqioZwCvcCuO@trolley.proxy.rlwy.net:24570/railway"

def h(p): return hashlib.sha256(p.encode()).hexdigest()

USERS = [
    ("alexracing",    "alex@gt.com",    "Miami, FL",       "Porsche obsessive. PDK only."),
    ("jordan_drives", "jordan@gt.com",  "Los Angeles, CA", "Italian cars or nothing."),
    ("jdm_carlos",    "carlos@gt.com",  "San Diego, CA",   "JDM collector since 2005."),
    ("riley_bimmer",  "riley@gt.com",   "Chicago, IL",     "Manual transmissions forever."),
    ("classic_diana", "diana@gt.com",   "Seattle, WA",     "Classic restoration expert."),
    ("alice_ev",      "alice@gt.com",   "Austin, TX",      "EV early adopter."),
    ("vinnie_v8",     "vinnie@gt.com",  "Dallas, TX",      "American muscle only."),
    ("subaroo_pete",  "pete@gt.com",    "Denver, CO",      "Flat-four fanatic."),
]

CARS = [
  { "owner":"alexracing",   "make":"Porsche",     "model":"911 Turbo S",          "year":2023, "price":230000, "mileage":5200,  "condition":"Excellent", "type":"both",  "emoji":"🏎️",
    "desc":"Guards Red, full carbon package, PDK, Sport Chrono, ceramic brakes. Zero track time — always garage kept.",
    "photos":["https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=800&q=80","https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&q=80","https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80"]},
  { "owner":"jordan_drives", "make":"Ferrari",    "model":"Roma",                  "year":2022, "price":225000, "mileage":3100,  "condition":"Excellent", "type":"trade", "emoji":"🏎️",
    "desc":"Grigio Silverstone over Charcoal leather. Adult driven, never tracked. All maintenance records.",
    "photos":["https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=800&q=80","https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&q=80","https://images.unsplash.com/photo-1555626906-fcf10d6851b4?w=800&q=80"]},
  { "owner":"jdm_carlos",   "make":"Nissan",      "model":"Skyline GT-R R34",      "year":1999, "price":175000, "mileage":31000, "condition":"Excellent", "type":"trade", "emoji":"🏎️",
    "desc":"Bayside Blue V-Spec. Federalized and titled. Completely stock, numbers matching. These are only going up.",
    "photos":["https://images.unsplash.com/photo-1632245889029-e406faaa34cd?w=800&q=80","https://images.unsplash.com/photo-1547744152-14d985cb937f?w=800&q=80","https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"]},
  { "owner":"riley_bimmer", "make":"BMW",         "model":"M4 Competition",        "year":2024, "price":88000,  "mileage":800,   "condition":"Excellent", "type":"both",  "emoji":"🚗",
    "desc":"Isle of Man Green, 6-speed manual, carbon bucket seats. 800 miles. The spec every enthusiast wants.",
    "photos":["https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80","https://images.unsplash.com/photo-1619405399517-d7fce0f13302?w=800&q=80","https://images.unsplash.com/photo-1617531653332-bd46c16f4d68?w=800&q=80"]},
  { "owner":"classic_diana","make":"Ford",        "model":"Mustang Mach 1",        "year":1969, "price":145000, "mileage":12000, "condition":"Excellent", "type":"sale",  "emoji":"🏎️",
    "desc":"428 Cobra Jet, Candy Apple Red. Frame-off restoration to factory spec. Numbers matching. Trophy winner.",
    "photos":["https://images.unsplash.com/photo-1567808291548-fc3ee04dbcf0?w=800&q=80","https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=800&q=80","https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=800&q=80"]},
  { "owner":"alice_ev",     "make":"Tesla",       "model":"Model S Plaid",         "year":2024, "price":89000,  "mileage":4900,  "condition":"Excellent", "type":"both",  "emoji":"⚡",
    "desc":"Midnight Silver, white interior, 21\" Arachnid wheels. FSD included. Under factory warranty.",
    "photos":["https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&q=80","https://images.unsplash.com/photo-1571987502227-9231b837d92a?w=800&q=80","https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800&q=80"]},
  { "owner":"vinnie_v8",    "make":"Dodge",       "model":"Challenger SRT Hellcat","year":2023, "price":72000,  "mileage":6800,  "condition":"Excellent", "type":"both",  "emoji":"🐍",
    "desc":"Hellraisin Purple, 6-speed manual, 717hp supercharged HEMI. Street only, never drag raced.",
    "photos":["https://images.unsplash.com/photo-1612825173281-9a193378527e?w=800&q=80","https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&q=80"]},
  { "owner":"vinnie_v8",    "make":"Ford",        "model":"GT Heritage Edition",   "year":2019, "price":595000, "mileage":1200,  "condition":"Excellent", "type":"trade", "emoji":"🏎️",
    "desc":"Liquid Blue, silver stripes. One of 1,350 built. Carbon everywhere. Stored since delivery.",
    "photos":["https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&q=80","https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&q=80"]},
  { "owner":"subaroo_pete", "make":"Subaru",      "model":"WRX STI Type RA",       "year":2018, "price":48000,  "mileage":22000, "condition":"Good",      "type":"both",  "emoji":"🚗",
    "desc":"Crystal White Pearl, stock. Only 500 made. The most capable all-weather performance car at this price.",
    "photos":["https://images.unsplash.com/photo-1616788494707-ec28f08d05a1?w=800&q=80","https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80"]},
  { "owner":"subaroo_pete", "make":"Lamborghini", "model":"Huracán EVO",           "year":2022, "price":265000, "mileage":4500,  "condition":"Excellent", "type":"both",  "emoji":"🏎️",
    "desc":"Giallo Orion, black Alcantara. LDVI torque vectoring, ANIMA selector, titanium exhaust.",
    "photos":["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80","https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=800&q=80"]},
  { "owner":"jdm_carlos",   "make":"Toyota",      "model":"Supra MK4",             "year":1998, "price":120000, "mileage":28000, "condition":"Excellent", "type":"both",  "emoji":"🏎️",
    "desc":"Renaissance Red, single turbo, 6-speed manual. All original. Holy grail of JDM.",
    "photos":["https://images.unsplash.com/photo-1632245889029-e406faaa34cd?w=800&q=80","https://images.unsplash.com/photo-1547744152-14d985cb937f?w=800&q=80"]},
  { "owner":"riley_bimmer", "make":"McLaren",     "model":"720S",                  "year":2021, "price":280000, "mileage":7800,  "condition":"Excellent", "type":"trade", "emoji":"🏎️",
    "desc":"Papaya Spark, electrochromic roof, nose lift, B&W audio. Serviced at McLaren Beverly Hills.",
    "photos":["https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80","https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&q=80"]},
]

def seed():
    print("🌱 Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    c = conn.cursor()
    
    # Check if already seeded
    c.execute("SELECT COUNT(*) as count FROM cars")
    if c.fetchone()['count'] > 0:
        print("⚠️  Database already has cars — skipping to avoid duplicates.")
        conn.close()
        return

    print("📝 Seeding users...")
    user_ids = {}
    for username, email, location, bio in USERS:
        try:
            c.execute("INSERT INTO users (username,email,password_hash,location,bio) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                      (username, email, h("password123"), location, bio))
            user_ids[username] = c.fetchone()['id']
            print(f"  ✅ {username}")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠️  {username} (may already exist)")
            c.execute("SELECT id FROM users WHERE username=%s", (username,))
            row = c.fetchone()
            if row: user_ids[username] = row['id']

    conn.commit()
    print(f"\n🚗 Seeding cars...")
    
    for car in CARS:
        oid = user_ids.get(car["owner"])
        if not oid: 
            print(f"  ⚠️  Skipping {car['model']} — owner not found")
            continue
        try:
            c.execute("""INSERT INTO cars (owner_id,make,model,year,price,mileage,condition,listing_type,description,emoji)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                      (oid, car["make"], car["model"], car["year"], car["price"],
                       car["mileage"], car["condition"], car["type"], car["desc"], car["emoji"]))
            cid = c.fetchone()['id']
            for i, url in enumerate(car["photos"]):
                c.execute("INSERT INTO car_photos (car_id,photo_path,is_primary) VALUES (%s,%s,%s)",
                          (cid, url, i == 0))
            print(f"  ✅ {car['year']} {car['make']} {car['model']}")
        except Exception as e:
            conn.rollback()
            print(f"  ❌ {car['model']}: {e}")
            continue

    conn.commit()
    c.execute("SELECT COUNT(*) as count FROM cars"); nc = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM car_photos"); np = c.fetchone()['count']
    conn.close()
    
    print(f"\n🎉 Done! {nc} cars · {np} photos seeded")
    print(f"All accounts use password: password123")

if __name__ == "__main__":
    seed()

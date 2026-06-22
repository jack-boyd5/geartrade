#!/usr/bin/env python3
"""
Add more test cars with listing_type for testing intent feature
"""

import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Usage: DATABASE_URL='your-db-url' python add_more_cars.py")
    exit(1)

# More test cars with different listing types
MORE_CARS = [
    {
        'make': 'Porsche',
        'model': 'Cayman GT4',
        'year': 2020,
        'price': 98000,
        'mileage': 15000,
        'condition': 'Excellent',
        'listing_type': 'both',
        'description': 'Manual transmission, track-prepped but street driven. Open to trades for other Porsches or exotic cars.',
        'emoji': '🏎️'
    },
    {
        'make': 'Audi',
        'model': 'RS5 Sportback',
        'year': 2021,
        'price': 72000,
        'mileage': 22000,
        'condition': 'Excellent',
        'listing_type': 'trade',
        'description': 'Looking to trade down to something lighter and more fun. Manual cars preferred.',
        'emoji': '🚗'
    },
    {
        'make': 'Ford',
        'model': 'Mustang GT',
        'year': 2019,
        'price': 38000,
        'mileage': 28000,
        'condition': 'Good',
        'listing_type': 'sale',
        'description': 'Coyote V8, performance pack. Clean title, adult owned. Cash only.',
        'emoji': '🏎️'
    },
    {
        'make': 'Chevrolet',
        'model': 'Corvette C8',
        'year': 2022,
        'price': 95000,
        'mileage': 4500,
        'condition': 'Excellent',
        'listing_type': 'both',
        'description': 'Rapid Blue, magnetic ride, Z51 package. Will trade for C7 ZR1 or sell.',
        'emoji': '🏎️'
    },
    {
        'make': 'Tesla',
        'model': 'Model 3 Performance',
        'year': 2021,
        'price': 52000,
        'mileage': 18000,
        'condition': 'Excellent',
        'listing_type': 'trade',
        'description': 'Want to trade for a gas sports car. Missing the manual experience.',
        'emoji': '⚡'
    },
    {
        'make': 'Volkswagen',
        'model': 'Golf R',
        'year': 2023,
        'price': 46000,
        'mileage': 6000,
        'condition': 'Excellent',
        'listing_type': 'both',
        'description': 'Lapiz Blue, DSG, essentially new. Trade or sale considered.',
        'emoji': '🚗'
    },
    {
        'make': 'Nissan',
        'model': 'Z (400Z)',
        'year': 2023,
        'price': 48000,
        'mileage': 2800,
        'condition': 'Excellent',
        'listing_type': 'sale',
        'description': 'Seiran Blue, manual transmission. Brand new condition. Not interested in trades.',
        'emoji': '🏎️'
    },
    {
        'make': 'Dodge',
        'model': 'Challenger Hellcat',
        'year': 2020,
        'price': 62000,
        'mileage': 12000,
        'condition': 'Excellent',
        'listing_type': 'both',
        'description': 'Supercharged 707hp beast. Will trade for muscle cars or sell outright.',
        'emoji': '🏎️'
    },
    {
        'make': 'McLaren',
        'model': '570S',
        'year': 2018,
        'price': 145000,
        'mileage': 8500,
        'condition': 'Excellent',
        'listing_type': 'trade',
        'description': 'Volcano Yellow, carbon ceramic brakes. Looking to trade for newer 720S or Huracan.',
        'emoji': '🏎️'
    },
    {
        'make': 'Lexus',
        'model': 'LC500',
        'year': 2022,
        'price': 88000,
        'mileage': 9000,
        'condition': 'Excellent',
        'listing_type': 'both',
        'description': 'Structural Blue, Mark Levinson audio. Trades or cash considered.',
        'emoji': '🚗'
    },
    {
        'make': 'Mercedes-AMG',
        'model': 'GT 63 S',
        'year': 2021,
        'price': 112000,
        'mileage': 14000,
        'condition': 'Excellent',
        'listing_type': 'sale',
        'description': '4-door coupe, ridiculously fast. Selling due to downsizing. No trades.',
        'emoji': '🏎️'
    },
    {
        'make': 'Acura',
        'model': 'Integra Type S',
        'year': 2024,
        'price': 52000,
        'mileage': 1200,
        'condition': 'Excellent',
        'listing_type': 'trade',
        'description': 'Liquid Carbon Pearl, manual. Only trading for another manual sports car.',
        'emoji': '🚗'
    }
]

def add_more_cars():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get a test user to own these cars
    cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
    result = cursor.fetchone()
    
    if not result:
        print("❌ No users found in database. Create a user first.")
        conn.close()
        return
    
    owner_id = result[0]
    
    try:
        added_count = 0
        both_count = 0
        trade_count = 0
        sale_count = 0
        
        for car in MORE_CARS:
            cursor.execute("""
                INSERT INTO cars 
                (owner_id, make, model, year, price, mileage, condition, listing_type, description, emoji, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id
            """, (
                owner_id,
                car['make'],
                car['model'],
                car['year'],
                car['price'],
                car['mileage'],
                car['condition'],
                car['listing_type'],
                car['description'],
                car['emoji']
            ))
            
            car_id = cursor.fetchone()[0]
            added_count += 1
            
            if car['listing_type'] == 'both':
                both_count += 1
            elif car['listing_type'] == 'trade':
                trade_count += 1
            elif car['listing_type'] == 'sale':
                sale_count += 1
            
            print(f"✅ Added: {car['year']} {car['make']} {car['model']} ({car['listing_type']})")
        
        conn.commit()
        print(f"\n🎉 Successfully added {added_count} more test cars!")
        print(f"\nListing type breakdown:")
        print(f"  - {both_count} cars: Trade or Sell (both)")
        print(f"  - {trade_count} cars: Trade Only (trade)")
        print(f"  - {sale_count} cars: Sale Only (sale)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding cars: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_more_cars()

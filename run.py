import os
from app import create_app
from app.extensions import db
from app.seed_data import seed_database

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
        
    port = int(os.environ.get('PORT', 5000))
    print(f"\n========================================================")
    print(f"🍱 FoodBridge Smart Food Rescue Platform is LIVE!")
    print(f"🔗 Local Web Server: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)

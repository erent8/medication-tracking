from app import app, init_db

if __name__ == '__main__':
    # Veritabanını başlat
    with app.app_context():
        init_db()
    
    # Uygulamayı başlat
    app.run(debug=True) 
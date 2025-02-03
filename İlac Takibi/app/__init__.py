import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

# Flask uygulamasını oluştur
app = Flask(__name__)

# Uygulama yapılandırması
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email yapılandırması
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Yükleme klasörü yapılandırması
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Uzantılar
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)
babel = Babel(app)

# Login yapılandırması
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bu sayfayı görüntülemek için lütfen giriş yapın.'
login_manager.login_message_category = 'info'

# Blueprint'leri kaydet
from app.controllers.auth import auth as auth_blueprint
from app.controllers.main import main as main_blueprint
from app.controllers.medicine import medicine as medicine_blueprint
from app.controllers.health import health as health_blueprint
from app.controllers.api import api as api_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(medicine_blueprint)
app.register_blueprint(health_blueprint)
app.register_blueprint(api_blueprint, url_prefix='/api')

# Hata sayfaları
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Veritabanı başlatma
def init_db():
    with app.app_context():
        db.create_all()

# Kullanıcı yükleyici
from app.models.user import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Dil seçimi
@babel.localeselector
def get_locale():
    return os.getenv('DEFAULT_LANGUAGE', 'tr')

# Hata sayfaları
from app.controllers.errors import page_not_found, internal_server_error

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error) 
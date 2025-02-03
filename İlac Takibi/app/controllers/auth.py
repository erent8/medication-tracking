from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db
import jwt
import datetime
from functools import wraps

auth = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return {'message': 'Token bulunamadı!'}, 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.get(data['user_id'])
        except:
            return {'message': 'Token geçersiz!'}, 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth.route('/kayit', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Bu email adresi zaten kayıtlı!', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            email=email,
            password=generate_password_hash(password, method='sha256'),
            ad=ad,
            soyad=soyad
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/giris', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Email veya şifre hatalı!', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))
    
    return render_template('auth/login.html')

@auth.route('/cikis')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/profil/guncelle', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        current_user.ad = request.form.get('ad')
        current_user.soyad = request.form.get('soyad')
        current_user.telefon = request.form.get('telefon')
        current_user.dogum_tarihi = request.form.get('dogum_tarihi')
        current_user.cinsiyet = request.form.get('cinsiyet')
        current_user.kan_grubu = request.form.get('kan_grubu')
        current_user.kronik_hastaliklar = request.form.get('kronik_hastaliklar')
        current_user.alerjiler = request.form.get('alerjiler')
        
        db.session.commit()
        flash('Profil bilgileriniz güncellendi!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/update_profile.html')

@auth.route('/sifre/guncelle', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        if not check_password_hash(current_user.password, old_password):
            flash('Mevcut şifreniz hatalı!', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        
        flash('Şifreniz başarıyla güncellendi!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/change_password.html')

@auth.route('/sifre/sifirla', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Şifre sıfırlama token'ı oluştur
            token = jwt.encode(
                {'reset_password': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                current_app.config['SECRET_KEY'], algorithm='HS256'
            )
            
            # Email gönder
            send_password_reset_email(user, token)
            flash('Şifre sıfırlama talimatları email adresinize gönderildi.', 'info')
            return redirect(url_for('auth.login'))
        
        flash('Bu email adresi kayıtlı değil!', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    return render_template('auth/reset_password_request.html') 
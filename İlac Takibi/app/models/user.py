from . import db, UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    parola_hash = db.Column(db.String(200), nullable=False)
    telefon = db.Column(db.String(15))
    dogum_tarihi = db.Column(db.Date)
    dil = db.Column(db.String(2), default='tr')
    tema = db.Column(db.String(10), default='light')
    bildirim_tercihleri = db.Column(db.JSON)
    son_giris = db.Column(db.DateTime)
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    aktif = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    receteler = db.relationship('Prescription', backref='hasta', lazy=True)
    hatirlaticilar = db.relationship('Reminder', backref='kullanici', lazy=True)
    saglik_olcumleri = db.relationship('HealthMetric', backref='kullanici', lazy=True)
    aile_uyeleri = db.relationship('FamilyMember', backref='kullanici', lazy=True)
    randevular = db.relationship('Appointment', backref='kullanici', lazy=True)
    acil_kisiler = db.relationship('EmergencyContact', backref='kullanici', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>' 
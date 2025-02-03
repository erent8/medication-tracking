from . import db
from datetime import datetime

class HealthMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tip = db.Column(db.String(50))  # Tansiyon, Şeker, Ateş, Nabız, Kilo, Kolesterol
    deger = db.Column(db.Float)
    birim = db.Column(db.String(20))
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    notlar = db.Column(db.Text)
    cihaz = db.Column(db.String(100))  # Ölçüm yapılan cihaz
    konum = db.Column(db.String(200))  # Ölçüm yapılan yer
    
    def __repr__(self):
        return f'<HealthMetric {self.tip}>'

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    uzmanlik = db.Column(db.String(100))
    hastane = db.Column(db.String(200))
    telefon = db.Column(db.String(15))
    email = db.Column(db.String(120))
    adres = db.Column(db.Text)
    
    # İlişkiler
    receteler = db.relationship('Prescription', backref='doktor', lazy=True)
    randevular = db.relationship('Appointment', backref='doktor', lazy=True)
    
    def __repr__(self):
        return f'<Doctor {self.ad} {self.soyad}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doktor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    tarih = db.Column(db.DateTime, nullable=False)
    tip = db.Column(db.String(50))  # Muayene, Kontrol, Tetkik
    durum = db.Column(db.String(20), default='Beklemede')  # Beklemede, Onaylandı, İptal, Tamamlandı
    notlar = db.Column(db.Text)
    hatirlatma = db.Column(db.Boolean, default=True)
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id}>'

class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    dogum_tarihi = db.Column(db.Date)
    yakinlik = db.Column(db.String(50))  # Anne, Baba, Eş, Çocuk
    notlar = db.Column(db.Text)
    
    def __repr__(self):
        return f'<FamilyMember {self.ad} {self.soyad}>'

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    telefon = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    yakinlik = db.Column(db.String(50))
    adres = db.Column(db.Text)
    oncelik = db.Column(db.Integer, default=1)  # 1: Birincil, 2: İkincil
    
    def __repr__(self):
        return f'<EmergencyContact {self.ad} {self.soyad}>' 
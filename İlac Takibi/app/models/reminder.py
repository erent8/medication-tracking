from . import db
from datetime import datetime

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ilac_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    recete_id = db.Column(db.Integer, db.ForeignKey('prescription.id'))
    zaman = db.Column(db.Time, nullable=False)
    gunler = db.Column(db.String(50))  # "1,2,3,4,5,6,7" şeklinde
    bildirim_tipi = db.Column(db.String(20))  # Email, SMS, Push, Alarm
    bildirim_oncesi = db.Column(db.Integer)  # Kaç dakika önce bildirim
    tekrar_sayisi = db.Column(db.Integer, default=1)  # Kaç kez tekrar edilecek
    aktif = db.Column(db.Boolean, default=True)
    son_hatirlatma = db.Column(db.DateTime)
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reminder {self.id}>'

class ReminderLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hatirlatici_id = db.Column(db.Integer, db.ForeignKey('reminder.id'), nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    durum = db.Column(db.String(20))  # Gönderildi, Alındı, Ertelendi, İptal
    notlar = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ReminderLog {self.id}>' 
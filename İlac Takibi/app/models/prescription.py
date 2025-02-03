from . import db
from datetime import datetime

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hasta_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ilac_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    doktor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    hastane = db.Column(db.String(100))
    baslangic_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    bitis_tarihi = db.Column(db.DateTime)
    dozaj = db.Column(db.String(200))
    kullanim_sekli = db.Column(db.String(200))
    notlar = db.Column(db.Text)
    durum = db.Column(db.String(20), default='Aktif')  # Aktif, Tamamlandı, İptal
    sigorta_durum = db.Column(db.String(50))  # Ödendi, Beklemede, Red
    fiyat = db.Column(db.Float)
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    hatirlaticilar = db.relationship('Reminder', backref='recete', lazy=True)
    
    def __repr__(self):
        return f'<Prescription {self.id}>' 
from . import db
from datetime import datetime

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    kullanim_amaci = db.Column(db.Text)
    faydalar = db.Column(db.Text)
    yan_etkiler = db.Column(db.Text)
    etkilesimler = db.Column(db.Text)
    dozaj = db.Column(db.String(200))
    barkod = db.Column(db.String(50), unique=True)
    uretici = db.Column(db.String(100))
    fiyat = db.Column(db.Float)
    resim_url = db.Column(db.String(200))
    prospektus_url = db.Column(db.String(200))
    aktif = db.Column(db.Boolean, default=True)
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    receteler = db.relationship('Prescription', backref='ilac', lazy=True)
    hatirlaticilar = db.relationship('Reminder', backref='ilac', lazy=True)
    alternatifler = db.relationship(
        'Medicine',
        secondary='medicine_alternatives',
        primaryjoin='Medicine.id == medicine_alternatives.c.medicine_id',
        secondaryjoin='Medicine.id == medicine_alternatives.c.alternative_id',
        backref=db.backref('ana_ilaclar', lazy=True)
    )
    
    def __repr__(self):
        return f'<Medicine {self.ad}>'

# İlaç alternatifleri için ara tablo
medicine_alternatives = db.Table('medicine_alternatives',
    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id'), primary_key=True),
    db.Column('alternative_id', db.Integer, db.ForeignKey('medicine.id'), primary_key=True)
) 
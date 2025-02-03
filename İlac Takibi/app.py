from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli_anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ilac_takip.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
db = SQLAlchemy(app)

# Örnek ilaç verileri
ornek_ilaclar = [
    {
        'ad': 'Paracetamol',
        'kategori': 'Ağrı Kesici',
        'kullanim_amaci': 'Hafif ve orta şiddetli ağrıların giderilmesi, ateş düşürülmesi',
        'faydalar': '''
        - Baş ağrısını giderir
        - Kas ağrılarını azaltır
        - Ateş düşürür
        - Diş ağrılarını hafifletir
        - Eklem ağrılarında etkilidir
        ''',
        'yan_etkiler': 'Yüksek dozlarda karaciğer hasarı riski, mide bulantısı, alerjik reaksiyonlar',
        'etkilesimler': 'Alkol ile birlikte kullanımı karaciğer hasarı riskini artırır',
        'dozaj': 'Yetişkinler için 6-8 saatte bir 500-1000 mg'
    },
    {
        'ad': 'Amoksisilin',
        'kategori': 'Antibiyotik',
        'kullanim_amaci': 'Bakteriyel enfeksiyonların tedavisi',
        'faydalar': '''
        - Üst solunum yolu enfeksiyonlarını tedavi eder
        - İdrar yolu enfeksiyonlarında etkili
        - Orta kulak iltihabını tedavi eder
        - Diş enfeksiyonlarında kullanılır
        - Sinüzit tedavisinde etkili
        ''',
        'yan_etkiler': 'İshal, mide bulantısı, alerjik reaksiyonlar, mantar enfeksiyonu riski',
        'etkilesimler': 'Bazı antibiyotiklerle etkileşime girebilir',
        'dozaj': 'Günde 3 kez 500 mg, enfeksiyonun şiddetine göre değişebilir'
    },
    {
        'ad': 'Sertralin',
        'kategori': 'Antidepresan',
        'kullanim_amaci': 'Depresyon, anksiyete ve panik bozukluğu tedavisi',
        'faydalar': '''
        - Depresyon semptomlarını azaltır
        - Anksiyete belirtilerini hafifletir
        - Panik atak sıklığını düşürür
        - Sosyal fobi tedavisinde etkili
        - Obsesif kompulsif bozukluk tedavisinde yardımcı
        ''',
        'yan_etkiler': 'Uyku problemleri, baş dönmesi, mide bulantısı, iştah değişiklikleri',
        'etkilesimler': 'MAO inhibitörleri ile kullanılmamalıdır',
        'dozaj': 'Günde bir kez 50-200 mg'
    },
    {
        'ad': 'Metformin',
        'kategori': 'Diyabet İlacı',
        'kullanim_amaci': 'Tip 2 diyabet tedavisi',
        'faydalar': '''
        - Kan şekerini düşürür
        - İnsülin direncini azaltır
        - Kilo kontrolüne yardımcı olur
        - Kalp hastalığı riskini azaltır
        - Karaciğer yağlanmasını azaltır
        ''',
        'yan_etkiler': 'Mide bulantısı, ishal, vitamin B12 eksikliği, metalik tat',
        'etkilesimler': 'Alkol ile birlikte kullanımından kaçınılmalıdır',
        'dozaj': 'Günde 2-3 kez 500-1000 mg'
    },
    {
        'ad': 'Pantoprazol',
        'kategori': 'Mide İlacı',
        'kullanim_amaci': 'Mide asidi fazlalığı ve reflü tedavisi',
        'faydalar': '''
        - Mide asidini azaltır
        - Reflü şikayetlerini giderir
        - Mide ülserini tedavi eder
        - Mide yanmasını önler
        - Yemek borusu iltihabını iyileştirir
        ''',
        'yan_etkiler': 'Baş ağrısı, ishal, vitamin B12 eksikliği riski',
        'etkilesimler': 'Bazı ilaçların emilimini etkileyebilir',
        'dozaj': 'Günde bir kez 40 mg'
    },
    {
        'ad': 'Atorvastatin',
        'kategori': 'Kolesterol İlacı',
        'kullanim_amaci': 'Yüksek kolesterol tedavisi',
        'faydalar': '''
        - Kötü kolesterolü düşürür
        - İyi kolesterolü yükseltir
        - Kalp krizi riskini azaltır
        - Damar sertliğini önler
        - İnme riskini azaltır
        ''',
        'yan_etkiler': 'Kas ağrıları, karaciğer enzimlerinde yükselme',
        'etkilesimler': 'Greyfurt suyu ile etkileşime girer',
        'dozaj': 'Günde bir kez 10-80 mg'
    },
    {
        'ad': 'Levotiroksin',
        'kategori': 'Tiroid İlacı',
        'kullanim_amaci': 'Tiroid hormonu eksikliğinin tedavisi',
        'faydalar': '''
        - Tiroid hormonunu dengeler
        - Metabolizmayı düzenler
        - Enerji seviyesini artırır
        - Kilo kontrolüne yardımcı olur
        - Kolesterol seviyelerini düzenler
        ''',
        'yan_etkiler': 'Kalp çarpıntısı, uykusuzluk, titreme',
        'etkilesimler': 'Demir ve kalsiyum takviyeleri emilimi etkileyebilir',
        'dozaj': 'Günde bir kez 25-200 mcg'
    },
    {
        'ad': 'Montelukast',
        'kategori': 'Alerji İlacı',
        'kullanim_amaci': 'Astım ve alerjik rinit tedavisi',
        'faydalar': '''
        - Astım semptomlarını azaltır
        - Alerjik nezle belirtilerini hafifletir
        - Nefes almayı kolaylaştırır
        - Öksürüğü azaltır
        - Egzersiz kaynaklı astımı önler
        ''',
        'yan_etkiler': 'Baş ağrısı, karın ağrısı, davranış değişiklikleri',
        'etkilesimler': 'Önemli bir ilaç etkileşimi bildirilmemiştir',
        'dozaj': 'Günde bir kez 10 mg'
    }
]

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    parola_hash = db.Column(db.String(200), nullable=False)
    telefon = db.Column(db.String(15))
    dogum_tarihi = db.Column(db.Date)
    receteler = db.relationship('Recete', backref='hasta', lazy=True)
    hatirlaticilar = db.relationship('Hatirlatici', backref='kullanici', lazy=True)

class Ilac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    kullanim_amaci = db.Column(db.Text)
    faydalar = db.Column(db.Text)
    yan_etkiler = db.Column(db.Text)
    etkilesimler = db.Column(db.Text)
    dozaj = db.Column(db.String(200))
    receteler = db.relationship('Recete', backref='ilac', lazy=True)
    hatirlaticilar = db.relationship('Hatirlatici', backref='ilac', lazy=True)

class Recete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hasta_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    ilac_id = db.Column(db.Integer, db.ForeignKey('ilac.id'), nullable=False)
    baslangic_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    bitis_tarihi = db.Column(db.DateTime)
    doktor_adi = db.Column(db.String(100))
    dozaj = db.Column(db.String(200))
    notlar = db.Column(db.Text)
    durum = db.Column(db.String(20), default='Aktif')  # Aktif, Tamamlandı, İptal

class Hatirlatici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    ilac_id = db.Column(db.Integer, db.ForeignKey('ilac.id'), nullable=False)
    zaman = db.Column(db.Time, nullable=False)
    gunler = db.Column(db.String(50))  # "1,2,3,4,5,6,7" şeklinde
    aktif = db.Column(db.Boolean, default=True)
    son_hatirlatma = db.Column(db.DateTime)

class SaglikTakip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    tip = db.Column(db.String(50))  # Tansiyon, Şeker, Ateş vb.
    deger = db.Column(db.Float)
    birim = db.Column(db.String(20))
    notlar = db.Column(db.Text)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'kullanici_id' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('giris'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        email = request.form['email']
        parola = request.form['parola']
        telefon = request.form['telefon']
        dogum_tarihi = datetime.strptime(request.form['dogum_tarihi'], '%Y-%m-%d')

        if Kullanici.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kayıtlı!', 'danger')
            return redirect(url_for('kayit'))

        yeni_kullanici = Kullanici(
            ad=ad,
            soyad=soyad,
            email=email,
            parola_hash=generate_password_hash(parola),
            telefon=telefon,
            dogum_tarihi=dogum_tarihi
        )
        db.session.add(yeni_kullanici)
        db.session.commit()

        flash('Kayıt başarıyla tamamlandı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('giris'))

    return render_template('kayit.html')

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        email = request.form['email']
        parola = request.form['parola']
        
        kullanici = Kullanici.query.filter_by(email=email).first()
        
        if kullanici and check_password_hash(kullanici.parola_hash, parola):
            session['kullanici_id'] = kullanici.id
            session['kullanici_ad'] = kullanici.ad
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('profil'))
        else:
            flash('E-posta veya parola hatalı!', 'danger')
    
    return render_template('giris.html')

@app.route('/cikis')
def cikis():
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('ana_sayfa'))

@app.route('/profil')
@login_required
def profil():
    kullanici = Kullanici.query.get(session['kullanici_id'])
    aktif_receteler = Recete.query.filter_by(
        hasta_id=kullanici.id,
        durum='Aktif'
    ).order_by(Recete.baslangic_tarihi.desc()).all()
    
    gecmis_receteler = Recete.query.filter(
        Recete.hasta_id == kullanici.id,
        Recete.durum != 'Aktif'
    ).order_by(Recete.baslangic_tarihi.desc()).all()
    
    hatirlaticilar = Hatirlatici.query.filter_by(
        kullanici_id=kullanici.id,
        aktif=True
    ).all()
    
    saglik_takipler = SaglikTakip.query.filter_by(
        kullanici_id=kullanici.id
    ).order_by(SaglikTakip.tarih.desc()).limit(10).all()
    
    return render_template('profil.html',
                         kullanici=kullanici,
                         aktif_receteler=aktif_receteler,
                         gecmis_receteler=gecmis_receteler,
                         hatirlaticilar=hatirlaticilar,
                         saglik_takipler=saglik_takipler)

@app.route('/hatirlatici/ekle', methods=['GET', 'POST'])
@login_required
def hatirlatici_ekle():
    if request.method == 'POST':
        ilac_id = request.form['ilac_id']
        zaman = datetime.strptime(request.form['zaman'], '%H:%M').time()
        gunler = ','.join(request.form.getlist('gunler'))
        
        yeni_hatirlatici = Hatirlatici(
            kullanici_id=session['kullanici_id'],
            ilac_id=ilac_id,
            zaman=zaman,
            gunler=gunler
        )
        db.session.add(yeni_hatirlatici)
        db.session.commit()
        
        flash('Hatırlatıcı başarıyla eklendi!', 'success')
        return redirect(url_for('profil'))
    
    ilaclar = Ilac.query.all()
    return render_template('hatirlatici_ekle.html', ilaclar=ilaclar)

@app.route('/saglik-takip/ekle', methods=['GET', 'POST'])
@login_required
def saglik_takip_ekle():
    if request.method == 'POST':
        tip = request.form['tip']
        deger = float(request.form['deger'])
        birim = request.form['birim']
        notlar = request.form['notlar']
        
        yeni_takip = SaglikTakip(
            kullanici_id=session['kullanici_id'],
            tip=tip,
            deger=deger,
            birim=birim,
            notlar=notlar
        )
        db.session.add(yeni_takip)
        db.session.commit()
        
        flash('Sağlık takip kaydı başarıyla eklendi!', 'success')
        return redirect(url_for('profil'))
    
    return render_template('saglik_takip_ekle.html')

@app.route('/recete/<int:recete_id>/durum-guncelle', methods=['POST'])
@login_required
def recete_durum_guncelle(recete_id):
    recete = Recete.query.get_or_404(recete_id)
    if recete.hasta_id != session['kullanici_id']:
        flash('Bu işlem için yetkiniz yok!', 'danger')
        return redirect(url_for('profil'))
    
    yeni_durum = request.form['durum']
    recete.durum = yeni_durum
    db.session.commit()
    
    flash('Reçete durumu güncellendi!', 'success')
    return redirect(url_for('profil'))

@app.route('/')
def ana_sayfa():
    kategoriler = ['Ağrı Kesici', 'Antibiyotik', 'Antidepresan', 'Diyabet İlacı', 
                  'Mide İlacı', 'Kolesterol İlacı', 'Tiroid İlacı', 'Alerji İlacı']
    ilaclar = Ilac.query.all()
    if not ilaclar:  # Veritabanı boşsa örnek ilaçları ekle
        for ilac_veri in ornek_ilaclar:
            yeni_ilac = Ilac(
                ad=ilac_veri['ad'],
                kategori=ilac_veri['kategori'],
                kullanim_amaci=ilac_veri['kullanim_amaci'],
                faydalar=ilac_veri['faydalar'],
                yan_etkiler=ilac_veri['yan_etkiler'],
                etkilesimler=ilac_veri['etkilesimler'],
                dozaj=ilac_veri['dozaj']
            )
            db.session.add(yeni_ilac)
        db.session.commit()
        ilaclar = Ilac.query.all()
    
    return render_template('ana_sayfa.html', ilaclar=ilaclar, kategoriler=kategoriler)

@app.route('/ilac/<int:ilac_id>')
def ilac_detay(ilac_id):
    ilac = Ilac.query.get_or_404(ilac_id)
    return render_template('ilac_detay.html', ilac=ilac)

@app.route('/recete/ekle', methods=['GET', 'POST'])
@login_required
def recete_ekle():
    if request.method == 'POST':
        ilac_id = request.form['ilac_id']
        baslangic = datetime.strptime(request.form['baslangic_tarihi'], '%Y-%m-%d')
        bitis = datetime.strptime(request.form['bitis_tarihi'], '%Y-%m-%d')
        doktor_adi = request.form['doktor_adi']
        dozaj = request.form['dozaj']
        notlar = request.form['notlar']
        
        yeni_recete = Recete(
            hasta_id=session['kullanici_id'],
            ilac_id=ilac_id,
            baslangic_tarihi=baslangic,
            bitis_tarihi=bitis,
            doktor_adi=doktor_adi,
            dozaj=dozaj,
            notlar=notlar
        )
        db.session.add(yeni_recete)
        db.session.commit()
        
        flash('Reçete başarıyla eklendi!', 'success')
        return redirect(url_for('profil'))
    
    ilaclar = Ilac.query.all()
    return render_template('recete_ekle.html', ilaclar=ilaclar)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Ilac.query.first():  # Veritabanında hiç ilaç yoksa
            for ilac_veri in ornek_ilaclar:
                yeni_ilac = Ilac(
                    ad=ilac_veri['ad'],
                    kategori=ilac_veri['kategori'],
                    kullanim_amaci=ilac_veri['kullanim_amaci'],
                    faydalar=ilac_veri['faydalar'],
                    yan_etkiler=ilac_veri['yan_etkiler'],
                    etkilesimler=ilac_veri['etkilesimler'],
                    dozaj=ilac_veri['dozaj']
                )
                db.session.add(yeni_ilac)
            db.session.commit()
    
    app.run(debug=True) 
# 🏥 İlaç Takip Uygulaması

Bu uygulama, kullanıcıların sağlık verilerini takip etmelerine, randevularını yönetmelerine ve sağlıklı yaşam hedeflerini izlemelerine olanak tanıyan kapsamlı bir sağlık yönetim platformudur.

## 🌟 Özellikler

### 📊 Sağlık Metrikleri
- Tansiyon, nabız, şeker, kilo gibi sağlık ölçümlerini kaydetme
- Ölçüm geçmişini görüntüleme ve analiz etme
- Grafiklerle veri görselleştirme

### 🎯 Sağlık Hedefleri
- Kişisel sağlık hedefleri belirleme
- İlerleme takibi
- Hedef gerçekleştirme bildirimleri

### 🏃‍♂️ Yaşam Tarzı Takibi
- Egzersiz aktivitelerini kaydetme
- Beslenme günlüğü tutma
- Uyku düzenini takip etme

### 📅 Randevu Yönetimi
- Doktor randevularını planlama
- Randevu hatırlatmaları
- Geçmiş randevuları görüntüleme

### 📱 Akıllı Bildirimler
- E-posta bildirimleri
- SMS bildirimleri
- Push bildirimleri

## 🛠️ Teknolojiler

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Veritabanı:** SQLite
- **UI Framework:** Bootstrap 5
- **Grafikler:** Plotly
- **İkonlar:** Font Awesome

## 📦 Gereksinimler

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Mail==0.9.1
Flask-Babel==4.0.0
python-dotenv==1.0.0
plotly==5.18.0
pandas==2.1.3
```

## 🚀 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/kullaniciadi/saglik-takip.git
cd saglik-takip
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv .venv
# Windows için
.venv\Scripts\activate
# Linux/Mac için
source .venv/bin/activate
```

3. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

4. `.env` dosyasını oluşturun:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=gizli_anahtar_buraya_yazilacak
DATABASE_URL=sqlite:///saglik_takip.db
```

5. Veritabanını oluşturun:
```bash
flask db upgrade
```

6. Uygulamayı çalıştırın:
```bash
flask run
```

## 📱 Ekran Görüntüleri

- Ana Sayfa
- Kontrol Paneli
- Sağlık Metrikleri
- Randevu Yönetimi
- Profil Sayfası

## 🔒 Güvenlik

- Şifreli kullanıcı kimlik doğrulama
- Güvenli parola yönetimi
- CSRF koruması
- XSS önleme
- SQL enjeksiyon koruması

## 🌐 Tarayıcı Desteği

- Chrome (son 3 versiyon)
- Firefox (son 3 versiyon)
- Safari (son 3 versiyon)
- Edge (son 3 versiyon)

## 🤝 Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: XYZ'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 İletişim

- Proje Sahibi: [Ad Soyad]
- E-posta: [E-posta adresi]
- Website: [Website adresi]

## 🙏 Teşekkürler

Bu projeye katkıda bulunan herkese teşekkür ederiz! 

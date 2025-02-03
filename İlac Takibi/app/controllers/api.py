from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.reminder import Reminder
from app.models.health import HealthMetric, Doctor, Appointment
from app import db
from datetime import datetime, timedelta
import qrcode
import io
import base64
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import os

api = Blueprint('api', __name__)

@api.route('/medicines')
@login_required
def list_medicines():
    medicines = Medicine.query.join(Prescription).filter(
        Prescription.hasta_id == current_user.id
    ).all()
    
    return jsonify([{
        'id': m.id,
        'ad': m.ad,
        'etken_madde': m.etken_madde,
        'form': m.form,
        'doz': m.doz,
        'firma': m.firma,
        'barkod': m.barkod,
        'recete': {
            'id': m.recete.id,
            'baslangic_tarihi': m.recete.baslangic_tarihi.isoformat(),
            'bitis_tarihi': m.recete.bitis_tarihi.isoformat(),
            'dozaj': m.recete.dozaj,
            'kullanim_sekli': m.recete.kullanim_sekli
        }
    } for m in medicines])

@api.route('/medicines/<int:id>')
@login_required
def get_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    prescription = Prescription.query.filter_by(
        hasta_id=current_user.id,
        ilac_id=id
    ).first_or_404()
    
    return jsonify({
        'id': medicine.id,
        'ad': medicine.ad,
        'etken_madde': medicine.etken_madde,
        'form': medicine.form,
        'doz': medicine.doz,
        'firma': medicine.firma,
        'barkod': medicine.barkod,
        'recete': {
            'id': prescription.id,
            'baslangic_tarihi': prescription.baslangic_tarihi.isoformat(),
            'bitis_tarihi': prescription.bitis_tarihi.isoformat(),
            'dozaj': prescription.dozaj,
            'kullanim_sekli': prescription.kullanim_sekli,
            'notlar': prescription.notlar
        }
    })

@api.route('/medicines/qr/<int:id>')
@login_required
def get_medicine_qr(id):
    medicine = Medicine.query.get_or_404(id)
    prescription = Prescription.query.filter_by(
        hasta_id=current_user.id,
        ilac_id=id
    ).first_or_404()
    
    # QR kod oluştur
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"İlaç: {medicine.ad}\nDoz: {prescription.dozaj}\nKullanım: {prescription.kullanim_sekli}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # QR kodu base64'e çevir
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'qr_code': qr_code})

@api.route('/pharmacies')
@login_required
def find_pharmacies():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    radius = float(request.args.get('radius', 1000))  # Varsayılan 1km
    
    # Google Places API'yi kullan
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{lat},{lon}",
        'radius': radius,
        'type': 'pharmacy',
        'key': os.getenv('GOOGLE_MAPS_API_KEY')
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    pharmacies = []
    for place in data.get('results', []):
        pharmacies.append({
            'name': place['name'],
            'address': place.get('vicinity'),
            'lat': place['geometry']['location']['lat'],
            'lon': place['geometry']['location']['lng'],
            'rating': place.get('rating'),
            'open_now': place.get('opening_hours', {}).get('open_now')
        })
    
    return jsonify(pharmacies)

@api.route('/health/chart/<int:user_id>')
@login_required
def get_health_chart(user_id):
    if user_id != current_user.id:
        return jsonify({'error': 'Yetkiniz yok!'}), 403
    
    tip = request.args.get('tip')
    start_date = datetime.now() - timedelta(days=30)
    
    metrics = HealthMetric.query.filter(
        HealthMetric.kullanici_id == user_id,
        HealthMetric.tip == tip,
        HealthMetric.tarih >= start_date
    ).order_by(HealthMetric.tarih).all()
    
    data = [{
        'tarih': m.tarih.isoformat(),
        'deger': m.deger,
        'birim': m.birim
    } for m in metrics]
    
    return jsonify(data)

@api.route('/interactions')
@login_required
def check_interactions():
    drug_ids = request.args.getlist('drugs[]')
    medicines = Medicine.query.filter(Medicine.id.in_(drug_ids)).all()
    
    # Bu kısım gelecekte gerçek bir ilaç etkileşimi API'si ile değiştirilebilir
    interactions = []
    if len(medicines) > 1:
        for i in range(len(medicines)):
            for j in range(i + 1, len(medicines)):
                interactions.append({
                    'ilac1': medicines[i].ad,
                    'ilac2': medicines[j].ad,
                    'risk_seviyesi': 'Bilinmiyor',
                    'aciklama': 'İlaç etkileşimi bilgisi mevcut değil.'
                })
    
    return jsonify(interactions)

@api.route('/doctors')
@login_required
def list_doctors():
    doctors = Doctor.query.all()
    return jsonify([{
        'id': d.id,
        'ad': d.ad,
        'soyad': d.soyad,
        'uzmanlik': d.uzmanlik,
        'hastane': d.hastane,
        'telefon': d.telefon,
        'email': d.email
    } for d in doctors])

@api.route('/appointments')
@login_required
def list_appointments():
    appointments = Appointment.query.filter_by(
        kullanici_id=current_user.id
    ).order_by(Appointment.tarih).all()
    
    return jsonify([{
        'id': a.id,
        'doktor': f"{a.doktor.ad} {a.doktor.soyad}",
        'tarih': a.tarih.isoformat(),
        'tip': a.tip,
        'durum': a.durum,
        'notlar': a.notlar
    } for a in appointments])

@api.route('/reminders/next')
@login_required
def get_next_reminders():
    reminders = Reminder.query.filter(
        Reminder.kullanici_id == current_user.id,
        Reminder.aktif == True
    ).order_by(Reminder.zaman).all()
    
    next_reminders = []
    now = datetime.now()
    
    for reminder in reminders:
        next_time = reminder.zaman.replace(
            year=now.year,
            month=now.month,
            day=now.day
        )
        
        if next_time < now:
            next_time = next_time + timedelta(days=1)
        
        next_reminders.append({
            'id': reminder.id,
            'ilac': reminder.ilac.ad,
            'zaman': next_time.isoformat(),
            'dozaj': reminder.recete.dozaj,
            'kullanim_sekli': reminder.recete.kullanim_sekli
        })
    
    return jsonify(next_reminders) 
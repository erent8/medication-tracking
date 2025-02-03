import qrcode
from PIL import Image
import io
import folium
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import jwt
import requests
from flask import current_app
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def generate_qr_code(data):
    """QR kod oluşturur"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def find_nearby_pharmacies(lat, lon, radius=5000):
    """Yakındaki eczaneleri bulur"""
    geolocator = Nominatim(user_agent="ilac_takip")
    map_center = [lat, lon]
    m = folium.Map(location=map_center, zoom_start=14)
    
    # Google Places API ile eczane araması
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "pharmacy",
        "key": current_app.config['GOOGLE_MAPS_API_KEY']
    }
    
    response = requests.get(url, params=params)
    pharmacies = response.json().get('results', [])
    
    for pharmacy in pharmacies:
        folium.Marker(
            location=[pharmacy['geometry']['location']['lat'], 
                     pharmacy['geometry']['location']['lng']],
            popup=pharmacy['name'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    return m._repr_html_()

def generate_health_chart(data, metric_type):
    """Sağlık verilerinin grafiğini oluşturur"""
    df = pd.DataFrame(data)
    
    if metric_type == 'line':
        fig = px.line(df, x='tarih', y='deger', title='Sağlık Takibi')
    elif metric_type == 'bar':
        fig = px.bar(df, x='tarih', y='deger', title='Sağlık Takibi')
    else:
        fig = px.scatter(df, x='tarih', y='deger', title='Sağlık Takibi')
    
    return fig.to_html()

def generate_token(user_id, expires_in=3600):
    """JWT token oluşturur"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """JWT token doğrular"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def check_drug_interactions(drug_list):
    """İlaç etkileşimlerini kontrol eder"""
    interactions = []
    for i in range(len(drug_list)):
        for j in range(i + 1, len(drug_list)):
            # İlaç etkileşim API'si entegrasyonu yapılabilir
            pass
    return interactions

def format_phone_number(phone):
    """Telefon numarasını formatlar"""
    if not phone:
        return ""
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone

def calculate_bmi(weight, height):
    """Vücut kitle indeksini hesaplar"""
    try:
        height_m = height / 100  # cm'yi m'ye çevir
        bmi = weight / (height_m * height_m)
        return round(bmi, 2)
    except:
        return None

def get_weather():
    """Hava durumu bilgisini getirir"""
    # OpenWeatherMap API entegrasyonu yapılabilir
    pass

def send_emergency_sms(phone, message):
    """Acil durum SMS'i gönderir"""
    # SMS API entegrasyonu yapılabilir
    pass

def calculate_next_dose(last_dose, frequency):
    """Bir sonraki doz zamanını hesaplar"""
    if frequency == 'daily':
        return last_dose + timedelta(days=1)
    elif frequency == '12h':
        return last_dose + timedelta(hours=12)
    elif frequency == '8h':
        return last_dose + timedelta(hours=8)
    elif frequency == '6h':
        return last_dose + timedelta(hours=6)
    return None 
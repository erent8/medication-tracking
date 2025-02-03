from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.reminder import Reminder
from app.models.health import HealthMetric, Doctor, Appointment
from app import db
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Aktif ilaçlar
    active_medicines = Medicine.query.join(Prescription).filter(
        Prescription.hasta_id == current_user.id,
        Prescription.bitis_tarihi >= datetime.now()
    ).all()
    
    # Yaklaşan hatırlatıcılar
    upcoming_reminders = Reminder.query.filter(
        Reminder.kullanici_id == current_user.id,
        Reminder.aktif == True
    ).order_by(Reminder.zaman).limit(5).all()
    
    # Yaklaşan randevular
    upcoming_appointments = Appointment.query.filter(
        Appointment.kullanici_id == current_user.id,
        Appointment.tarih >= datetime.now()
    ).order_by(Appointment.tarih).limit(3).all()
    
    # Son sağlık ölçümleri
    recent_metrics = HealthMetric.query.filter_by(
        kullanici_id=current_user.id
    ).order_by(HealthMetric.tarih.desc()).limit(5).all()
    
    return render_template('main/dashboard.html',
                         active_medicines=active_medicines,
                         upcoming_reminders=upcoming_reminders,
                         upcoming_appointments=upcoming_appointments,
                         recent_metrics=recent_metrics)

@main.route('/profil')
@login_required
def profile():
    return render_template('main/profile.html')

@main.route('/takvim')
@login_required
def calendar():
    # İlaç hatırlatıcıları
    reminders = Reminder.query.filter_by(
        kullanici_id=current_user.id,
        aktif=True
    ).all()
    
    # Randevular
    appointments = Appointment.query.filter_by(
        kullanici_id=current_user.id
    ).all()
    
    events = []
    
    # Hatırlatıcıları events listesine ekle
    for reminder in reminders:
        # Her gün için tekrarlanan hatırlatıcılar oluştur
        if reminder.gunler:
            gun_listesi = [int(gun) for gun in reminder.gunler.split(',')]
            for gun in gun_listesi:
                events.append({
                    'title': f'İlaç: {reminder.ilac.ad}',
                    'description': f'Dozaj: {reminder.recete.dozaj if reminder.recete else "Belirtilmemiş"}',
                    'start': reminder.zaman.strftime('%H:%M'),
                    'daysOfWeek': [gun],  # 1=Pazartesi, 7=Pazar
                    'color': '#0d6efd',
                    'url': url_for('medicine.view', id=reminder.ilac_id),
                    'extendedProps': {
                        'type': 'reminder',
                        'ilacAd': reminder.ilac.ad,
                        'dozaj': reminder.recete.dozaj if reminder.recete else "Belirtilmemiş",
                        'kullanımSekli': reminder.recete.kullanim_sekli if reminder.recete else "Belirtilmemiş"
                    }
                })
    
    # Randevuları events listesine ekle
    for appointment in appointments:
        events.append({
            'title': f'Randevu: Dr. {appointment.doktor.ad} {appointment.doktor.soyad}',
            'description': f'Tip: {appointment.tip}\nHastane: {appointment.doktor.hastane}',
            'start': appointment.tarih.isoformat(),
            'color': '#198754',
            'url': url_for('health.appointments'),
            'extendedProps': {
                'type': 'appointment',
                'doktorAd': f'Dr. {appointment.doktor.ad} {appointment.doktor.soyad}',
                'hastane': appointment.doktor.hastane,
                'tip': appointment.tip,
                'notlar': appointment.notlar
            }
        })
    
    # Reçete bitiş tarihlerini events listesine ekle
    prescriptions = Prescription.query.filter_by(
        hasta_id=current_user.id,
        durum='Aktif'
    ).all()
    
    for prescription in prescriptions:
        if prescription.bitis_tarihi:
            events.append({
                'title': f'Reçete Bitiş: {prescription.ilac.ad}',
                'description': 'Reçete kullanım süresi sona eriyor',
                'start': prescription.bitis_tarihi.isoformat(),
                'color': '#dc3545',
                'url': url_for('medicine.view', id=prescription.ilac_id),
                'extendedProps': {
                    'type': 'prescription_end',
                    'ilacAd': prescription.ilac.ad,
                    'doktor': f'Dr. {prescription.doktor.ad} {prescription.doktor.soyad}' if prescription.doktor else 'Belirtilmemiş',
                    'notlar': prescription.notlar
                }
            })
    
    return render_template('main/calendar.html', events=events)

@main.route('/istatistikler')
@login_required
def statistics():
    # Son 30 günlük ilaç kullanım istatistikleri
    start_date = datetime.now() - timedelta(days=30)
    
    # İlaç kullanım sayıları
    medicine_usage = db.session.query(
        Medicine.ad,
        db.func.count(Reminder.id).label('kullanim_sayisi')
    ).join(Reminder).filter(
        Reminder.kullanici_id == current_user.id,
        Reminder.tarih >= start_date
    ).group_by(Medicine.ad).all()
    
    # Sağlık ölçümleri
    health_metrics = HealthMetric.query.filter(
        HealthMetric.kullanici_id == current_user.id,
        HealthMetric.tarih >= start_date
    ).order_by(HealthMetric.tarih).all()
    
    # Randevu istatistikleri
    appointment_stats = db.session.query(
        Doctor.uzmanlik,
        db.func.count(Appointment.id).label('randevu_sayisi')
    ).join(Appointment).filter(
        Appointment.kullanici_id == current_user.id,
        Appointment.tarih >= start_date
    ).group_by(Doctor.uzmanlik).all()
    
    return render_template('main/statistics.html',
                         medicine_usage=medicine_usage,
                         health_metrics=health_metrics,
                         appointment_stats=appointment_stats)

@main.route('/ayarlar', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Bildirim ayarları
        current_user.bildirim_email = 'email' in request.form
        current_user.bildirim_sms = 'sms' in request.form
        current_user.bildirim_push = 'push' in request.form
        
        # Gizlilik ayarları
        current_user.veri_paylasimi = 'veri_paylasimi' in request.form
        
        # Dil ayarı
        current_user.dil = request.form.get('dil', 'tr')
        
        db.session.commit()
        flash('Ayarlarınız güncellendi!', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('main/settings.html') 
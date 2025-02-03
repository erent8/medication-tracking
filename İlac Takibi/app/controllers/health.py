from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.health import HealthMetric, Doctor, Appointment
from app import db
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import json

health = Blueprint('health', __name__)

@health.route('/saglik/olcumler')
@login_required
def metrics():
    metrics = HealthMetric.query.filter_by(
        kullanici_id=current_user.id
    ).order_by(HealthMetric.tarih.desc()).all()
    
    return render_template('health/metrics.html', metrics=metrics)

@health.route('/saglik/olcum/ekle', methods=['GET', 'POST'])
@login_required
def add_metric():
    if request.method == 'POST':
        tip = request.form.get('tip')
        deger = float(request.form.get('deger'))
        birim = request.form.get('birim')
        tarih = datetime.strptime(request.form.get('tarih'), '%Y-%m-%d %H:%M')
        notlar = request.form.get('notlar')
        cihaz = request.form.get('cihaz')
        konum = request.form.get('konum')
        
        metric = HealthMetric(
            kullanici_id=current_user.id,
            tip=tip,
            deger=deger,
            birim=birim,
            tarih=tarih,
            notlar=notlar,
            cihaz=cihaz,
            konum=konum
        )
        
        db.session.add(metric)
        db.session.commit()
        
        flash('Sağlık ölçümü başarıyla kaydedildi!', 'success')
        return redirect(url_for('health.metrics'))
    
    return render_template('health/add_metric.html')

@health.route('/saglik/olcum/<int:id>/sil')
@login_required
def delete_metric(id):
    metric = HealthMetric.query.get_or_404(id)
    
    if metric.kullanici_id != current_user.id:
        flash('Bu işlem için yetkiniz yok!', 'danger')
        return redirect(url_for('health.metrics'))
    
    db.session.delete(metric)
    db.session.commit()
    
    flash('Sağlık ölçümü silindi!', 'success')
    return redirect(url_for('health.metrics'))

@health.route('/saglik/grafik/<tip>')
@login_required
def chart(tip):
    # Son 30 günlük ölçümleri al
    start_date = datetime.now() - timedelta(days=30)
    metrics = HealthMetric.query.filter(
        HealthMetric.kullanici_id == current_user.id,
        HealthMetric.tip == tip,
        HealthMetric.tarih >= start_date
    ).order_by(HealthMetric.tarih).all()
    
    # Pandas DataFrame oluştur
    df = pd.DataFrame([{
        'tarih': m.tarih,
        'deger': m.deger,
        'birim': m.birim
    } for m in metrics])
    
    # Grafik oluştur
    fig = px.line(df, x='tarih', y='deger', title=f'{tip} Değişimi')
    fig.update_layout(yaxis_title=f'{tip} ({metrics[0].birim if metrics else ""})')
    
    # HTML'e çevir
    chart_html = fig.to_html(full_html=False)
    
    return render_template('health/chart.html',
                         chart_html=chart_html,
                         tip=tip)

@health.route('/doktorlar')
@login_required
def doctors():
    doctors = Doctor.query.all()
    return render_template('health/doctors.html', doctors=doctors)

@health.route('/doktor/ekle', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        doctor = Doctor(
            ad=request.form.get('ad'),
            soyad=request.form.get('soyad'),
            uzmanlik=request.form.get('uzmanlik'),
            hastane=request.form.get('hastane'),
            telefon=request.form.get('telefon'),
            email=request.form.get('email'),
            adres=request.form.get('adres')
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doktor başarıyla eklendi!', 'success')
        return redirect(url_for('health.doctors'))
    
    return render_template('health/add_doctor.html')

@health.route('/randevular')
@login_required
def appointments():
    # Geçmiş randevular
    past_appointments = Appointment.query.filter(
        Appointment.kullanici_id == current_user.id,
        Appointment.tarih < datetime.now()
    ).order_by(Appointment.tarih.desc()).all()
    
    # Gelecek randevular
    upcoming_appointments = Appointment.query.filter(
        Appointment.kullanici_id == current_user.id,
        Appointment.tarih >= datetime.now()
    ).order_by(Appointment.tarih).all()
    
    return render_template('health/appointments.html',
                         past_appointments=past_appointments,
                         upcoming_appointments=upcoming_appointments)

@health.route('/randevu/ekle', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if request.method == 'POST':
        appointment = Appointment(
            kullanici_id=current_user.id,
            doktor_id=request.form.get('doktor_id'),
            tarih=datetime.strptime(request.form.get('tarih'), '%Y-%m-%d %H:%M'),
            tip=request.form.get('tip'),
            notlar=request.form.get('notlar'),
            hatirlatma=True if request.form.get('hatirlatma') else False
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Randevu başarıyla oluşturuldu!', 'success')
        return redirect(url_for('health.appointments'))
    
    doctors = Doctor.query.all()
    return render_template('health/add_appointment.html', doctors=doctors)

@health.route('/randevu/<int:id>/iptal')
@login_required
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    if appointment.kullanici_id != current_user.id:
        flash('Bu işlem için yetkiniz yok!', 'danger')
        return redirect(url_for('health.appointments'))
    
    if appointment.tarih < datetime.now():
        flash('Geçmiş randevular iptal edilemez!', 'warning')
        return redirect(url_for('health.appointments'))
    
    appointment.durum = 'İptal Edildi'
    db.session.commit()
    
    flash('Randevu iptal edildi!', 'success')
    return redirect(url_for('health.appointments'))

@health.route('/randevu/<int:id>/notlar', methods=['POST'])
@login_required
def update_appointment_notes(id):
    appointment = Appointment.query.get_or_404(id)
    
    if appointment.kullanici_id != current_user.id:
        return jsonify({'error': 'Yetkiniz yok!'}), 403
    
    appointment.notlar = request.form.get('notlar')
    db.session.commit()
    
    return jsonify({'success': True}) 
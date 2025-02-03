from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.reminder import Reminder, ReminderLog
from app import db
from datetime import datetime, timedelta
import qrcode
import io
import base64

medicine = Blueprint('medicine', __name__)

@medicine.route('/ilaclar')
@login_required
def list():
    medicines = Medicine.query.join(Prescription).filter(
        Prescription.hasta_id == current_user.id
    ).all()
    return render_template('medicine/list.html', medicines=medicines)

@medicine.route('/ilac/<int:id>')
@login_required
def view(id):
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
    
    return render_template('medicine/view.html',
                         medicine=medicine,
                         prescription=prescription,
                         qr_code=qr_code)

@medicine.route('/ilac/ekle', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # İlaç bilgileri
        ad = request.form.get('ad')
        etken_madde = request.form.get('etken_madde')
        form = request.form.get('form')
        doz = request.form.get('doz')
        firma = request.form.get('firma')
        barkod = request.form.get('barkod')
        
        # Reçete bilgileri
        doktor_id = request.form.get('doktor_id')
        hastane = request.form.get('hastane')
        baslangic_tarihi = datetime.strptime(request.form.get('baslangic_tarihi'), '%Y-%m-%d')
        bitis_tarihi = datetime.strptime(request.form.get('bitis_tarihi'), '%Y-%m-%d')
        dozaj = request.form.get('dozaj')
        kullanim_sekli = request.form.get('kullanim_sekli')
        notlar = request.form.get('notlar')
        
        # İlaç oluştur
        medicine = Medicine(
            ad=ad,
            etken_madde=etken_madde,
            form=form,
            doz=doz,
            firma=firma,
            barkod=barkod
        )
        db.session.add(medicine)
        db.session.flush()  # ID almak için flush
        
        # Reçete oluştur
        prescription = Prescription(
            hasta_id=current_user.id,
            ilac_id=medicine.id,
            doktor_id=doktor_id,
            hastane=hastane,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            dozaj=dozaj,
            kullanim_sekli=kullanim_sekli,
            notlar=notlar
        )
        db.session.add(prescription)
        
        # Hatırlatıcı oluştur
        if 'hatirlatici' in request.form:
            zaman = datetime.strptime(request.form.get('hatirlatici_zaman'), '%H:%M')
            gunler = request.form.getlist('hatirlatici_gunler')
            bildirim_tipi = request.form.get('bildirim_tipi')
            bildirim_oncesi = int(request.form.get('bildirim_oncesi', 0))
            
            reminder = Reminder(
                kullanici_id=current_user.id,
                ilac_id=medicine.id,
                recete_id=prescription.id,
                zaman=zaman,
                gunler=','.join(gunler),
                bildirim_tipi=bildirim_tipi,
                bildirim_oncesi=bildirim_oncesi,
                aktif=True
            )
            db.session.add(reminder)
        
        db.session.commit()
        flash('İlaç başarıyla eklendi!', 'success')
        return redirect(url_for('medicine.view', id=medicine.id))
    
    return render_template('medicine/add.html')

@medicine.route('/ilac/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def edit(id):
    medicine = Medicine.query.get_or_404(id)
    prescription = Prescription.query.filter_by(
        hasta_id=current_user.id,
        ilac_id=id
    ).first_or_404()
    
    if request.method == 'POST':
        # İlaç bilgilerini güncelle
        medicine.ad = request.form.get('ad')
        medicine.etken_madde = request.form.get('etken_madde')
        medicine.form = request.form.get('form')
        medicine.doz = request.form.get('doz')
        medicine.firma = request.form.get('firma')
        medicine.barkod = request.form.get('barkod')
        
        # Reçete bilgilerini güncelle
        prescription.doktor_id = request.form.get('doktor_id')
        prescription.hastane = request.form.get('hastane')
        prescription.baslangic_tarihi = datetime.strptime(request.form.get('baslangic_tarihi'), '%Y-%m-%d')
        prescription.bitis_tarihi = datetime.strptime(request.form.get('bitis_tarihi'), '%Y-%m-%d')
        prescription.dozaj = request.form.get('dozaj')
        prescription.kullanim_sekli = request.form.get('kullanim_sekli')
        prescription.notlar = request.form.get('notlar')
        
        db.session.commit()
        flash('İlaç bilgileri güncellendi!', 'success')
        return redirect(url_for('medicine.view', id=id))
    
    return render_template('medicine/edit.html',
                         medicine=medicine,
                         prescription=prescription)

@medicine.route('/ilac/<int:id>/sil')
@login_required
def delete(id):
    medicine = Medicine.query.get_or_404(id)
    prescription = Prescription.query.filter_by(
        hasta_id=current_user.id,
        ilac_id=id
    ).first_or_404()
    
    # İlacı ve reçeteyi sil
    db.session.delete(prescription)
    db.session.delete(medicine)
    db.session.commit()
    
    flash('İlaç başarıyla silindi!', 'success')
    return redirect(url_for('medicine.list'))

@medicine.route('/hatirlatici/kaydet', methods=['POST'])
@login_required
def log_reminder():
    reminder_id = request.form.get('reminder_id')
    durum = request.form.get('durum')
    notlar = request.form.get('notlar')
    
    log = ReminderLog(
        hatirlatici_id=reminder_id,
        tarih=datetime.now(),
        durum=durum,
        notlar=notlar
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@medicine.route('/hatirlatici/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def edit_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    
    if request.method == 'POST':
        reminder.zaman = datetime.strptime(request.form.get('zaman'), '%H:%M')
        reminder.gunler = ','.join(request.form.getlist('gunler'))
        reminder.bildirim_tipi = request.form.get('bildirim_tipi')
        reminder.bildirim_oncesi = int(request.form.get('bildirim_oncesi', 0))
        reminder.aktif = 'aktif' in request.form
        
        db.session.commit()
        flash('Hatırlatıcı güncellendi!', 'success')
        return redirect(url_for('medicine.view', id=reminder.ilac_id))
    
    return render_template('medicine/edit_reminder.html', reminder=reminder) 
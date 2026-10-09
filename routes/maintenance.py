from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.maintenance import PreventiveMaintenance
from models.mesin import Mesin
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/maintenance', methods=['GET', 'POST'])
@login_required
def kelola_pm():
    if current_user.role not in ['ASTEK', 'MASKep']:
        flash('Anda tidak memiliki akses ke halaman Preventive Maintenance.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    if request.method == 'POST' and current_user.role == 'ASTEK':
        mesin_id = request.form.get('mesin_id')
        tanggal_str = request.form.get('jadwal_maintenance')
        keterangan = request.form.get('keterangan')
        
        jadwal = datetime.strptime(tanggal_str, '%Y-%m-%d')
        
        new_pm = PreventiveMaintenance(
            mesin_id=mesin_id,
            jadwal_maintenance=jadwal,
            keterangan=keterangan,
            status='TERJADWAL'
        )
        db.session.add(new_pm)
        db.session.commit()
        
        flash('Jadwal Preventive Maintenance berhasil ditambahkan!', 'success')
        return redirect(url_for('maintenance.kelola_pm'))
        
    mesin_list = Mesin.query.all()
    pm_list = PreventiveMaintenance.query.all()
    return render_template('maintenance/pm.html', mesin_list=mesin_list, pm_list=pm_list)
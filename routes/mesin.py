import csv
import io
from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from flask_login import login_required, current_user
from extensions import db
from models.mesin import Mesin

# Deklarasi Blueprint di paling atas
mesin_bp = Blueprint('mesin', __name__)

@mesin_bp.route('/mesin', methods=['GET'])
@login_required
def daftar_mesin():
    mesin_list = Mesin.query.all()
    return render_template('mesin/daftar_mesin.html', mesin_list=mesin_list)

@mesin_bp.route('/mesin/tambah', methods=['POST'])
@login_required
def tambah_mesin():
    if current_user.role not in ['Pengadaan', 'MASKep', 'ASTEK']:
        flash('Anda tidak memiliki hak akses untuk menambah data mesin.', 'danger')
        return redirect(url_for('mesin.daftar_mesin'))
        
    kode_mesin = request.form.get('kode_mesin')
    nama_mesin = request.form.get('nama_mesin')
    lokasi = request.form.get('lokasi', 'Pabrik Utama')
    
    if kode_mesin and nama_mesin:
        existing = Mesin.query.filter_by(kode_mesin=kode_mesin).first()
        if existing:
            flash('Kode mesin tersebut sudah terdaftar di sistem.', 'warning')
        else:
            new_mesin = Mesin(
                kode_mesin=kode_mesin,
                nama_mesin=nama_mesin,
                lokasi=lokasi,
                status_operasional='Normal'
            )
            db.session.add(new_mesin)
            db.session.commit()
            flash('Data mesin baru berhasil ditambahkan!', 'success')
            
    return redirect(url_for('mesin.daftar_mesin'))

@mesin_bp.route('/mesin/impor', methods=['POST'])
@login_required
def impor_mesin():
    if current_user.role not in ['Pengadaan', 'MASKep', 'ASTEK']:
        flash('Anda tidak memiliki hak akses.', 'danger')
        return redirect(url_for('mesin.daftar_mesin'))
        
    file = request.files.get('file_excel')
    if not file or file.filename == '':
        flash('Pilih file CSV terlebih dahulu.', 'danger')
        return redirect(url_for('mesin.daftar_mesin'))
        
    try:
        stream = io.TextIOWrapper(file.stream, encoding='utf-8')
        csv_reader = csv.DictReader(stream)
        count = 0
        for row in csv_reader:
            kode_mesin = row.get('kode_mesin')
            nama_mesin = row.get('nama_mesin')
            lokasi = row.get('lokasi', 'Pabrik Utama')
            if kode_mesin and nama_mesin:
                existing = Mesin.query.filter_by(kode_mesin=kode_mesin).first()
                if not existing:
                    db.session.add(Mesin(
                        kode_mesin=kode_mesin,
                        nama_mesin=nama_mesin,
                        lokasi=lokasi,
                        status_operasional='Normal'
                    ))
                    count += 1
        db.session.commit()
        flash(f'Berhasil mengimpor {count} data mesin dari CSV!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal mengimpor file: {str(e)}', 'danger')
        
    return redirect(url_for('mesin.daftar_mesin'))

@mesin_bp.route('/mesin/ekspor', methods=['GET'])
@login_required
def ekspor_mesin():
    mesin_list = Mesin.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Kode Mesin', 'Nama Mesin', 'Lokasi', 'Status Operasional'])
    for m in mesin_list:
        writer.writerow([m.id, m.kode_mesin, m.nama_mesin, m.lokasi, m.status_operasional])
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=data_mesin_pabrik.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response
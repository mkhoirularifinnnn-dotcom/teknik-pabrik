import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.laporan import LaporanKerusakan
from models.mesin import Mesin
from models.barang import Barang, KebutuhanBarang, TransaksiGudang

laporan_bp = Blueprint('laporan', __name__)

@laporan_bp.route('/laporan', methods=['GET'])
@login_required
def daftar_laporan():
    mesin_id = request.args.get('mesin_id')
    status = request.args.get('status')
    tanggal_mulai = request.args.get('tanggal_mulai')
    tanggal_selesai = request.args.get('tanggal_selesai')
    
    query = LaporanKerusakan.query
    if mesin_id:
        query = query.filter_by(mesin_id=int(mesin_id))
    if status:
        query = query.filter_by(status=status)
    if tanggal_mulai:
        query = query.filter(LaporanKerusakan.tanggal_laporan >= tanggal_mulai)
    if tanggal_selesai:
        query = query.filter(LaporanKerusakan.tanggal_laporan <= tanggal_selesai)
        
    laporan_list = query.order_by(LaporanKerusakan.id.desc()).all()
    mesin_list = Mesin.query.all()
    
    return render_template('laporan/daftar_laporan.html', 
                           laporan_list=laporan_list, 
                           mesin_list=mesin_list,
                           selected_mesin=mesin_id,
                           selected_status=status,
                           selected_mulai=tanggal_mulai,
                           selected_selesai=tanggal_selesai)

@laporan_bp.route('/laporan/tambah', methods=['GET', 'POST'])
@login_required
def buat_laporan():
    if current_user.role not in ['ASTEK', 'Asisten Pengolahan']:
        flash('Anda tidak memiliki izin untuk membuat laporan kerusakan.', 'danger')
        return redirect(url_for('laporan.daftar_laporan'))
        
    if request.method == 'POST':
        mesin_id = request.form.get('mesin_id')
        lokasi_pabrik = request.form.get('lokasi_pabrik')
        tanggal_str = request.form.get('tanggal_laporan')
        deskripsi = request.form.get('deskripsi')
        file_bukti = request.files.get('foto_bukti')
        
        if not tanggal_str or not deskripsi or not mesin_id or not lokasi_pabrik:
            flash('Semua kolom wajib diisi (Lokasi Pabrik, Mesin, Tanggal, dan Deskripsi)!', 'danger')
            return redirect(url_for('laporan.buat_laporan'))
            
        try:
            tanggal_laporan = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal tidak valid.', 'danger')
            return redirect(url_for('laporan.buat_laporan'))
            
        mesin_obj = Mesin.query.get(int(mesin_id))
        if mesin_obj:
            mesin_obj.lokasi = lokasi_pabrik
            
        filename = None
        if file_bukti and file_bukti.filename != '':
            original_filename = secure_filename(file_bukti.filename)
            filename = f"{uuid.uuid4().hex[:8]}_{original_filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_bukti.save(os.path.join(upload_folder, filename))
            
        nomor_laporan = f"LP-{uuid.uuid4().hex[:6].upper()}"
        
        new_laporan = LaporanKerusakan(
            nomor_laporan=nomor_laporan,
            mesin_id=int(mesin_id),
            tanggal_laporan=tanggal_laporan,
            deskripsi=deskripsi,
            foto_bukti=filename,
            status='PENDING'
        )
        db.session.add(new_laporan)
        db.session.commit()
        
        flash('Laporan kerusakan beserta lokasi pabrik berhasil dikirim!', 'success')
        return redirect(url_for('laporan.daftar_laporan'))
        
    mesin_list = Mesin.query.all()
    return render_template('laporan/buat_laporan.html', mesin_list=mesin_list)

@laporan_bp.route('/laporan/tindak-lanjut/<int:laporan_id>', methods=['GET', 'POST'])
@login_required
def tindak_lanjut_laporan(laporan_id):
    if current_user.role != 'ASTEK':
        flash('Hanya ASTEK yang dapat melakukan tindak lanjut perbaikan.', 'danger')
        return redirect(url_for('laporan.daftar_laporan'))
        
    laporan = LaporanKerusakan.query.get_or_404(laporan_id)
    lokasi_mesin = laporan.mesin.lokasi if laporan.mesin else 'Sedep'

    barang_list = Barang.query.filter_by(gudang_pabrik=lokasi_mesin).all()
    
    if request.method == 'POST':
        aksi = request.form.get('aksi')
        
        if aksi == 'tambah_kebutuhan':
            nama_barang_manual = request.form.get('nama_barang_manual')
            jumlah_diminta = request.form.get('jumlah_diminta')
            satuan = request.form.get('satuan', 'Pcs')
            
            if nama_barang_manual and jumlah_diminta:
                jml_minta = int(jumlah_diminta)
                
                # Cari barang di gudang pabrik yang sesuai lokasi mesin
                barang_terdaftar = Barang.query.filter(
                    Barang.gudang_pabrik == lokasi_mesin,
                    Barang.nama_barang.ilike(f"%{nama_barang_manual}%")
                ).first()
                
                if barang_terdaftar:
                    barang_id = barang_terdaftar.id
                else:
                    new_barang_pengadaan = Barang(
                        nama_barang=nama_barang_manual, 
                        stok=0, 
                        satuan=satuan, 
                        gudang_pabrik=lokasi_mesin
                    )
                    db.session.add(new_barang_pengadaan)
                    db.session.flush()
                    barang_id = new_barang_pengadaan.id
                
                # Simpan kebutuhan dengan status 'MENUNGGU PERSETUJUAN' agar muncul di akun Pengadaan
                new_kebutuhan = KebutuhanBarang(
                    laporan_id=laporan.id,
                    barang_id=barang_id,
                    jumlah_diminta=jml_minta,
                    status_pengadaan='MENUNGGU PERSETUJUAN'
                )
                db.session.add(new_kebutuhan)
                db.session.commit()
                flash(f'Kebutuhan barang berhasil diajukan ke Pengadaan Gudang {lokasi_mesin}.', 'success')
                
        elif aksi == 'simpan_rencana':
            rencana_tgl_str = request.form.get('rencana_tanggal')
            if not rencana_tgl_str:
                flash('Tanggal rencana perbaikan wajib diisi.', 'danger')
                return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan.id))
                
            try:
                laporan.rencana_tanggal = datetime.strptime(rencana_tgl_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format tanggal rencana tidak valid.', 'danger')
                return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan.id))
                
            laporan.status = 'PROSES'
            db.session.commit()
            flash('Rencana tanggal perbaikan disimpan dan status laporan berubah menjadi PROSES!', 'success')
            
        elif aksi == 'selesaikan_perbaikan':
            # Pastikan seluruh kebutuhan barang sudah DISETUJUI oleh pengadaan
            belum_disetujui = any('DISETUJUI' not in k.status_pengadaan for k in laporan.kebutuhan_list)
            if belum_disetujui:
                flash('Perbaikan belum dapat diselesaikan karena masih ada barang yang belum disetujui (di-acc) oleh Pengadaan!', 'danger')
                return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan.id))
                
            realisasi_tgl_str = request.form.get('tanggal_realisasi')
            files_realisasi = request.files.getlist('dokumentasi_realisasi')
            
            if not realisasi_tgl_str:
                flash('Tanggal realisasi perbaikan wajib diisi.', 'danger')
                return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan.id))
                
            try:
                laporan.tanggal_realisasi = datetime.strptime(realisasi_tgl_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format tanggal realisasi tidak valid.', 'danger')
                return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan.id))

            uploaded_filenames = laporan.dokumentasi_realisasi.split(',') if laporan.dokumentasi_realisasi else []
            for file_realisasi in files_realisasi:
                if file_realisasi and file_realisasi.filename != '':
                    original_filename = secure_filename(file_realisasi.filename)
                    filename = f"tl_{uuid.uuid4().hex[:8]}_{original_filename}"
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_realisasi.save(os.path.join(upload_folder, filename))
                    uploaded_filenames.append(filename)
                    
            laporan.dokumentasi_realisasi = ",".join(uploaded_filenames) if uploaded_filenames else None
            laporan.status = 'SELESAI'
            
            db.session.commit()
            flash('Perbaikan berhasil direalisasikan dan status laporan menjadi SELESAI!', 'success')
            return redirect(url_for('laporan.daftar_laporan'))
            
        return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan.id))
        
    return render_template('laporan/tindak_lanjut.html', laporan=laporan, barang_list=barang_list, lokasi_mesin=lokasi_mesin)

@laporan_bp.route('/laporan/hapus-kebutuhan/<int:kebutuhan_id>', methods=['POST'])
@login_required
def hapus_kebutuhan(kebutuhan_id):
    if current_user.role != 'ASTEK':
        flash('Hanya ASTEK yang dapat menghapus data kebutuhan.', 'danger')
        return redirect(url_for('laporan.daftar_laporan'))
        
    kebutuhan = KebutuhanBarang.query.get_or_404(kebutuhan_id)
    laporan_id = kebutuhan.laporan_id
    
    try:
        db.session.delete(kebutuhan)
        db.session.commit()
        flash('Data kebutuhan barang berhasil dihapus.', 'success')
    except Exception:
        db.session.rollback()
        flash('Gagal menghapus data kebutuhan barang.', 'danger')
        
    return redirect(url_for('laporan.tindak_lanjut_laporan', laporan_id=laporan_id))

@laporan_bp.route('/laporan/status/<int:laporan_id>', methods=['POST'])
@login_required
def update_status(laporan_id):
    if current_user.role not in ['MASKep', 'ASTEK']:
        flash('Anda tidak memiliki izin untuk mengubah status laporan.', 'danger')
        return redirect(url_for('laporan.daftar_laporan'))
        
    laporan = LaporanKerusakan.query.get_or_404(laporan_id)
    status_baru = request.form.get('status')
    
    if status_baru in ['PENDING', 'PROSES', 'SELESAI']:
        laporan.status = status_baru
        db.session.commit()
        flash(f'Status laporan berhasil diperbarui menjadi {status_baru}!', 'success')
    else:
        flash('Status tidak valid.', 'danger')
        
    return redirect(url_for('laporan.daftar_laporan'))

@laporan_bp.route('/laporan/hapus/<int:laporan_id>', methods=['POST'])
@login_required
def hapus_laporan(laporan_id):
    if current_user.role not in ['MASKep', 'ASTEK']:
        flash('Anda tidak memiliki hak akses untuk menghapus laporan perbaikan.', 'danger')
        return redirect(url_for('laporan.daftar_laporan'))
        
    laporan = LaporanKerusakan.query.get_or_404(laporan_id)
    try:
        if laporan.foto_bukti:
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', laporan.foto_bukti)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(laporan)
        db.session.commit()
        flash('Data laporan perbaikan berhasil dihapus.', 'success')
    except Exception:
        db.session.rollback()
        flash('Gagal menghapus data.', 'danger')
        
    return redirect(url_for('laporan.daftar_laporan'))
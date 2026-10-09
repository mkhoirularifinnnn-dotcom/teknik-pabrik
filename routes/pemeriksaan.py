from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.laporan import LaporanKerusakan, PemeriksaanKerusakan
from models.barang import Barang, KebutuhanBarang

pemeriksaan_bp = Blueprint('pemeriksaan', __name__)

@pemeriksaan_bp.route('/pemeriksaan/<int:laporan_id>', methods=['GET', 'POST'])
@login_required
def proses_pemeriksaan(laporan_id):
    if current_user.role != 'ASTEK':
        flash('Hanya ASTEK yang dapat melakukan pemeriksaan kerusakan mesin.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    laporan = LaporanKerusakan.query.get_or_404(laporan_id)
    
    if request.method == 'POST':
        tindakan = request.form.get('tindakan_perbaikan')
        status_akhir = request.form.get('status_laporan') # DIPROSES, MENUNGGU_BARANG, SELESAI
        
        # Ambil inputan barang & jumlah dari form pengadaan
        barang_id = request.form.get('barang_id')
        jumlah_diminta = request.form.get('jumlah_diminta')
        
        # Cek apakah laporan sudah pernah diperiksa
        pemeriksaan_existing = PemeriksaanKerusakan.query.filter_by(laporan_id=laporan.id).first()
        
        if pemeriksaan_existing:
            pemeriksaan_existing.tindakan_perbaikan = tindakan
            pemeriksaan_existing.teknisi_id = current_user.id
        else:
            new_pemeriksaan = PemeriksaanKerusakan(
                laporan_id=laporan.id,
                teknisi_id=current_user.id,
                tindakan_perbaikan=tindakan
            )
            db.session.add(new_pemeriksaan)
            
        # Jika ASTEK memilih barang untuk diajukan pengadaannya
        if barang_id and jumlah_diminta and int(jumlah_diminta) > 0:
            new_kebutuhan = KebutuhanBarang(
                laporan_id=laporan.id,
                barang_id=int(barang_id),
                jumlah_diminta=int(jumlah_diminta),
                status_pengadaan='MENGAJUKAN'
            )
            db.session.add(new_kebutuhan)
            status_akhir = 'MENUNGGU_BARANG'
            
        # Update status pada laporan utama
        laporan.status = status_akhir
        db.session.commit()
        
        flash('Data pemeriksaan dan pengajuan kebutuhan barang berhasil disimpan!', 'success')
        return redirect(url_for('laporan.daftar_laporan'))
        
    # Ambil daftar barang/sparepart untuk pilihan di form HTML
    barang_list = Barang.query.all()
    return render_template('laporan/pemeriksaan.html', laporan=laporan, barang_list=barang_list)
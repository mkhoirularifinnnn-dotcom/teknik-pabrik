from extensions import db
from datetime import datetime

class PreventiveMaintenance(db.Model):
    __tablename__ = 'preventive_maintenance'
    id = db.Column(db.Integer, primary_key=True)
    mesin_id = db.Column(db.Integer, db.ForeignKey('mesin.id'), nullable=False)
    jadwal_maintenance = db.Column(db.DateTime, nullable=False)
    keterangan = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='TERJADWAL') # TERJADWAL, SELESAI

    mesin = db.relationship('Mesin', backref='pm_list', lazy=True)
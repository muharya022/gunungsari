from django.db import models

class Fasilitas(models.Model):
    nama = models.CharField(max_length=100)
    lokasi = models.CharField(max_length=200)
    kapasitas = models.IntegerField()
    foto = models.ImageField(upload_to='fasilitas/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.nama


class Kegiatan(models.Model):
    nama_kegiatan = models.CharField(max_length=100)
    tanggal = models.DateField()
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()
    fasilitas = models.ManyToManyField(Fasilitas)
    penanggung_jawab = models.CharField(max_length=100)

class PermohonanPeminjaman(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    nama_pemohon = models.CharField(max_length=255)
    alamat = models.CharField(max_length=500)
    no_telepon = models.CharField(max_length=20)
    email_pemohon = models.EmailField()
    fasilitas_dipinjam = models.CharField(max_length=100)
    tanggal_peminjaman = models.DateField()
    waktu_mulai = models.TimeField()
    waktu_selesai = models.TimeField()
    keperluan = models.TextField()
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    catatan = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama_pemohon} - {self.fasilitas_dipinjam} ({self.tanggal_peminjaman})"

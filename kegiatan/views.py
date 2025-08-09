from django.shortcuts import render, redirect
from .models import Fasilitas, Kegiatan
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Selamat datang, {user.username}!")
            return redirect('index')  # Redirect ke halaman utama setelah login sukses
        else:
            messages.error(request, "Username atau password salah.")
            return render(request, 'index.html', {'logged_in': False})

    else:
        return redirect('index')  # kalau akses GET langsung ke home

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect('index')


def index(request):
    fasilitas_qs = Fasilitas.objects.all()
    # Buat list dict sesuai properti yang diperlukan di JS
    fasilitas_list = []
    for f in fasilitas_qs:
        fasilitas_list.append({
            'id': f.id,
            'nama': f.nama,
            'lokasi': f.lokasi,
            'latitude': f.latitude,
            'longitude': f.longitude,
        })

    context = {
        'fasilitas_list': fasilitas_list,
    }
    return render(request, 'index.html', context)

def fasilitas_list(request):
    fasilitas = Fasilitas.objects.all()
    return render(request, 'fasilitas_list.html', {'fasilitas': fasilitas})

def fasilitas_detail(request, id):
    fasilitas = get_object_or_404(Fasilitas, id=id)
    return render(request, 'fasilitas_detail.html', {'fasilitas': fasilitas})

def jadwal_list(request):
    jadwal = Kegiatan.objects.all().order_by('tanggal', 'jam_mulai')
    return render(request, 'jadwal_list.html', {'jadwal': jadwal})

from django.shortcuts import render, redirect
from .models import Fasilitas
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_view')
def tambah_fasilitas(request):
    if request.method == 'POST':
        nama = request.POST['nama']
        lokasi = request.POST['lokasi']
        kapasitas = request.POST['kapasitas']
        foto = request.FILES.get('foto')
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']

        fasilitas = Fasilitas(
            nama=nama,
            lokasi=lokasi,
            kapasitas=kapasitas,
            foto=foto,
            latitude=latitude,
            longitude=longitude
        )
        fasilitas.save()
        return redirect('fasilitas_list')
    return render(request, 'tambah_fasilitas.html')

@login_required(login_url='login_view')
def tambah_jadwal(request):
    fasilitas = Fasilitas.objects.all()
    if request.method == 'POST':
        nama_kegiatan = request.POST['nama_kegiatan']
        tanggal = request.POST['tanggal']
        jam_mulai = request.POST['jam_mulai']
        jam_selesai = request.POST['jam_selesai']
        fasilitas_ids = request.POST.getlist('fasilitas')  # ambil list fasilitas yg dipilih
        penanggung_jawab = request.POST['penanggung_jawab']

        kegiatan = Kegiatan.objects.create(
            nama_kegiatan=nama_kegiatan,
            tanggal=tanggal,
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai,
            penanggung_jawab=penanggung_jawab
        )
        kegiatan.fasilitas.set(fasilitas_ids)  # simpan ManyToMany
        kegiatan.save()
        return redirect('jadwal_list')

    return render(request, 'tambah_jadwal.html', {'fasilitas': fasilitas})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Fasilitas, Kegiatan

# Hapus Fasilitas
@login_required(login_url='login_view')
def hapus_fasilitas(request, id):
    fasilitas = get_object_or_404(Fasilitas, id=id)
    fasilitas.delete()
    messages.success(request, "Fasilitas berhasil dihapus.")
    return redirect('fasilitas_list')

# Hapus Jadwal
@login_required(login_url='login_view')
def hapus_jadwal(request, id):
    jadwal = get_object_or_404(Kegiatan, id=id)
    jadwal.delete()
    messages.success(request, "Jadwal berhasil dihapus.")
    return redirect('jadwal_list')


def jadwal_api(request):
    events = []
    jadwal = Kegiatan.objects.all()
    for j in jadwal:
        fasilitas_nama = ", ".join([f.nama for f in j.fasilitas.all()])
        events.append({
            'title': f"{j.nama_kegiatan} - {fasilitas_nama}",
            'start': f"{j.tanggal}T{j.jam_mulai}",
            'end': f"{j.tanggal}T{j.jam_selesai}",
        })
    return JsonResponse(events, safe=False)


from django.http import JsonResponse
from .models import Kegiatan

def jadwal_events(request):
    events = []
    for j in Kegiatan.objects.all():
        events.append({
            "title": j.nama_kegiatan,
            "start": f"{j.tanggal}T{j.jam_mulai}",
            "end": f"{j.tanggal}T{j.jam_selesai}",
            "url": f"/jadwal_list/{j.id}/" 
        })
    return JsonResponse(events, safe=False)

def jadwal_detail(request, id):
    kegiatan = get_object_or_404(Kegiatan, id=id)
    return render(request, 'jadwal_detail.html', {'kegiatan': kegiatan})

from .models import Fasilitas
from django.contrib import messages
from .models import PermohonanPeminjaman

def permohonan_peminjaman_form(request):
    fasilitas_list = Fasilitas.objects.all()

    if request.method == 'POST':
        nama_pemohon = request.POST.get('nama_pemohon')
        alamat = request.POST.get('alamat')
        no_telepon = request.POST.get('no_telepon')
        fasilitas_dipinjam = request.POST.get('fasilitas_dipinjam')
        tanggal_peminjaman = request.POST.get('tanggal_peminjaman')
        waktu_mulai = request.POST.get('waktu_mulai')
        waktu_selesai = request.POST.get('waktu_selesai')
        keperluan = request.POST.get('keperluan')

        # Validasi sederhana, bisa kamu tambah
        if not all([nama_pemohon, alamat, no_telepon, fasilitas_dipinjam, tanggal_peminjaman, waktu_mulai, waktu_selesai, keperluan]):
            messages.error(request, "Semua kolom wajib diisi.")
            return render(request, 'permohonan.html', {'fasilitas_list': fasilitas_list})

        # Simpan data ke database
        permohonan = PermohonanPeminjaman(
            nama_pemohon=nama_pemohon,
            alamat=alamat,
            no_telepon=no_telepon,
            fasilitas_dipinjam=fasilitas_dipinjam,
            tanggal_peminjaman=tanggal_peminjaman,
            waktu_mulai=waktu_mulai,
            waktu_selesai=waktu_selesai,
            keperluan=keperluan,
        )
        permohonan.save()
        # tambahkan pesan sukses
        messages.success(request, "Permohonan berhasil dikirim! Silakan tunggu persetujuan dari admin.")
        return redirect('jadwal_list')

    # Jika GET, tampilkan form kosong dengan daftar fasilitas
    return render(request, 'permohonan.html', {'fasilitas_list': fasilitas_list})

from django.http import JsonResponse
from .models import Fasilitas

def fasilitas_json(request):
    fasilitas = Fasilitas.objects.all()
    data = []
    for f in fasilitas:
        data.append({
            'nama': f.nama,
            'latitude': f.latitude,
            'longitude': f.longitude,
            'kapasitas': f.kapasitas,
            # Kalau mau kirim foto juga bisa tambahkan URL-nya, misal:
            'foto_url': f.foto.url if f.foto else '',
        })
    return JsonResponse(data, safe=False)

from django.shortcuts import render, get_object_or_404, redirect
from .models import PermohonanPeminjaman, Kegiatan, Fasilitas

def daftar_persetujuan(request):
    permohonan_list = PermohonanPeminjaman.objects.filter(status="menunggu")
    return render(request, "persetujuan_list.html", {"permohonan_list": permohonan_list})

def persetujuan_detail(request, pk):
    permohonan = get_object_or_404(PermohonanPeminjaman, pk=pk)

    if request.method == "POST":
        status = request.POST.get("status")
        catatan = request.POST.get("catatan", "")

        permohonan.status = status
        permohonan.catatan = catatan
        permohonan.save()

        if status == "disetujui":
            kegiatan = Kegiatan.objects.create(
                nama_kegiatan=permohonan.keperluan,
                tanggal=permohonan.tanggal_peminjaman,
                jam_mulai=permohonan.waktu_mulai,
                jam_selesai=permohonan.waktu_selesai,
                penanggung_jawab=permohonan.nama_pemohon
            )
            fasilitas_obj = Fasilitas.objects.filter(nama=permohonan.fasilitas_dipinjam)
            if fasilitas_obj.exists():
                kegiatan.fasilitas.set(fasilitas_obj)

        return redirect("daftar_persetujuan")

    return render(request, "persetujuan_detail.html", {"permohonan": permohonan})

from django.contrib import messages

def setujui_permohonan(request, id):
    # logika setujui
    messages.success(request, "Permohonan berhasil disetujui dan masuk ke jadwal.")
    return redirect('daftar_persetujuan')

def tolak_permohonan(request, id):
    # logika tolak
    messages.error(request, "Permohonan ditolak dan tidak akan masuk ke jadwal.")
    return redirect('daftar_persetujuan')

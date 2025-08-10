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
    messages.success(request, f"Selamat tinggal, Admin!")
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
        messages.success(request, f"Berhasil menambah fasilitas!")
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

from .models import Fasilitas, PermohonanPeminjaman
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect

# Import SDK
from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailTo

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
        email_pemohon = request.POST.get('email_pemohon')

        if not all([nama_pemohon, alamat, no_telepon, fasilitas_dipinjam, tanggal_peminjaman, waktu_mulai, waktu_selesai, keperluan, email_pemohon]):
            messages.error(request, "Semua kolom wajib diisi.")
            return render(request, 'permohonan.html', {'fasilitas_list': fasilitas_list})

        permohonan = PermohonanPeminjaman(
            nama_pemohon=nama_pemohon,
            alamat=alamat,
            no_telepon=no_telepon,
            fasilitas_dipinjam=fasilitas_dipinjam,
            tanggal_peminjaman=tanggal_peminjaman,
            waktu_mulai=waktu_mulai,
            waktu_selesai=waktu_selesai,
            keperluan=keperluan,
            email_pemohon=email_pemohon,
        )
        permohonan.save()

        # Kirim email pakai API Brevo
        configuration = Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        api_instance = TransactionalEmailsApi(ApiClient(configuration))

        subject = "Konfirmasi Permohonan Peminjaman Fasilitas"
        html_content = f"""
        <p>Halo {nama_pemohon},</p>
        <p>Permohonan peminjaman fasilitas <b>{fasilitas_dipinjam}</b> Anda telah kami terima.<br/>
        Silakan tunggu informasi selanjutnya dari admin.</p>
        <p>Terima kasih.</p>
        """

        send_smtp_email = SendSmtpEmail(
            to=[SendSmtpEmailTo(email=email_pemohon, name=nama_pemohon)],
            sender={'email': settings.EMAIL_HOST_USER, 'name': 'Admin Fasilitas'},
            subject=subject,
            html_content=html_content
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
        except Exception as e:
            messages.error(request, f"Gagal mengirim email: {e}")
            return render(request, 'permohonan.html', {'fasilitas_list': fasilitas_list})

        messages.success(request, "Permohonan berhasil dikirim! Silakan cek email Anda untuk konfirmasi.")
        return redirect('jadwal_list')

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
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

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

        # Jika disetujui, buat jadwal kegiatan dan set fasilitas
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

        # Kirim email notifikasi sesuai status
        kirim_notifikasi_email(permohonan)

        messages.success(request, f"Permohonan berhasil {status}. Email notifikasi telah dikirim.")
        return redirect("daftar_persetujuan")

    return render(request, "persetujuan_detail.html", {"permohonan": permohonan})

from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailTo
from django.conf import settings

def kirim_notifikasi_email(permohonan):
    configuration = Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    api_instance = TransactionalEmailsApi(ApiClient(configuration))

    if permohonan.status == "disetujui":
        subject = 'Permohonan Anda Telah Disetujui'
        html_content = f"""
        <p>Halo {permohonan.nama_pemohon},</p>
        <p>Permohonan dengan ID <b>{permohonan.id}</b> untuk fasilitas "<b>{permohonan.fasilitas_dipinjam}</b>" telah disetujui oleh admin.</p>
        <p>Catatan: {permohonan.catatan}</p>
        <p>Terima kasih.</p>
        """
    elif permohonan.status == "ditolak":
        subject = 'Permohonan Anda Ditolak'
        html_content = f"""
        <p>Halo {permohonan.nama_pemohon},</p>
        <p>Mohon maaf, permohonan dengan ID <b>{permohonan.id}</b> untuk fasilitas "<b>{permohonan.fasilitas_dipinjam}</b>" telah ditolak oleh admin.</p>
        <p>Catatan: {permohonan.catatan}</p>
        <p>Jika ada pertanyaan, silakan hubungi admin.</p>
        <p>Terima kasih.</p>
        """
    else:
        return  # Jangan kirim email jika status lain

    send_smtp_email = SendSmtpEmail(
        to=[SendSmtpEmailTo(email=permohonan.email_pemohon, name=permohonan.nama_pemohon)],
        sender={'email': settings.EMAIL_HOST_USER, 'name': 'Admin Fasilitas Desa Gunung Sari'},
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except Exception as e:
        # Bisa juga kamu log error ini ke file log atau database
        print(f"Error mengirim email notifikasi: {e}")

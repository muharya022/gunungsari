from django.urls import path
from . import views
from .views import login_view, logout_view

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    path('fasilitas/', views.fasilitas_list, name='fasilitas_list'),
    path('fasilitas_list/', views.fasilitas_list, name='fasilitas_list'),
    path('fasilitas/<int:id>/', views.fasilitas_detail, name='fasilitas_detail'),
    path('jadwal/', views.jadwal_list, name='jadwal_list'),
    path('jadwal_list/<int:id>/', views.jadwal_detail, name='jadwal_detail'),
    path('jadwal/api/', views.jadwal_api, name='jadwal_api'),
    path('fasilitas/tambah/', views.tambah_fasilitas, name='tambah_fasilitas'),
    path('jadwal/tambah/', views.tambah_jadwal, name='tambah_jadwal'),
    path('events/', views.jadwal_events, name='jadwal_events'),
    path('fasilitas/hapus/<int:id>/', views.hapus_fasilitas, name='hapus_fasilitas'),
    path('jadwal/delete/<int:id>/', views.hapus_jadwal, name='hapus_jadwal'),
    path('permohonan/', views.permohonan_peminjaman_form, name='permohonan_peminjaman_submit'),
    path('api/fasilitas/', views.fasilitas_json, name='fasilitas-json'),
    path("persetujuan/", views.daftar_persetujuan, name="daftar_persetujuan"),
    path("persetujuan/<int:pk>/", views.persetujuan_detail, name="persetujuan_detail"),
]

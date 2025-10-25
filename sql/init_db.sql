_-- ------------------------------------------------
-- SafeKampüs Projesi - Veritabanı Başlangıç Dosyası
-- Veritabanı: safekampus_db
-- Kullanıcı: safekampus_user
-- ------------------------------------------------

-- Eğer tablo varsa sil
DROP TABLE IF EXISTS olaylar CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS security_staff CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS chats CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;
DROP TABLE IF EXISTS map_locations CASCADE;

-- -----------------------------
-- Kullanıcılar Tablosu
-- -----------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    isim VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    sifre VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Güvenlik Personeli Tablosu
-- -----------------------------
CREATE TABLE security_staff (
    id SERIAL PRIMARY KEY,
    isim VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    sifre VARCHAR(150) NOT NULL,
    telefon VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Olaylar Tablosu
-- -----------------------------
CREATE TABLE olaylar (
    id SERIAL PRIMARY KEY,
    olay_turu VARCHAR(100) NOT NULL,
    konum VARCHAR(150) NOT NULL,
    aciklama TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Duyurular Tablosu
-- -----------------------------
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    baslik VARCHAR(150) NOT NULL,
    icerik TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Bildirimler Tablosu
-- -----------------------------
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    mesaj TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Sohbet Tablosu
-- -----------------------------
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INT REFERENCES users(id) ON DELETE CASCADE,
    mesaj TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Harita Konumları Tablosu
-- -----------------------------
CREATE TABLE map_locations (
    id SERIAL PRIMARY KEY,
    isim VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    aciklama TEXT
);

-- ------------------------------------------------
-- Örnek veri eklemek istersen buraya INSERT komutları yazabilirsin
-- ------------------------------------------------

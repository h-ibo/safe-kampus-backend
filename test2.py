from app.utils.faiss_store import search

def hafizayi_sorgula(soru):
    print(f"\n🤔 Kullanıcı Sorusu: {soru}")
    sonuclar = search(soru, k=3) # En alakalı 3 parçayı getir
    
    if not sonuclar:
        print("❌ Üzgünüm, hafızada bu konuyla ilgili bir bilgi bulamadım.")
    else:
        print("✅ Bulunan alakalı bilgiler:")
        for i, metin in enumerate(sonuclar):
            print(f"\n[{i+1}] {metin[:250]}...") # İlk 250 karakteri göster

if __name__ == "__main__":
    # Harran Üniversitesi ile ilgili bildiği şeyleri soralım
    hafizayi_sorgula("Harran Üniversitesi nerede?")
    hafizayi_sorgula("Yemekhane veya öğrenci işleri hakkında bilgi var mı?")
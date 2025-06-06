import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto


# Leksikal kategoriler
class LeksikolTip(Enum):
    REZERVE_KELIME = auto()
    DEGISKEN_ADI = auto()
    NUMERIK_DEGER = auto()
    ISLEMCI = auto()
    DIZGI = auto()
    TEK_KARAKTER = auto()
    ACIKLAMA = auto()
    ONISLEMCI_KOMUT = auto()
    AYRAC = auto()
    BOSALAN = auto()


# Leksikal birim özelliklerini saklayan veri yapısı  
@dataclass
class LeksikolBirim:
    baslama_indeks: int          # Leksikal birimin kaynak metindeki başlangıç noktası
    bitis_indeks: int            # Leksikal birimin kaynak metindeki son konumu
    kategori: LeksikolTip        # Leksikal birimin kategorik sınıflandırması
    icerik: str                  # Leksikal birimin gerçek metin değeri


# Sözdizimi renklendirme işlemlerini yürüten merkezi sınıf
class SozdizimRenklendiricisi:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.leksikal_birimler = []
        
        # C programlama dilinin ayrılmış sözcük koleksiyonu
        self.rezerveSozcukler = [
            "auto", "break", "case", "char", "const", "continue", "default", "do",
            "double", "else", "enum", "extern", "float", "for", "goto", "if",
            "int", "long", "register", "return", "short", "signed", "sizeof", 
            "static", "struct", "switch", "typedef", "union", "unsigned", "void",
            "volatile", "while"
        ]
        
        # Düzenli ifade kalıpları ile leksikal kategorilerin eşleştirilmesi
        self.kalip_listesi = [
            (LeksikolTip.ACIKLAMA, r'//[^\n]*|/\*[\s\S]*?\*/'),
            (LeksikolTip.ONISLEMCI_KOMUT, r'#\s*\w+.*'),
            (LeksikolTip.DIZGI, r'"(?:[^"\\]|\\.)*"'),
            (LeksikolTip.TEK_KARAKTER, r"'(?:[^'\\]|\\.)'"),
            (LeksikolTip.REZERVE_KELIME, r'\b(' + '|'.join(self.rezerveSozcukler) + r')\b'),
            (LeksikolTip.NUMERIK_DEGER, r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b'),
            (LeksikolTip.ISLEMCI, r'(==|!=|<=|>=|&&|\|\||<<|>>|\+\+|--|[+\-*/%=<>!&|^~]|\?|:)'),
            (LeksikolTip.AYRAC, r'[(){}\[\];,.]'),
            (LeksikolTip.DEGISKEN_ADI, r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            (LeksikolTip.BOSALAN, r'\s+'),
        ]
        
        # Leksikal kategoriler için görsel stil tanımlamaları
        self.stil_haritasi = {
            LeksikolTip.REZERVE_KELIME: {"foreground": "blue", "font": ("Courier", 12, "bold")},
            LeksikolTip.DEGISKEN_ADI: {"foreground": "black", "font": ("Courier", 12, "normal")},
            LeksikolTip.NUMERIK_DEGER: {"foreground": "red", "font": ("Courier", 12, "normal")},
            LeksikolTip.ISLEMCI: {"foreground": "purple", "font": ("Courier", 12, "normal")},
            LeksikolTip.DIZGI: {"foreground": "green", "font": ("Courier", 12, "normal")},
            LeksikolTip.TEK_KARAKTER: {"foreground": "orange", "font": ("Courier", 12, "normal")},
            LeksikolTip.ACIKLAMA: {"foreground": "gray", "font": ("Courier", 12, "italic")},
            LeksikolTip.ONISLEMCI_KOMUT: {"foreground": "darkred", "font": ("Courier", 12, "bold")},
            LeksikolTip.AYRAC: {"foreground": "brown", "font": ("Courier", 12, "normal")},
            LeksikolTip.BOSALAN: {"foreground": "black", "font": ("Courier", 12, "normal")}
        }
        
        # Stilendirme etiketlerini hazırla
        self._etiketleri_hazirla()
    
    def _etiketleri_hazirla(self):
        """Metin widget'ı için görsel etiketleri yapılandırır"""
        for kategori, stil in self.stil_haritasi.items():
            etiket_adi = f"leksikal_{kategori.name.lower()}"
            self.text_widget.tag_configure(etiket_adi, **stil)
    
    def leksikal_analiz_yap(self):
        """Kaynak metni leksikal birimlere ayrıştırır"""
        self.leksikal_birimler.clear()
        kaynak_metin = self.text_widget.get("1.0", tk.END)
        
        konum = 0
        while konum < len(kaynak_metin):
            eslesti = False
            
            for kategori, kalip in self.kalip_listesi:
                derlenmiş_kalip = re.compile(kalip)
                eslesme = derlenmiş_kalip.match(kaynak_metin, konum)
                
                if eslesme:
                    leksikal_birim = LeksikolBirim(
                        baslama_indeks=konum,
                        bitis_indeks=eslesme.end(),
                        kategori=kategori,
                        icerik=eslesme.group()
                    )
                    
                    if kategori != LeksikolTip.BOSALAN:  # Beyaz boşlukları kaydetme
                        self.leksikal_birimler.append(leksikal_birim)
                    
                    konum = eslesme.end()
                    eslesti = True
                    break
            
            if not eslesti:
                konum += 1  # Tanınmayan sembolü geç
        
        return self.leksikal_birimler
    
    def renklendirmeyi_uygula(self):
        """Tespit edilen leksikal birimlere göre metni görsel olarak biçimlendirir"""
        # Öncelikle tüm etiketleri kaldır
        for kategori in LeksikolTip:
            etiket_adi = f"leksikal_{kategori.name.lower()}"
            self.text_widget.tag_remove(etiket_adi, "1.0", tk.END)
        
        # Leksikal birimleri renklendir
        for birim in self.leksikal_birimler:
            etiket_adi = f"leksikal_{birim.kategori.name.lower()}"
            baslama_konumu = f"1.0+{birim.baslama_indeks}c"
            bitis_konumu = f"1.0+{birim.bitis_indeks}c"
            self.text_widget.tag_add(etiket_adi, baslama_konumu, bitis_konumu)


# Leksikal çözümleme sonuçlarını görselleştiren pencere sınıfı
class LeksikolAnalizGorunumu(tk.Toplevel):
    def __init__(self, parent, renklendirici):
        super().__init__(parent)
        self.renklendirici = renklendirici
        self.title("Leksikal Çözümleme")
        self.geometry("500x600")
        
        # Hiyerarşik görüntüleyici oluştur
        self.agac_gorunumu = ttk.Treeview(self, columns=("kategori", "icerik"), show="tree headings")
        self.agac_gorunumu.heading("#0", text="Leksikal Birim")
        self.agac_gorunumu.heading("kategori", text="Kategori")
        self.agac_gorunumu.heading("icerik", text="İçerik")
        
        # Kaydırma çubuğu ekle
        kaydirma_cubugu = ttk.Scrollbar(self, orient="vertical", command=self.agac_gorunumu.yview)
        self.agac_gorunumu.configure(yscrollcommand=kaydirma_cubugu.set)
        
        # Düzenleme
        self.agac_gorunumu.pack(side="left", fill="both", expand=True)
        kaydirma_cubugu.pack(side="right", fill="y")
        
        self.veriyi_guncelle()
    
    def veriyi_guncelle(self):
        """Hiyerarşik görünümü güncel leksikal birimlerle yeniler"""
        # Görünümü temizle
        for ogesi in self.agac_gorunumu.get_children():
            self.agac_gorunumu.delete(ogesi)
        
        # Ana düğümü ekle
        kok_dugum = self.agac_gorunumu.insert("", "end", text="C Programlama Dili Kaynak Kodu", open=True)
        
        # Her leksikal birimi ağaca ekle
        for sira, birim in enumerate(self.renklendirici.leksikal_birimler):
            kategori_ismi = self.leksikolKategoriIsminiAl(birim.kategori)
            birim_metni = repr(birim.icerik)
            self.agac_gorunumu.insert(kok_dugum, "end", text=f"Birim {sira+1}", 
                           values=(kategori_ismi, birim_metni))
    
    @staticmethod
    def leksikolKategoriIsminiAl(kategori):
        """Leksikal kategoriyi Türkçe isme dönüştürür"""
        isim_sozlugu = {
            LeksikolTip.REZERVE_KELIME: "Ayrılmış Kelime",
            LeksikolTip.DEGISKEN_ADI: "Kimlik Belirteci",
            LeksikolTip.NUMERIK_DEGER: "Sayısal Değer",
            LeksikolTip.ISLEMCI: "İşlem Operatörü",
            LeksikolTip.DIZGI: "Karakter Dizisi",
            LeksikolTip.TEK_KARAKTER: "Tekil Karakter", 
            LeksikolTip.ACIKLAMA: "Açıklama Metni",
            LeksikolTip.ONISLEMCI_KOMUT: "Ön İşlemci Komutu",
            LeksikolTip.AYRAC: "Ayrıştırıcı Simge",
            LeksikolTip.BOSALAN: "Boşluk Karakteri"
        }
        return isim_sozlugu.get(kategori, "Tanımsız")


# Sözdizimi ağacı düğüm kategorileri
class DugumKategorisi(Enum):
    PROGRAM_KOKÜ = auto()
    FONKSIYON_TANIMI = auto()
    DEGISKEN_BILDIRGESI = auto()
    PARAMETRE_LISTESI = auto()
    PARAMETRE = auto()
    IFADE_BILDIRIMI = auto()
    KOSULLU_IFADE = auto()
    DONGU_WHILE = auto()
    DONGU_FOR = auto()
    GERI_DONUS = auto()
    MATEMATIK_IFADE = auto()
    IKILI_ISLEM = auto()
    TEKLI_ISLEM = auto()
    ATAMA_ISLEMI = auto()
    SABIT_DEGER = auto()
    KIMLIK_BELIRTECI = auto()
    VERİ_TIPI = auto()
    KOD_BLOGU = auto()


# Sözdizimi ağacı düğüm yapısı
@dataclass
class SozdizimDugumu:
    kategori: DugumKategorisi
    deger: str = ""
    alt_dugumler: List['SozdizimDugumu'] = None
    
    def __post_init__(self):
        if self.alt_dugumler is None:
            self.alt_dugumler = []


# Gelişmiş sözdizimsel çözümleyici sınıfı
class SozdizimCozumleyicisi:
    def __init__(self, leksikal_birimler: List[LeksikolBirim]):
        self.leksikal_birimler = [b for b in leksikal_birimler if b.kategori != LeksikolTip.BOSALAN]
        self.mevcut_konum = 0
        self.aktif_birim = None
        self._ilerlet()
    
    def _ilerlet(self):
        """Bir sonraki leksikal birime geç"""
        if self.mevcut_konum < len(self.leksikal_birimler):
            self.aktif_birim = self.leksikal_birimler[self.mevcut_konum]
            self.mevcut_konum += 1
        else:
            self.aktif_birim = None
    
    def _eslesme_kontrol(self, beklenen_deger: str = None, beklenen_kategori: LeksikolTip = None) -> bool:
        """Leksikal birimin beklenenden eşleşip eşleşmediğini kontrol et"""
        if self.aktif_birim is None:
            return False
        if beklenen_deger and self.aktif_birim.icerik != beklenen_deger:
            return False
        if beklenen_kategori and self.aktif_birim.kategori != beklenen_kategori:
            return False
        return True
    
    def cozumle(self) -> SozdizimDugumu:
        """Ana çözümleme metodu"""
        kok = SozdizimDugumu(DugumKategorisi.PROGRAM_KOKÜ, "Program")
        
        while self.aktif_birim is not None:
            if self.aktif_birim.kategori == LeksikolTip.ACIKLAMA:
                yorum_dugumu = SozdizimDugumu(DugumKategorisi.IFADE_BILDIRIMI, f"Yorum: {self.aktif_birim.icerik[:30]}...")
                kok.alt_dugumler.append(yorum_dugumu)
                self._ilerlet()
            elif self.aktif_birim.kategori == LeksikolTip.ONISLEMCI_KOMUT:
                onislemci_dugumu = SozdizimDugumu(DugumKategorisi.IFADE_BILDIRIMI, f"Ön İşlemci: {self.aktif_birim.icerik}")
                kok.alt_dugumler.append(onislemci_dugumu)
                self._ilerlet()
            else:
                ifade = self._ifade_cozumle()
                if ifade:
                    kok.alt_dugumler.append(ifade)
                else:
                    self._ilerlet()
        
        return kok
    
    def _ifade_cozumle(self) -> Optional[SozdizimDugumu]:
        """İfadeleri çözümler"""
        if self.aktif_birim is None:
            return None
        
        if self.aktif_birim.kategori == LeksikolTip.REZERVE_KELIME:
            if self.aktif_birim.icerik in ["int", "float", "char", "double", "void"]:
                return self._degisken_veya_fonksiyon_cozumle()
            elif self.aktif_birim.icerik == "if":
                return self._if_cozumle()
            elif self.aktif_birim.icerik == "while":
                return self._while_cozumle()
            elif self.aktif_birim.icerik == "return":
                return self._return_cozumle()
        
        # Basit ifade olarak çözümle
        return self._basit_ifade_cozumle()
    
    def _degisken_veya_fonksiyon_cozumle(self) -> SozdizimDugumu:
        """Değişken veya fonksiyon tanımı çözümler"""
        tip_birimi = self.aktif_birim
        self._ilerlet()
        
        if self.aktif_birim and self.aktif_birim.kategori == LeksikolTip.DEGISKEN_ADI:
            isim_birimi = self.aktif_birim
            self._ilerlet()
            
            # Fonksiyon mu değişken mi?
            if self._eslesme_kontrol("(", LeksikolTip.AYRAC):
                return self._fonksiyon_tanimi_cozumle(tip_birimi, isim_birimi)
            else:
                return self._degisken_bildirimi_cozumle(tip_birimi, isim_birimi)
        
        return SozdizimDugumu(DugumKategorisi.IFADE_BILDIRIMI, "Geçersiz")
    
    def _fonksiyon_tanimi_cozumle(self, tip_birimi: LeksikolBirim, isim_birimi: LeksikolBirim) -> SozdizimDugumu:
        """Fonksiyon tanımı çözümler"""
        fonk_dugumu = SozdizimDugumu(DugumKategorisi.FONKSIYON_TANIMI, f"Fonksiyon: {isim_birimi.icerik}")
        
        # Return type
        tip_dugumu = SozdizimDugumu(DugumKategorisi.VERİ_TIPI, tip_birimi.icerik)
        fonk_dugumu.alt_dugumler.append(tip_dugumu)
        
        # Function name
        isim_dugumu = SozdizimDugumu(DugumKategorisi.KIMLIK_BELIRTECI, isim_birimi.icerik)
        fonk_dugumu.alt_dugumler.append(isim_dugumu)
        
        # Parametreler
        if self._eslesme_kontrol("(", LeksikolTip.AYRAC):
            self._ilerlet()  # '(' atla
            param_listesi = SozdizimDugumu(DugumKategorisi.PARAMETRE_LISTESI, "Parametreler")
            
            # Basit parametre çözümlemesi
            while self.aktif_birim and not self._eslesme_kontrol(")", LeksikolTip.AYRAC):
                if self.aktif_birim.kategori == LeksikolTip.REZERVE_KELIME:
                    param_tip = self.aktif_birim.icerik
                    self._ilerlet()
                    if self.aktif_birim and self.aktif_birim.kategori == LeksikolTip.DEGISKEN_ADI:
                        param_isim = self.aktif_birim.icerik
                        self._ilerlet()
                        param_dugumu = SozdizimDugumu(DugumKategorisi.PARAMETRE, f"{param_tip} {param_isim}")
                        param_listesi.alt_dugumler.append(param_dugumu)
                else:
                    self._ilerlet()
                
                if self._eslesme_kontrol(",", LeksikolTip.AYRAC):
                    self._ilerlet()
            
            if self._eslesme_kontrol(")", LeksikolTip.AYRAC):
                self._ilerlet()
            
            fonk_dugumu.alt_dugumler.append(param_listesi)
        
        # Function body
        if self._eslesme_kontrol("{", LeksikolTip.AYRAC):
            govde = self._kod_blogu_cozumle()
            if govde:
                fonk_dugumu.alt_dugumler.append(govde)
        
        return fonk_dugumu
    
    def _degisken_bildirimi_cozumle(self, tip_birimi: LeksikolBirim, isim_birimi: LeksikolBirim) -> SozdizimDugumu:
        """Değişken bildirimi çözümler"""
        dugum = SozdizimDugumu(DugumKategorisi.DEGISKEN_BILDIRGESI, f"Değişken: {isim_birimi.icerik}")
        
        # Type
        tip_dugumu = SozdizimDugumu(DugumKategorisi.VERİ_TIPI, tip_birimi.icerik)
        dugum.alt_dugumler.append(tip_dugumu)
        
        # Name
        isim_dugumu = SozdizimDugumu(DugumKategorisi.KIMLIK_BELIRTECI, isim_birimi.icerik)
        dugum.alt_dugumler.append(isim_dugumu)
        
        # Array veya assignment
        if self._eslesme_kontrol("[", LeksikolTip.AYRAC):
            self._ilerlet()
            self._noktalıvirgule_kadar_atla()
        elif self._eslesme_kontrol("=", LeksikolTip.ISLEMCI):
            self._ilerlet()
            deger = self._ifade_degeri_cozumle()
            if deger:
                atama_dugumu = SozdizimDugumu(DugumKategorisi.ATAMA_ISLEMI, "Atama")
                atama_dugumu.alt_dugumler.append(deger)
                dugum.alt_dugumler.append(atama_dugumu)
            self._noktalıvirgule_kadar_atla()
        else:
            self._noktalıvirgule_kadar_atla()
        
        return dugum
    
    def _kod_blogu_cozumle(self) -> SozdizimDugumu:
        """Kod bloğu çözümler"""
        if not self._eslesme_kontrol("{", LeksikolTip.AYRAC):
            return None
        
        self._ilerlet()  # '{' atla
        blok = SozdizimDugumu(DugumKategorisi.KOD_BLOGU, "Kod Bloğu")
        
        while self.aktif_birim and not self._eslesme_kontrol("}", LeksikolTip.AYRAC):
            ifade = self._ifade_cozumle()
            if ifade:
                blok.alt_dugumler.append(ifade)
            else:
                self._ilerlet()
        
        if self._eslesme_kontrol("}", LeksikolTip.AYRAC):
            self._ilerlet()
        
        return blok
    
    def _if_cozumle(self) -> SozdizimDugumu:
        """If ifadesi çözümler"""
        dugum = SozdizimDugumu(DugumKategorisi.KOSULLU_IFADE, "If İfadesi")
        self._ilerlet()  # 'if' atla
        
        if self._eslesme_kontrol("(", LeksikolTip.AYRAC):
            self._ilerlet()
            kosul = SozdizimDugumu(DugumKategorisi.MATEMATIK_IFADE, "Koşul")
            # Basit koşul çözümlemesi
            while self.aktif_birim and not self._eslesme_kontrol(")", LeksikolTip.AYRAC):
                if self.aktif_birim.kategori in [LeksikolTip.DEGISKEN_ADI, LeksikolTip.NUMERIK_DEGER]:
                    ifade_dugumu = SozdizimDugumu(DugumKategorisi.SABIT_DEGER, self.aktif_birim.icerik)
                    kosul.alt_dugumler.append(ifade_dugumu)
                self._ilerlet()
            
            if self._eslesme_kontrol(")", LeksikolTip.AYRAC):
                self._ilerlet()
            
            dugum.alt_dugumler.append(kosul)
        
        if self._eslesme_kontrol("{", LeksikolTip.AYRAC):
            govde = self._kod_blogu_cozumle()
            if govde:
                dugum.alt_dugumler.append(govde)
        
        return dugum
    
    def _while_cozumle(self) -> SozdizimDugumu:
        """While döngüsü çözümler"""
        dugum = SozdizimDugumu(DugumKategorisi.DONGU_WHILE, "While Döngüsü")
        self._ilerlet()  # 'while' atla
        
        if self._eslesme_kontrol("(", LeksikolTip.AYRAC):
            self._ilerlet()
            kosul = SozdizimDugumu(DugumKategorisi.MATEMATIK_IFADE, "Koşul")
            # Koşul içeriğini basit çözümle
            while self.aktif_birim and not self._eslesme_kontrol(")", LeksikolTip.AYRAC):
                self._ilerlet()
            
            if self._eslesme_kontrol(")", LeksikolTip.AYRAC):
                self._ilerlet()
            
            dugum.alt_dugumler.append(kosul)
        
        if self._eslesme_kontrol("{", LeksikolTip.AYRAC):
            govde = self._kod_blogu_cozumle()
            if govde:
                dugum.alt_dugumler.append(govde)
        
        return dugum
    
    def _return_cozumle(self) -> SozdizimDugumu:
        """Return ifadesi çözümler"""
        dugum = SozdizimDugumu(DugumKategorisi.GERI_DONUS, "Return İfadesi")
        self._ilerlet()  # 'return' atla
        
        deger = self._ifade_degeri_cozumle()
        if deger:
            dugum.alt_dugumler.append(deger)
        
        self._noktalıvirgule_kadar_atla()
        return dugum
    
    def _ifade_degeri_cozumle(self) -> Optional[SozdizimDugumu]:
        """İfade değeri çözümler"""
        if self.aktif_birim is None:
            return None
        
        if self.aktif_birim.kategori == LeksikolTip.DEGISKEN_ADI:
            dugum = SozdizimDugumu(DugumKategorisi.KIMLIK_BELIRTECI, self.aktif_birim.icerik)
            self._ilerlet()
            return dugum
        elif self.aktif_birim.kategori == LeksikolTip.NUMERIK_DEGER:
            dugum = SozdizimDugumu(DugumKategorisi.SABIT_DEGER, self.aktif_birim.icerik)
            self._ilerlet()
            return dugum
        elif self.aktif_birim.kategori == LeksikolTip.DIZGI:
            dugum = SozdizimDugumu(DugumKategorisi.SABIT_DEGER, self.aktif_birim.icerik)
            self._ilerlet()
            return dugum
        
        return None
    
    def _basit_ifade_cozumle(self) -> Optional[SozdizimDugumu]:
        """Basit ifade çözümler"""
        if self.aktif_birim is None:
            return None
        
        ifade = SozdizimDugumu(DugumKategorisi.MATEMATIK_IFADE, "İfade")
        
        # Basit çözümleme
        while self.aktif_birim and not self._ifade_sonu_mu():
            if self.aktif_birim.kategori in [LeksikolTip.DEGISKEN_ADI, LeksikolTip.NUMERIK_DEGER]:
                dugum = SozdizimDugumu(DugumKategorisi.SABIT_DEGER, self.aktif_birim.icerik)
                ifade.alt_dugumler.append(dugum)
            self._ilerlet()
        
        return ifade if ifade.alt_dugumler else None
    
    def _noktalıvirgule_kadar_atla(self):
        """Noktalı virgüle kadar atla"""
        while self.aktif_birim and not self._eslesme_kontrol(";", LeksikolTip.AYRAC):
            self._ilerlet()
        if self.aktif_birim and self._eslesme_kontrol(";", LeksikolTip.AYRAC):
            self._ilerlet()
    
    def _ifade_sonu_mu(self) -> bool:
        """İfade sonu mu kontrol et"""
        return (self.aktif_birim is None or 
                self._eslesme_kontrol(";", LeksikolTip.AYRAC) or
                self._eslesme_kontrol("}", LeksikolTip.AYRAC))


# Sözdizimi ağacı görüntüleyici pencere sınıfı
class SozdizimAgaciGorunumu(tk.Toplevel):
    def __init__(self, parent, renklendirici):
        super().__init__(parent)
        self.renklendirici = renklendirici
        self.title("Sözdizimi Ağacı")
        self.geometry("600x700")
        
        # Ağaç görüntüleyici oluştur
        self.agac_widget = ttk.Treeview(self, show="tree")
        
        # Kaydırma çubuğu ekle
        kaydirma_cubugu = ttk.Scrollbar(self, orient="vertical", command=self.agac_widget.yview)
        self.agac_widget.configure(yscrollcommand=kaydirma_cubugu.set)
        
        # Düzenleme
        self.agac_widget.pack(side="left", fill="both", expand=True)
        kaydirma_cubugu.pack(side="right", fill="y")
        
        self.agaci_yenile()
    
    def agaci_yenile(self):
        """Ağacı güncel sözdizimi ağacı ile yeniler"""
        # Ağacı temizle
        for ogesi in self.agac_widget.get_children():
            self.agac_widget.delete(ogesi)
        
        # Çözümleyiciyi çalıştır
        cozumleyici = SozdizimCozumleyicisi(self.renklendirici.leksikal_birimler)
        kok_dugum = cozumleyici.cozumle()
        
        # Ağacı oluştur
        self._dugumu_agaca_ekle("", kok_dugum)
    
    def _dugumu_agaca_ekle(self, parent_id: str, dugum: SozdizimDugumu):
        """Düğümü ağaca ekler"""
        etiket = self.dugumKategorisiIsminiAl(dugum.kategori)
        if dugum.deger:
            etiket += f": {dugum.deger}"
        
        ogesi_id = self.agac_widget.insert(parent_id, "end", text=etiket, open=True)
        
        for alt_dugum in dugum.alt_dugumler:
            self._dugumu_agaca_ekle(ogesi_id, alt_dugum)
    
    @staticmethod
    def dugumKategorisiIsminiAl(kategori: DugumKategorisi) -> str:
        """Düğüm kategorisini Türkçe isme çevirir"""
        isimler = {
            DugumKategorisi.PROGRAM_KOKÜ: "Program",
            DugumKategorisi.FONKSIYON_TANIMI: "Fonksiyon Tanımı",
            DugumKategorisi.DEGISKEN_BILDIRGESI: "Değişken Bildirimi",
            DugumKategorisi.PARAMETRE_LISTESI: "Parametre Listesi",
            DugumKategorisi.PARAMETRE: "Parametre",
            DugumKategorisi.IFADE_BILDIRIMI: "İfade",
            DugumKategorisi.KOSULLU_IFADE: "Koşullu İfade",
            DugumKategorisi.DONGU_WHILE: "While Döngüsü",
            DugumKategorisi.DONGU_FOR: "For Döngüsü",
            DugumKategorisi.GERI_DONUS: "Return İfadesi",
            DugumKategorisi.MATEMATIK_IFADE: "Matematik İfade",
            DugumKategorisi.IKILI_ISLEM: "İkili İşlem",
            DugumKategorisi.TEKLI_ISLEM: "Tekli İşlem",
            DugumKategorisi.ATAMA_ISLEMI: "Atama İşlemi",
            DugumKategorisi.SABIT_DEGER: "Sabit Değer",
            DugumKategorisi.KIMLIK_BELIRTECI: "Kimlik Belirteci",
            DugumKategorisi.VERİ_TIPI: "Veri Tipi",
            DugumKategorisi.KOD_BLOGU: "Kod Bloğu"
        }
        return isimler.get(kategori, "Bilinmeyen")


# Merkezi uygulama arayüzü sınıfı
class MerkeziPencere(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("C Dilinde Sözdizimi Renklendirici ve Çözümleme Aracı")
        self.geometry("900x700")
        
        # Ana çerçeve
        ana_cerceve = ttk.Frame(self)
        ana_cerceve.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Kod düzenleyici alanı
        self.kod_editoru = scrolledtext.ScrolledText(
            ana_cerceve, 
            wrap="none", 
            font=("Courier", 12),
            height=30,
            bg="white",        # Arkaplan rengi beyaz
            fg="black",        # Varsayılan metin rengi siyah
            insertbackground="black"  # İmleç rengi siyah
        )
        self.kod_editoru.pack(fill="both", expand=True)
        
        # Kontrol düğmeleri çerçevesi
        dugme_cercevesi = ttk.Frame(ana_cerceve)
        dugme_cercevesi.pack(fill="x", pady=(10, 0))
        
        # İşlev düğmeleri
        self.leksikal_dugme = ttk.Button(
            dugme_cercevesi, 
            text="Leksikal Çözümleme", 
            command=self.leksikal_gorunumu_ac
        )
        self.leksikal_dugme.pack(side="left", padx=(0, 10))
        
        self.sozdizimi_dugme = ttk.Button(
            dugme_cercevesi, 
            text="Sözdizimi Ağacı", 
            command=self.sozdizimi_agacini_goster
        )
        self.sozdizimi_dugme.pack(side="left")
        
        # Sözdizimi renklendirici
        self.renklendirici = SozdizimRenklendiricisi(self.kod_editoru)
        
        # Yardımcı pencereler
        self.leksikal_penceresi = None
        self.sozdizimi_penceresi = None
        
        # Olay bağlantıları
        self.kod_editoru.bind('<KeyRelease>', self.icerik_degistiginde)
        self.kod_editoru.bind('<Button-1>', self.icerik_degistiginde)
        
        # Örnek kaynak kod yükle
        self.varsayilan_kod_yukle()
        
        # İlk çözümleme
        self.icerik_degistiginde()
    
    def icerik_degistiginde(self, olay=None):
        """Editör içeriği değiştiğinde çağrılan işlev"""
        try:
            self.renklendirici.leksikal_analiz_yap()
            self.renklendirici.renklendirmeyi_uygula()
            
            # Yardımcı pencereleri güncelle
            if self.leksikal_penceresi and self.leksikal_penceresi.winfo_exists():
                self.leksikal_penceresi.veriyi_guncelle()
            if self.sozdizimi_penceresi and self.sozdizimi_penceresi.winfo_exists():
                self.sozdizimi_penceresi.agaci_yenile()
                
        except Exception as hata:
            print(f"İşlem hatası: {hata}")
    
    def leksikal_gorunumu_ac(self):
        """Leksikal çözümleme penceresini görüntüle"""
        if self.leksikal_penceresi is None or not self.leksikal_penceresi.winfo_exists():
            self.leksikal_penceresi = LeksikolAnalizGorunumu(self, self.renklendirici)
        else:
            self.leksikal_penceresi.veriyi_guncelle()
            self.leksikal_penceresi.lift()
    
    def sozdizimi_agacini_goster(self):
        """Sözdizimi ağacı penceresini görüntüle"""
        if self.sozdizimi_penceresi is None or not self.sozdizimi_penceresi.winfo_exists():
            self.sozdizimi_penceresi = SozdizimAgaciGorunumu(self, self.renklendirici)
        else:
            self.sozdizimi_penceresi.agaci_yenile()
            self.sozdizimi_penceresi.lift()
    
    def varsayilan_kod_yukle(self):
        """Varsayılan C kaynak kodunu editöre yerleştirir"""
        demo_kod = '''// Bu satır tek satırlık açıklama içerir
/* Aşağıdaki blok
   çoklu satır
   açıklama örneğidir */

#include <stdio.h>
#include <stdlib.h>

char ileti[] = "Selam Dünya!";
int deger = 42;
float pi_sayisi = 3.14159;
char harf = 'X';

int islev_calistir(int a, float b) {
    if (a > 0 && b < 100.0) {
        char durum[] = "Olumlu";
        return a + (int)b;
    } else {
        while (a != 0) {
            a = a - 1;
            b = b * 2.0;
        }
        for (int j = 0; j < 10; j++) {
            float toplam = a + b;
            if (toplam >= 50.0) {
                break;
            }
        }
    }
    return 0;
}

int main() {
    int sonuc = islev_calistir(5, 10.5);
    printf("Çıktı: %d\\n", sonuc);
    return 0;
}
'''
        self.kod_editoru.insert("1.0", demo_kod)


if __name__ == "__main__":
    uygulama = MerkeziPencere()
    uygulama.mainloop() 
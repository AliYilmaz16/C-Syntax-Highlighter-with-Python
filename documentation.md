# C Syntax Vurgulayıcı ve Sözdizimi Ağacı Dokümantasyonu (Python)

## İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Kurulum ve Gereksinimler](#kurulum-ve-gereksinimler)
3. [Syntax Vurgulayıcı](#syntax-vurgulayıcı)
   - [Token Tipleri](#token-tipleri)
   - [SyntaxVurgulayici Sınıfı](#syntaxvurgulayici-sınıfı)
   - [Token İşleme](#token-işleme)
   - [Regex Desenleri](#regex-desenleri)
   - [Renk ve Stil Yönetimi](#renk-ve-stil-yönetimi)
4. [Sözdizimi Ağacı](#sözdizimi-ağacı)
   - [Düğüm Tipleri](#düğüm-tipleri)
   - [Parser Sınıfı](#parser-sınıfı)
   - [Ağaç Yapısı](#ağaç-yapısı)
   - [Ayrıştırma Stratejisi](#ayrıştırma-stratejisi)
   - [Hata Yönetimi](#hata-yönetimi)
5. [Kullanıcı Arayüzü](#kullanıcı-arayüzü)
   - [Ana Pencere](#ana-pencere)
   - [Lexical Analiz Penceresi](#lexical-analiz-penceresi)
   - [Sözdizimi Ağacı Penceresi](#sözdizimi-ağacı-penceresi)
6. [Örnek Kullanım](#örnek-kullanım)
   - [Basit Örnekler](#basit-örnekler)
   - [Karmaşık Örnekler](#karmaşık-örnekler)

## Genel Bakış

Bu proje, C kodlarını analiz eden ve görselleştiren iki ana bileşenden oluşmaktadır:

1. **Syntax Vurgulayıcı**: Kaynak kodundaki farklı token'ları (anahtar kelimeler, tanımlayıcılar, sayılar vb.) renklendirerek görsel olarak ayırt edilmesini sağlar.
2. **Sözdizimi Ağacı**: Kaynak kodun yapısal analizini yaparak, kodun hiyerarşik bir ağaç yapısında gösterilmesini sağlar.

Proje Python'da tkinter kütüphanesi kullanılarak geliştirilmiştir ve modern bir grafiksel kullanıcı arayüzü sunmaktadır.

### Temel Özellikler

- Gerçek zamanlı syntax vurgulama
- Detaylı lexical analiz görüntüleme
- Hiyerarşik sözdizimi ağacı gösterimi
- Modern ve kullanıcı dostu arayüz
- Platform bağımsız çalışma

## Kurulum ve Gereksinimler

### Sistem Gereksinimleri

- Python 3.7 veya üzeri
- tkinter (Python'un standart kütüphanesi)
- typing modülü (Python 3.7+ için)
- dataclasses modülü (Python 3.7+ için)
- enum modülü (Python 3.4+ için)

### Kurulum Adımları

1. Python kurulumunu kontrol edin:
```bash
python --version
# Çıktı: Python 3.7.0 veya üzeri olmalı
```

2. Gerekli modülleri test edin:
```bash
python -c "import tkinter, typing, dataclasses, enum, re; print('Tüm modüller mevcut')"
```

3. Projeyi çalıştırın:
```bash
python main.py
```

### Bağımlılıklar

Proje şu ana Python modüllerini kullanır:

```python
import tkinter as tk                    # GUI framework
from tkinter import ttk, scrolledtext   # GUI bileşenleri
import re                              # Regex işlemleri
from typing import Dict, List, Tuple   # Tip belirteçleri
from dataclasses import dataclass      # Veri sınıfları
from enum import Enum, auto           # Enum tanımları
```

## Syntax Vurgulayıcı

### Token Tipleri

Token tipleri, kaynak kodundaki farklı öğeleri sınıflandırmak için kullanılan temel yapı taşlarıdır. Her token tipi, kodun belirli bir öğesini temsil eder ve ona özel bir renk/stil atanır.

```python
class TokenTipi(Enum):
    ANAHTAR_KELIME = auto()  # if, else, while gibi C anahtar kelimeleri
    TANIMLAYICI = auto()     # Değişken ve fonksiyon isimleri
    SAYI = auto()            # Sayısal değerler (tam sayı ve ondalıklı)
    OPERATOR = auto()        # +, -, *, /, =, ==, != gibi operatörler
    METIN = auto()           # Çift tırnak içindeki string'ler
    KARAKTER = auto()        # Tek tırnak içindeki karakterler
    YORUM = auto()           # // veya /* */ içindeki yorumlar
    ONISLEMCI = auto()       # #include, #define gibi ön işlemci direktifleri
    SEPARATOR = auto()       # Parantezler, noktalı virgül vb.
    BOSLUK = auto()          # Boşluk, tab ve satır sonları
```

### Token Yapısı

Token yapısı, her bir token'ın metin içindeki konumunu ve özelliklerini tutan temel veri yapısıdır:

```python
@dataclass
class Token:
    baslangic: int           # Token'ın metin içindeki başlangıç pozisyonu
    bitis: int               # Token'ın metin içindeki bitiş pozisyonu
    tip: TokenTipi           # Token'ın tipi
    deger: str               # Token'ın değeri
```

### SyntaxVurgulayici Sınıfı

SyntaxVurgulayici sınıfı, kaynak kodun token'lara ayrılması ve renklendirilmesi işlemlerini yöneten ana sınıftır:

```python
class SyntaxVurgulayici:
    def __init__(self, text_widget: scrolledtext.ScrolledText):
        self.text_widget = text_widget
        self.tokenlar: List[Token] = []
        
        # C anahtar kelimeleri listesi
        self.anahtarKelimeler = [
            "auto", "break", "case", "char", "const", "continue", 
            "default", "do", "double", "else", "enum", "extern", 
            "float", "for", "goto", "if", "int", "long", "register", 
            "return", "short", "signed", "sizeof", "static", "struct", 
            "switch", "typedef", "union", "unsigned", "void", 
            "volatile", "while"
        ]
```

### Regex Desenleri

Regex desenleri, farklı token tiplerini metin içinde bulmak için kullanılan güçlü araçlardır:

```python
# Token tiplerini bulmak için kullanılan regex desenleri
self.regex_desenleri = [
    (TokenTipi.YORUM, r'//[^\n]*|/\*[\s\S]*?\*/'),
    (TokenTipi.ONISLEMCI, r'#\s*\w+.*'),
    (TokenTipi.METIN, r'"(?:[^"\\]|\\.)*"'),
    (TokenTipi.KARAKTER, r"'(?:[^'\\]|\\.)'"),
    (TokenTipi.ANAHTAR_KELIME, r'\b(' + '|'.join(self.anahtarKelimeler) + r')\b'),
    (TokenTipi.SAYI, r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b'),
    (TokenTipi.OPERATOR, r'(==|!=|<=|>=|&&|\|\||<<|>>|\+\+|--|[+\-*/%=<>!&|^~]|\?|:)'),
    (TokenTipi.SEPARATOR, r'[(){}\[\];,.]'),
    (TokenTipi.TANIMLAYICI, r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    (TokenTipi.BOSLUK, r'\s+'),
]
```

#### Regex Desenlerinin Açıklamaları:

1. **Yorumlar**: `//[^\n]*|/\*[\s\S]*?\*/`
   - Tek satır yorumları (`//`) ve çok satır yorumları (`/* */`) yakalar

2. **Ön İşlemci**: `#\s*\w+.*`
   - `#include`, `#define` gibi direktifleri yakalar

3. **Metinler**: `"(?:[^"\\]|\\.)*"`
   - Çift tırnak içindeki string'leri yakalar, kaçış karakterlerini dikkate alır

4. **Karakterler**: `'(?:[^'\\]|\\.)'`
   - Tek tırnak içindeki karakterleri yakalar

5. **Anahtar Kelimeler**: `\b(if|else|while|...)\b`
   - C'nin anahtar kelimelerini word boundary ile yakalar

6. **Sayılar**: `\b\d+(\.\d+)?([eE][+-]?\d+)?\b`
   - Tam sayı, ondalık ve bilimsel notasyon sayılarını yakalar

7. **Operatörler**: `(==|!=|<=|>=|&&|\|\||...)`
   - C'nin tüm operatörlerini yakalar

### Token İşleme

Token işleme süreci iki ana adımdan oluşur:

#### 1. Tokenization (Token'lara Ayırma)

```python
def tokenize(self) -> List[Token]:
    """Metni token'lara ayırır"""
    self.tokenlar.clear()
    metin = self.text_widget.get("1.0", tk.END)
    
    pos = 0
    while pos < len(metin):
        match_found = False
        
        for tip, pattern in self.regex_desenleri:
            regex = re.compile(pattern)
            match = regex.match(metin, pos)
            
            if match:
                token = Token(
                    baslangic=pos,
                    bitis=match.end(),
                    tip=tip,
                    deger=match.group()
                )
                
                if tip != TokenTipi.BOSLUK:  # Boşlukları kaydetme
                    self.tokenlar.append(token)
                
                pos = match.end()
                match_found = True
                break
        
        if not match_found:
            pos += 1  # Bilinmeyen karakteri atla
    
    return self.tokenlar
```

#### 2. Vurgulama (Highlighting)

```python
def vurgula(self):
    """Bulunan token'lara göre metni renklendirir"""
    # Önce tüm tag'leri temizle
    for tip in TokenTipi:
        tag_name = f"token_{tip.name.lower()}"
        self.text_widget.tag_remove(tag_name, "1.0", tk.END)
    
    # Token'ları renklendir
    for token in self.tokenlar:
        tag_name = f"token_{token.tip.name.lower()}"
        start_index = f"1.0+{token.baslangic}c"
        end_index = f"1.0+{token.bitis}c"
        self.text_widget.tag_add(tag_name, start_index, end_index)
```

### Renk ve Stil Yönetimi

Her token tipi için özel renk ve font stilleri tanımlanır:

```python
# Her token tipi için renk tanımlamaları
self.renkHaritasi = {
    TokenTipi.ANAHTAR_KELIME: {"foreground": "blue", "font": ("Courier", 12, "bold")},
    TokenTipi.TANIMLAYICI: {"foreground": "black", "font": ("Courier", 12, "normal")},
    TokenTipi.SAYI: {"foreground": "red", "font": ("Courier", 12, "normal")},
    TokenTipi.OPERATOR: {"foreground": "purple", "font": ("Courier", 12, "normal")},
    TokenTipi.METIN: {"foreground": "green", "font": ("Courier", 12, "normal")},
    TokenTipi.KARAKTER: {"foreground": "orange", "font": ("Courier", 12, "normal")},
    TokenTipi.YORUM: {"foreground": "gray", "font": ("Courier", 12, "italic")},
    TokenTipi.ONISLEMCI: {"foreground": "darkred", "font": ("Courier", 12, "bold")},
    TokenTipi.SEPARATOR: {"foreground": "brown", "font": ("Courier", 12, "normal")},
    TokenTipi.BOSLUK: {"foreground": "black", "font": ("Courier", 12, "normal")}
}
```

## Sözdizimi Ağacı

### Düğüm Tipleri

Düğüm tipleri, sözdizimi ağacındaki her bir düğümün ne tür bir kod yapısını temsil ettiğini belirten sınıflandırma sistemidir:

```python
class NodeType(Enum):
    PROGRAM = auto()            # Programın kök düğümü
    FUNCTION_DEF = auto()       # Fonksiyon tanımı
    VARIABLE_DECL = auto()      # Değişken tanımı
    PARAM_LIST = auto()         # Parametre listesi
    PARAM = auto()              # Tek bir parametre
    STATEMENT = auto()          # Genel ifade
    IF_STATEMENT = auto()       # If koşul ifadesi
    WHILE_STATEMENT = auto()    # While döngü ifadesi
    FOR_STATEMENT = auto()      # For döngü ifadesi
    RETURN_STATEMENT = auto()   # Return ifadesi
    EXPRESSION = auto()         # Genel ifade
    BINARY_EXPR = auto()        # İkili işlem (+, -, *, /, vb.)
    UNARY_EXPR = auto()         # Tekli işlem
    ASSIGNMENT_EXPR = auto()    # Atama ifadesi
    LITERAL = auto()            # Sabit değer
    IDENTIFIER = auto()         # Tanımlayıcı
    TYPE = auto()               # Veri tipi
    BLOCK_STATEMENT = auto()    # Kod bloğu
```

### Parser Sınıfı

Parser sınıfı, token'ları okuyup sözdizimi ağacını oluşturan sistemdir:

```python
class Parser:
    def __init__(self, tokenlar: List[Token]):
        self.tokenlar = tokenlar
        self.position = 0
        self.current_token = None
        self._advance()
    
    def _advance(self):
        """Bir sonraki token'a geç"""
        if self.position < len(self.tokenlar):
            self.current_token = self.tokenlar[self.position]
            self.position += 1
        else:
            self.current_token = None
    
    def parse(self) -> ParseNode:
        """Ana parse metodu"""
        root = ParseNode(NodeType.PROGRAM, "Program")
        
        while self.current_token is not None:
            stmt = self.parse_statement()
            if stmt:
                root.children.append(stmt)
        
        return root
```

### Ağaç Yapısı

Parse tree'nin düğüm yapısı şu şekilde tanımlanır:

```python
@dataclass
class ParseNode:
    type: NodeType
    value: str = ""
    children: List['ParseNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
```

### Ayrıştırma Stratejisi

Parser, farklı ifade tiplerini ayrıştırmak için özel metodlar kullanır:

#### 1. İfade Ayrıştırma

```python
def parse_statement(self) -> Optional[ParseNode]:
    """İfadeleri ayrıştırır"""
    if self.current_token is None:
        return None
    
    if self.current_token.tip == TokenTipi.ANAHTAR_KELIME:
        if self.current_token.deger in ["int", "float", "char", "double", "void"]:
            return self.parse_declaration()
        elif self.current_token.deger == "if":
            return self.parse_if_statement()
        elif self.current_token.deger == "while":
            return self.parse_while_statement()
        elif self.current_token.deger == "for":
            return self.parse_for_statement()
        elif self.current_token.deger == "return":
            return self.parse_return_statement()
    
    # Basit ifade olarak parse et
    expr = self.parse_expression()
    self._skip_until_semicolon()
    return expr
```

#### 2. Değişken Tanımı Ayrıştırma

```python
def parse_declaration(self) -> ParseNode:
    """Değişken tanımlaması ayrıştırır"""
    node = ParseNode(NodeType.VARIABLE_DECL, "Değişken Tanımı")
    
    # Tip
    if self.current_token and self.current_token.tip == TokenTipi.ANAHTAR_KELIME:
        type_node = ParseNode(NodeType.TYPE, self.current_token.deger)
        node.children.append(type_node)
        self._advance()
    
    # İsim
    if self.current_token and self.current_token.tip == TokenTipi.TANIMLAYICI:
        id_node = ParseNode(NodeType.IDENTIFIER, self.current_token.deger)
        node.children.append(id_node)
        self._advance()
    
    self._skip_until_semicolon()
    return node
```

#### 3. If İfadesi Ayrıştırma

```python
def parse_if_statement(self) -> ParseNode:
    """If ifadesi ayrıştırır"""
    node = ParseNode(NodeType.IF_STATEMENT, "If İfadesi")
    self._advance()  # 'if' token'ını atla
    
    # Koşul ifadesini basit şekilde ayrıştır
    condition = ParseNode(NodeType.EXPRESSION, "Koşul")
    node.children.append(condition)
    
    self._skip_until_brace()
    return node
```

### Hata Yönetimi

Parser, basit hata yönetimi mekanizmaları içerir:

```python
def _skip_until_semicolon(self):
    """Noktalı virgüle kadar atla"""
    while (self.current_token and 
           not (self.current_token.tip == TokenTipi.SEPARATOR and 
                self.current_token.deger == ";")):
        self._advance()
    if self.current_token:
        self._advance()  # Noktalı virgülü de atla

def _skip_until_brace(self):
    """Süslü paranteze kadar atla"""
    while (self.current_token and 
           not (self.current_token.tip == TokenTipi.SEPARATOR and 
                self.current_token.deger == "{")):
        self._advance()
```

## Kullanıcı Arayüzü

### Ana Pencere

Ana pencere, uygulamanın merkezi arayüzünü oluşturur:

```python
class AnaPencere(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("C Syntax Vurgulayıcı ve Analiz Aracı")
        self.geometry("900x700")
        
        # Ana frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Metin düzenleyici
        self.text_editor = scrolledtext.ScrolledText(
            main_frame, 
            wrap="none", 
            font=("Courier", 12),
            height=30
        )
        self.text_editor.pack(fill="both", expand=True)
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.lex_button = ttk.Button(
            button_frame, 
            text="Lexical Analiz", 
            command=self.lex_goster
        )
        self.lex_button.pack(side="left", padx=(0, 10))
        
        self.parse_button = ttk.Button(
            button_frame, 
            text="Sözdizimi Ağacı", 
            command=self.parse_tree_goster
        )
        self.parse_button.pack(side="left")
```

### Lexical Analiz Penceresi

Token'ları ağaç yapısında gösteren pencere:

```python
class LexicalAnalizPencere(tk.Toplevel):
    def __init__(self, parent, vurgulayici: SyntaxVurgulayici):
        super().__init__(parent)
        self.vurgulayici = vurgulayici
        self.title("Lexical Analiz")
        self.geometry("500x600")
        
        # Ağaç yapısını oluştur
        self.tree = ttk.Treeview(self, columns=("tip", "deger"), show="tree headings")
        self.tree.heading("#0", text="Token")
        self.tree.heading("tip", text="Tip")
        self.tree.heading("deger", text="Değer")
        
        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
```

### Sözdizimi Ağacı Penceresi

Parse tree'yi gösteren pencere:

```python
class ParseTreePencere(tk.Toplevel):
    def __init__(self, parent, vurgulayici: SyntaxVurgulayici):
        super().__init__(parent)
        self.vurgulayici = vurgulayici
        self.title("Sözdizimi Ağacı")
        self.geometry("600x700")
        
        # Ağaç yapısını oluştur
        self.tree = ttk.Treeview(self, show="tree")
        
        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
```

## Örnek Kullanım

### Basit Örnekler

#### 1. Değişken Tanımlamaları

```c
int sayi = 42;
float pi = 3.14159;
char karakter = 'A';
```

**Lexical Analiz Çıktısı:**
- Token 1: Anahtar Kelime: "int"
- Token 2: Tanımlayıcı: "sayi"
- Token 3: Operatör: "="
- Token 4: Sayı: "42"
- Token 5: Ayırıcı: ";"

**Parse Tree Çıktısı:**
```
Program
├── Değişken Tanımı
│   ├── Veri Tipi: int
│   └── Tanımlayıcı: sayi
├── Değişken Tanımı
│   ├── Veri Tipi: float
│   └── Tanımlayıcı: pi
└── Değişken Tanımı
    ├── Veri Tipi: char
    └── Tanımlayıcı: karakter
```

#### 2. Basit If İfadesi

```c
if (x > 0) {
    return 1;
}
```

**Parse Tree Çıktısı:**
```
Program
└── If İfadesi
    └── Koşul
```

### Karmaşık Örnekler

#### 1. Fonksiyon Tanımı (Basit Analiz)

```c
int hesapla(int x, float y) {
    if (x > 0 && y < 100.0) {
        return x + y;
    }
    return 0;
}
```

**Lexical Analiz Özeti:**
- 25+ token tespit edilir
- Anahtar kelimeler: int, if, return
- Tanımlayıcılar: hesapla, x, y
- Operatörler: >, &&, <, +
- Sayılar: 0, 100.0
- Ayırıcılar: (, ), {, }, ;

#### 2. Çoklu Yapılar

```c
#include <stdio.h>

int main() {
    for (int i = 0; i < 10; i++) {
        while (i > 5) {
            printf("Sayı: %d\n", i);
            break;
        }
    }
    return 0;
}
```

**Parse Tree Yapısı:**
```
Program
├── Değişken Tanımı (main fonksiyonu olarak)
│   ├── Veri Tipi: int
│   └── Tanımlayıcı: main
├── For Döngüsü
│   ├── Başlangıç
│   ├── Koşul
│   └── Artırma
├── While Döngüsü
│   └── Koşul
└── Return İfadesi
```

## Performans ve Optimizasyon

### Token İşleme Performansı

- Regex kullanımı O(n) kompleksitede çalışır
- Büyük dosyalar için bellek kullanımı token sayısı ile doğru orantılı
- Gerçek zamanlı güncelleme için debouncing önerilir

### Bellek Yönetimi

- Token'lar listede saklanır
- Parse tree düğümleri referans ile bağlanır
- Garbage collection otomatik çalışır

### Optimizasyon Önerileri

1. **Büyük Dosyalar İçin:**
   - Lazy loading
   - Chunked processing
   - Background threading

2. **Performans İyileştirmeleri:**
   - Compiled regex kullanımı
   - Token caching
   - Incremental parsing

## Sınırlamalar ve Gelecek Geliştirmeler

### Mevcut Sınırlamalar

1. **Parser Sınırlamaları:**
   - Basit statement parsing
   - Fonksiyon gövdesi tam ayrıştırılmaz
   - Tip dönüşümleri desteklenmez

2. **Lexical Analiz Sınırlamaları:**
   - Karmaşık makrolar desteklenmez
   - Conditional compilation direktifleri basit
   - String escape karakterleri sınırlı

3. **UI Sınırlamaları:**
   - Tema değiştirme yok
   - Font boyutu sabit
   - Klavye kısayolları sınırlı

### Gelecek Geliştirmeler

1. **Parser İyileştirmeleri:**
   - Tam semantic analiz
   - Symbol table oluşturma
   - Tip kontrolü
   - Function call graph

2. **UI İyileştirmeleri:**
   - Tema desteği
   - Dosya yönetimi
   - Find/Replace özelliği
   - Code completion

3. **Analiz Özellikleri:**
   - Hata tespiti
   - Warning'ler
   - Code metrics
   - Dependency analysis

## Teknik Detaylar

### Regex Pattern Optimizasyonu

Regex desenleri performans için öncelik sırasına göre düzenlenmiştir:

1. Yorumlar (en uzun match'ler)
2. String'ler
3. Anahtar kelimeler
4. Sayılar
5. Operatörler
6. Tanımlayıcılar (en genel)

### Tkinter Tag Sistemi

Text widget'ın tag sistemi kullanılarak renklendirme yapılır:

```python
# Tag oluşturma
self.text_widget.tag_configure("token_anahtar_kelime", 
                              foreground="blue", 
                              font=("Courier", 12, "bold"))

# Tag uygulama
self.text_widget.tag_add("token_anahtar_kelime", "1.5", "1.8")
```

### Event Handling

Gerçek zamanlı güncelleme için event binding:

```python
self.text_editor.bind('<KeyRelease>', self.metin_degisti)
self.text_editor.bind('<Button-1>', self.metin_degisti)
```

Bu dokümantasyon, projenin tüm teknik detaylarını ve kullanım senaryolarını kapsamlı şekilde açıklar. 

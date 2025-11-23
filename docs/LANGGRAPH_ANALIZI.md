# LangGraph Yapısı Analizi ve Öğretici Kılavuz

## 🎯 LangGraph Yapısı Analizi ve Puanlama

### Genel Puan: **8.5/10**

**Güçlü Yönler:**
- ✅ **State Management (10/10)**: TypedDict kullanımı mükemmel - type-safe, tahmin edilebilir
- ✅ **Modülerlik (9/10)**: Her node ayrı dosya, temiz separation of concerns
- ✅ **Conditional Routing (9/10)**: Intent'e göre dinamik yönlendirme
- ✅ **Error Handling (8/10)**: Try-catch blokları ve error tracking
- ✅ **LLM Kullanımı (9/10)**: Sadece gerektiğinde (intent + itinerary), routing'de değil

**İyileştirilebilir Yönler:**
- ⚠️ **Parallelization (6/10)**: Sequential chain var, gerçek parallellik yok
- ⚠️ **Async Handling (7/10)**: nest_asyncio kullanımı hacky, native async olmalı
- ⚠️ **Testing (N/A)**: Test coverage görünmüyor

---

## 📚 LangGraph Nasıl Çalışıyor? - Öğretici Anlatım

### 🔹 Temel Konsept: State Machine (Durum Makinesi)

LangGraph, **bir durum (state) objesini farklı fonksiyonlar (nodes) arasında dolaştıran bir pipeline**'dır. Klasik prosedürel koddan farkı:

```python
# ❌ Klasik Kod (Statik)
def travel_planner(query):
    intent = classify(query)
    if intent == "plan_trip":
        flights = search_flights()
        hotels = search_hotels()
        return create_itinerary(flights, hotels)

# ✅ LangGraph (Dinamik)
workflow = StateGraph(TravelPlannerState)
workflow.add_node("classify", classify_node)
workflow.add_node("flights", flight_node)
workflow.add_conditional_edges("classify", route_function, {...})
```

**Fark nedir?**
- Klasik kod: Hard-coded if/else, değiştirmek zor
- LangGraph: Graph yapısı, node ekle/çıkar, kolayca değiştir

---

### 🔹 Kod Nasıl Çalışıyor: 5 Adımlı Süreç

#### **Adım 1: State Tanımı (schemas/state.py)**

State, tüm workflow boyunca taşınan veri yapısı:

```python
class TravelPlannerState(TypedDict):
    # Girdiler
    user_query: str
    origin: Optional[str]
    destination: Optional[str]

    # Routing bayrakları
    intent: str  # "plan_trip", "search_flights", vs.
    requires_flights: bool
    requires_hotels: bool

    # Sonuçlar
    flight_options: List[FlightOption]
    hotel_options: List[HotelOption]
    itinerary: str
```

**Burada kritik nokta:** Her node bu state'i okur, bir kısmını değiştirir, sonraki node'a gönderir.

---

#### **Adım 2: Node'lar (nodes/ klasörü)**

Her node, **saf bir fonksiyon** (pure function):

```python
async def classify_intent_node(state, llm) -> Dict[str, Any]:
    # State'den oku
    user_query = state.get("user_query")

    # LLM'e sor
    result = await llm.ainvoke(prompt)

    # State güncellemelerini döndür
    return {
        "intent": "plan_trip",
        "requires_flights": True,
        "requires_hotels": True,
        "completed_steps": ["intent_classification"]
    }
```

**Önemli detaylar:**
- Node, state'i direkt değiştirmez (immutable pattern)
- Sadece güncellemeleri döndürür
- LangGraph bu güncellemeleri state'e merge eder

---

#### **Adım 3: Workflow Tanımı (workflows/travel_workflow.py)**

Workflow, node'ları birbirine bağlayan graph:

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(TravelPlannerState)

# Node'ları ekle
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("search_flights", search_flights_node)
workflow.add_node("search_hotels", search_hotels_node)
workflow.add_node("generate_itinerary", generate_itinerary_node)

# Başlangıç noktası
workflow.set_entry_point("classify_intent")

# Kenarları tanımla (edges = bağlantılar)
workflow.add_conditional_edges(
    "classify_intent",
    route_after_intent,  # Routing fonksiyonu
    {
        "parallel_search": "search_flights",
        "end": END
    }
)

workflow.add_edge("search_flights", "search_hotels")
workflow.add_edge("search_hotels", "generate_itinerary")
workflow.add_edge("generate_itinerary", END)
```

**Nasıl çalışır?**
1. `classify_intent` çalışır → state güncellenir
2. `route_after_intent` fonksiyonu state'e bakar
3. Eğer `intent == "plan_trip"` ise → `search_flights`'a git
4. Değilse → `END` (bitir)

---

#### **Adım 4: Conditional Routing (Dinamik Akış)**

Bu kod **statik değil, dinamik**! Çünkü routing fonksiyonları state'e göre karar verir:

```python
def route_after_intent(state: TravelPlannerState) -> str:
    intent = state.get("intent")

    if intent == "general":
        return "end"  # Hiçbir şey yapma

    if intent == "plan_trip":
        return "parallel_search"  # Tüm servisleri çağır

    return "parallel_search"
```

**Örnek Senaryolar:**

| Kullanıcı Sorgusu | Intent | Route | Çalışan Node'lar |
|-------------------|--------|-------|------------------|
| "Merhaba" | general | end | Sadece classify |
| "Tokyo'ya uçuş ara" | search_flights | parallel_search | classify → flights → response |
| "5 günlük Paris tatili planla" | plan_trip | parallel_search | classify → flights → hotels → weather → activities → itinerary |

---

#### **Adım 5: Execution (Çalıştırma)**

```python
planner = TravelPlannerV2(provider="anthropic")

# Kullanıcı isteği
result = await planner.plan_trip(
    "Istanbul'dan Paris'e 3 günlük tatil planla"
)

# Arkada olan:
# 1. Initial state oluştur:
initial_state = {
    "user_query": "Istanbul'dan Paris'e 3 günlük tatil planla",
    "flight_options": [],
    "hotel_options": [],
    ...
}

# 2. Workflow'u çalıştır:
final_state = await workflow.ainvoke(initial_state)

# 3. Sonucu döndür:
print(final_state["itinerary"])
print(final_state["flight_options"])
```

---

### 🔹 Statik mi Dinamik mi?

**Cevap: Hibrit (Hybrid)** 🎭

#### **Statik Kısımlar:**
- Graph yapısı sabittir (compile time'da belli)
- Node'lar kodda tanımlıdır
- Edge'ler (bağlantılar) değişmez

#### **Dinamik Kısımlar:**
- **Routing runtime'da belirlenir** (intent'e göre)
- **Her istek farklı path izleyebilir:**
  - İstek 1: classify → flights → response → END
  - İstek 2: classify → flights → hotels → weather → activities → itinerary → response → END
- **State her çalıştırmada farklıdır**

---

### 🔹 Gerçek Hayat Örneği

```
Kullanıcı: "Istanbul'dan Paris'e 3 gecelik ucuz otel bul"

┌──────────────────────────────────────────────────┐
│ STEP 1: classify_intent_node                     │
│ Input State: { user_query: "..." }              │
│ LLM: "Bu hotel arama isteği"                    │
│ Output: { intent: "search_hotels",              │
│           requires_hotels: true,                 │
│           requires_flights: false,               │
│           destination: "Paris" }                 │
└──────────────────────────────────────────────────┘
                     ↓
        route_after_intent() kontrol eder
                     ↓
┌──────────────────────────────────────────────────┐
│ STEP 2: search_flights_node                      │
│ if not state["requires_flights"]:               │
│     return {} # Skip                             │
│ → SKİPLENDİ (requires_flights=false)            │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│ STEP 3: search_hotels_node                       │
│ if not state["requires_hotels"]:                │
│     return {} # Skip                             │
│ → ÇALIŞTI (requires_hotels=true)                │
│ Output: { hotel_options: [                      │
│   {name: "Novotel Paris", price: 120},          │
│   {name: "Ibis Budget", price: 80}              │
│ ]}                                               │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│ STEP 4: check_weather_node                       │
│ → SKİPLENDİ                                      │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│ STEP 5: search_activities_node                   │
│ → SKİPLENDİ                                      │
└──────────────────────────────────────────────────┘
                     ↓
        route_after_parallel_search()
                     ↓
┌──────────────────────────────────────────────────┐
│ STEP 6: generate_response_node                   │
│ "İşte Paris için 3 gecelik otel seçenekleri:    │
│  1. Novotel Paris - €120/gece                    │
│  2. Ibis Budget - €80/gece (en ucuz)"           │
└──────────────────────────────────────────────────┘
                     ↓
                    END
```

---

### 🔹 Neden LangGraph? V1 ile Karşılaştırma

**V1 (DeepAgent) Problemi:**
```python
# Her routing kararı LLM'e sorar (pahalı!)
supervisor: "Hangi agent'a gideyim?"
llm: "Flight agent'a git"
supervisor: "Şimdi ne yapayım?"
llm: "Hotel agent'a git"
supervisor: "Şimdi?"
llm: "Itinerary agent'a git"

# 12 LLM çağrısı, 20 saniye, $0.126
```

**V2 (LangGraph) Çözümü:**
```python
# Routing Python kodu ile (ücretsiz!)
if intent == "plan_trip":
    go_to("search_flights")

# Sadece 2 LLM çağrısı (intent + itinerary), 4 saniye, $0.021
```

---

### 🎓 Özet: 3 Kritik Nokta

1. **State-Driven:** Her şey state'te saklanır, node'lar state'i dönüştürür
2. **Declarative Graph:** Workflow tanımı (add_node, add_edge) vs execution ayrı
3. **Runtime Routing:** Conditional edges sayesinde her istek farklı path izleyebilir

**Analoji:** LangGraph = Tren rayları
- Raylar sabittir (graph yapısı)
- Ama makas noktaları vardır (conditional edges)
- Tren hangi yöne gideceğini runtime'da belirler (state bazlı)

---

## 🎬 Desteklenen Senaryolar

### ✅ Tam Desteklenen Senaryolar (1-15)

#### **1. Tam Seyahat Planlaması**
```
Kullanıcı: "Istanbul'dan Paris'e 5 günlük tatil planla, 2 kişi, bütçe $3000"

Akış: classify → flights → hotels → weather → activities → itinerary → response → END

Sonuç:
- Uçuş seçenekleri (gidiş-dönüş)
- Otel önerileri (4 gece)
- Hava durumu tahmini
- Aktivite önerileri
- Günlük itinerary
- Bütçe analizi
```

#### **2. Sadece Uçuş Arama**
```
Kullanıcı: "New York'tan Londra'ya uçuş ara, 15 Haziran"

Akış: classify → flights → (hotels skip) → (weather skip) → (activities skip) → response → END

Sonuç:
- Sadece uçuş seçenekleri
- Fiyat karşılaştırması
- Farklı havayolları
```

#### **3. Sadece Otel Arama**
```
Kullanıcı: "Tokyo'da 3 gecelik 4 yıldızlı otel"

Akış: classify → (flights skip) → hotels → (weather skip) → (activities skip) → response → END

Sonuç:
- Otel seçenekleri
- Rating ve amenities
- Fiyat aralıkları
```

#### **4. Hava Durumu Sorgusu**
```
Kullanıcı: "Barcelona'da Mart ayında hava nasıl olur?"

Akış: classify → (flights skip) → (hotels skip) → weather → (activities skip) → response → END

Sonuç:
- Hava durumu tahmini
- Sıcaklık aralıkları
- Yağış olasılığı
- Paket önerileri
```

#### **5. Aktivite Önerileri**
```
Kullanıcı: "Roma'da yapılacak şeyler neler?"

Akış: classify → (flights skip) → (hotels skip) → (weather skip) → activities → response → END

Sonuç:
- Müzeler
- Restoranlar
- Turistik yerler
- Fiyat ve süre bilgileri
```

#### **6. Bütçe Odaklı Planlama**
```
Kullanıcı: "Berlin'e $1000 bütçeyle 3 günlük tatil"

Akış: classify → flights (budget filter) → hotels (budget filter) → weather → activities (free/cheap) → itinerary → response → END

Sonuç:
- Bütçeye uygun uçuşlar
- Ekonomik oteller
- Ücretsiz/ucuz aktiviteler
- Kalan bütçe hesabı
```

#### **7. Tarih Esnekliği ile Arama**
```
Kullanıcı: "Kasım ayında bir haftalık sıcak bir yere gitmek istiyorum"

Akış: classify → flights (flexible dates) → hotels → weather → activities → itinerary → response → END

Sonuç:
- Sıcak destinasyonlar
- Farklı tarih seçenekleri
- Fiyat karşılaştırması
```

#### **8. Özel Tercihlerle Planlama**
```
Kullanıcı: "Business class uçuş, 5 yıldızlı otel, spa aktiviteleri istiyorum"

Akış: classify (preferences extract) → flights (business class) → hotels (5 star) → weather → activities (spa filter) → itinerary → response → END

Sonuç:
- Business class uçuşlar
- Lüks oteller
- Spa ve wellness aktiviteleri
```

#### **9. Aile Tatili Planlaması**
```
Kullanıcı: "4 kişilik aile için Disneyland Paris tatili, 5 gün"

Akış: classify → flights (4 passengers) → hotels (family rooms) → weather → activities (kid-friendly) → itinerary → response → END

Sonuç:
- Aile dostu oteller
- Çocuk aktiviteleri
- Gruplar için indirimler
```

#### **10. Gidiş-Dönüş Olmadan (One-way)**
```
Kullanıcı: "Los Angeles'a tek yön uçuş"

Akış: classify → flights (one-way) → (hotels skip) → (weather skip) → (activities skip) → response → END

Sonuç:
- Sadece gidiş uçuşları
- Tek yön fiyatları
```

#### **11. Çok Kısa Kaçamak (Weekend Trip)**
```
Kullanıcı: "Bu hafta sonu Amsterdam'a kaçış"

Akış: classify → flights (2 days) → hotels (2 nights) → weather → activities → itinerary → response → END

Sonuç:
- 2 günlük yoğun itinerary
- Son dakika otelleri
- Must-see yerler
```

#### **12. İş Seyahati**
```
Kullanıcı: "Berlin'e iş seyahati, conference için 3 gün"

Akış: classify (business intent) → flights (flexible times) → hotels (near conference) → weather → activities (networking) → itinerary → response → END

Sonuç:
- İş seyahati odaklı uçuşlar
- Merkezi oteller
- Networking mekanları
```

#### **13. Mevsimsel Tatil**
```
Kullanıcı: "Kış kayağı için Alpler'e gitmek istiyorum"

Akış: classify (winter sports) → flights → hotels (ski resorts) → weather (snow forecast) → activities (skiing) → itinerary → response → END

Sonuç:
- Kayak merkezleri
- Kar durumu
- Kayak aktiviteleri
```

#### **14. Öğrenci Bütçesi**
```
Kullanıcı: "Backpacking için Güneydoğu Asya, $500 bütçe"

Akış: classify → flights (budget airlines) → hotels (hostels) → weather → activities (free) → itinerary → response → END

Sonuç:
- Ucuz uçuşlar
- Hosteller
- Ücretsiz geziler
```

#### **15. Balayı/Romantik Tatil**
```
Kullanıcı: "Balayı için 7 günlük Maldivler"

Akış: classify (honeymoon) → flights → hotels (romantic) → weather → activities (couples) → itinerary → response → END

Sonuç:
- Romantik oteller
- Çift aktiviteleri
- Özel paketler
```

---

### ⚠️ Kısmi Desteklenen Senaryolar (16-20)

#### **16. Çoklu Destinasyon**
```
Kullanıcı: "Paris, Roma ve Barselona'yı kapsayan 2 haftalık tur"

Mevcut Durum: ❌ Desteklenmez
Neden: State sadece tek origin-destination tutuyor

Gerekli Değişiklik:
- Multi-city state desteği
- Her segment için ayrı flight/hotel search
- Şehir arası transferler
```

#### **17. Tarih Aralığı Karşılaştırması**
```
Kullanıcı: "Tokyo'ya Mart mı Nisan mı gitsem daha ucuz?"

Mevcut Durum: ❌ Desteklenmez
Neden: Tek tarih search yapıyor

Gerekli Değişiklik:
- Parallel date search
- Fiyat comparison node
```

#### **18. Alternatif Havalimanları**
```
Kullanıcı: "New York'a JFK veya Newark, hangisi daha ucuz?"

Mevcut Durum: ❌ Desteklenmez
Neden: Tek origin/destination

Gerekli Değişiklik:
- Multiple airport support
- Airport comparison logic
```

#### **19. Stopover/Layover Planlama**
```
Kullanıcı: "Londra'ya giderken Paris'te 2 gün duraklama yapmak istiyorum"

Mevcut Durum: ❌ Desteklenmez
Neden: Stopover mantığı yok

Gerekli Değişiklik:
- Stopover node
- Multi-segment itinerary
```

#### **20. Grup Rezervasyonu (10+ kişi)**
```
Kullanıcı: "15 kişilik grup için Barcelona"

Mevcut Durum: ⚠️ Kısmi destek
Neden: num_passengers var ama grup indirimleri yok

Gerekli Değişiklik:
- Group booking logic
- Special pricing node
```

---

### ❌ Desteklenmeyen Senaryolar (21-25)

#### **21. Rezervasyon/Ödeme**
```
Kullanıcı: "Bu oteli rezerve et ve kredi kartımla öde"

Mevcut Durum: ❌ Desteklenmez
Neden:
- booking_confirmed var ama sadece placeholder
- Gerçek payment gateway integration yok
- transaction_id dolmuyor

Eksik Node'lar:
- payment_node
- booking_confirmation_node
- payment_gateway_integration
```

#### **22. Dinamik Yeniden Planlama**
```
Kullanıcı: "Uçuşum iptal oldu, alternatif bul"

Mevcut Durum: ❌ Desteklenmez
Neden:
- Workflow her zaman classify'dan başlar
- Ortadan giriş noktası yok
- Mevcut state'i update edip resume edemez

Eksik Özellik:
- Workflow resume capability
- Mid-flow entry points
- State persistence
```

#### **23. Akıllı Öneri/Kişiselleştirme**
```
Kullanıcı: "Geçen sefer gittiğim yerlere benzer bir tatil"

Mevcut Durum: ❌ Desteklenmez
Neden:
- User history yok
- Preference learning yok
- Recommendation engine yok

Eksik Node'lar:
- user_profile_node
- recommendation_engine_node
- preference_learning_node
```

#### **24. Gerçek Zamanlı Fiyat İzleme**
```
Kullanıcı: "Bu rotayı takip et, fiyat düşerse haber ver"

Mevcut Durum: ❌ Desteklenmez
Neden:
- Workflow one-shot execution
- Background monitoring yok
- Alert sistemi yok

Eksik Özellikler:
- Price tracking
- Notification system
- Scheduled re-execution
```

#### **25. Karmaşık Filtreler ve Sıralama**
```
Kullanıcı: "En az 2 yıldızlı, havaalanına 5km içinde, ücretsiz kahvaltılı, en ucuzdan pahalıya sırala"

Mevcut Durum: ⚠️ Kısmi destek
Neden:
- Hotel rating filter var
- Ama kompleks AND/OR filtreleri yok
- Sorting logic basit (sadece price/rating)

Gerekli Değişiklik:
- Advanced filter node
- Custom sorting strategies
```

---

## 🚫 Akış Kısıtlamaları ve Limitler

### **1. Tek Yönlü Akış (No Backward Flow)**
```
Mevcut: classify → flights → hotels → weather → activities → itinerary → END

Desteklenmeyen:
- activities → flights (aktivite seçince uçuşu değiştir)
- hotels → weather (hava kötüyse otel değiştir)
- itinerary → flights (bütçe aşarsa ucuz uçuş bul)

Sebep: LangGraph döngüsüz (acyclic) graph kullanıyor
```

### **2. Ortadan Giriş Yapılamaz**
```
Desteklenmeyen:
result = await planner.resume_from("search_hotels", existing_state)

Sebep:
- Entry point sadece classify_intent
- set_entry_point sadece 1 kez çağrılıyor
- State persistence yok

Kullanım Senaryosu:
- Kullanıcı önce uçuş bulmuş
- Sonra gelip "şimdi otel bul" diyor
- Sistem tüm workflow'u baştan çalıştırıyor
```

### **3. Koşullu Dallanma Sınırlı**
```
Mevcut:
- route_after_intent: 2 yol (parallel_search veya end)
- route_after_parallel_search: 2 yol (itinerary veya end)

Desteklenmeyen:
- Multi-way branching (3+ yol)
- Dynamic node selection (runtime'da node ekle/çıkar)

Örnek İhtiyaç:
if budget > 5000:
    goto luxury_search_node
elif budget > 2000:
    goto standard_search_node
else:
    goto budget_search_node
```

### **4. Paralel Execution Fake**
```
Kod:
workflow.add_edge("search_flights", "search_hotels")
workflow.add_edge("search_hotels", "check_weather")
workflow.add_edge("check_weather", "search_activities")

Gerçek: Sequential (sıralı çalışıyor)

Gerçek Paralel Olması İçin:
from langgraph.graph import ParallelNode

parallel_node = ParallelNode([
    search_flights_node,
    search_hotels_node,
    check_weather_node
])
```

### **5. Error Recovery Yok**
```
Mevcut:
try:
    result = search_flights()
except:
    errors.append("Flight error")
    return {"errors": errors}  # Sonra da workflow devam ediyor

Desteklenmeyen:
- Retry logic (3 kez dene)
- Fallback node (flight fail olursa alternatif api)
- Compensation (transaction rollback)

Örnek İhtiyaç:
if flight_search_fails:
    retry(3, exponential_backoff)
    if still_fails:
        try_alternative_api()
```

---

## 📊 Senaryo Özet Tablosu

| # | Senaryo Tipi | Destek Durumu | Node'lar | Eksik Özellik |
|---|--------------|---------------|----------|---------------|
| 1 | Tam seyahat planı | ✅ Tam | Tümü | - |
| 2 | Sadece uçuş | ✅ Tam | classify, flights, response | - |
| 3 | Sadece otel | ✅ Tam | classify, hotels, response | - |
| 4 | Hava durumu | ✅ Tam | classify, weather, response | - |
| 5 | Aktiviteler | ✅ Tam | classify, activities, response | - |
| 6 | Bütçe odaklı | ✅ Tam | Tümü + budget filter | - |
| 7 | Tarih esnekliği | ✅ Tam | Tümü | - |
| 8 | Özel tercihler | ✅ Tam | Tümü + preferences | - |
| 9 | Aile tatili | ✅ Tam | Tümü + family filters | - |
| 10 | One-way uçuş | ✅ Tam | classify, flights | - |
| 11 | Weekend trip | ✅ Tam | Tümü | - |
| 12 | İş seyahati | ✅ Tam | Tümü | - |
| 13 | Mevsimsel | ✅ Tam | Tümü | - |
| 14 | Öğrenci bütçesi | ✅ Tam | Tümü | - |
| 15 | Balayı | ✅ Tam | Tümü | - |
| 16 | Multi-city | ❌ Yok | - | Multi-destination support |
| 17 | Tarih karşılaştırma | ❌ Yok | - | Parallel date search |
| 18 | Alternatif havalimanı | ❌ Yok | - | Multi-airport logic |
| 19 | Stopover | ❌ Yok | - | Stopover planning |
| 20 | Grup rezervasyon | ⚠️ Kısmi | Tümü | Group pricing logic |
| 21 | Rezervasyon/Ödeme | ❌ Yok | - | payment_node, booking_node |
| 22 | Yeniden planlama | ❌ Yok | - | Resume capability |
| 23 | Kişiselleştirme | ❌ Yok | - | User profile, ML recommendations |
| 24 | Fiyat izleme | ❌ Yok | - | Background monitoring |
| 25 | Kompleks filter | ⚠️ Kısmi | search nodes | Advanced filtering |

---

## 🎯 Sonuç ve Öneriler

### **Güçlü Yanlar:**
1. ✅ Temel seyahat senaryolarını (1-15) mükemmel destekliyor
2. ✅ Intent-based routing çok esnek
3. ✅ Node'lar birbirinden bağımsız (modüler)
4. ✅ State yönetimi temiz ve anlaşılır

### **Geliştirilmesi Gerekenler:**
1. ❌ Multi-city/multi-destination support
2. ❌ Gerçek paralel execution
3. ❌ Resume/mid-flow entry capability
4. ❌ Booking ve payment integration
5. ❌ Retry ve fallback mekanizmaları

### **Mimari Öneriler:**
1. **ParallelNode kullan:** Flights, hotels, weather gerçekten paralel çalışsın
2. **Cycles ekle:** User feedback → re-search flow'u için
3. **Checkpointing:** State'i kaydet, resume et
4. **Dynamic routing:** Runtime'da yeni node'lar ekleyebilme
5. **Error recovery:** Retry, fallback, compensation patterns

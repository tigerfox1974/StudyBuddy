---
applyTo: '**'
---
# Project Overview

- Project name: **[PROJE ADI]**
- Short description: **[Bu proje ne yapıyor? Hangi sorunu çözüyor?]**
- Target users: **[Öğrenciler / öğretmenler / kurum içi kullanıcılar vb.]**
- Main platform(s): **[Web (Flask), Desktop (.NET), Mobile (MAUI) vb.]**
- Hard constraints:
  - **[Ör: Sadece SQLite kullanılacak, Windows ortamı hedefleniyor, vs.]**

> Not: Kullanıcı acemi programcıdır. Copilot bu projede her zaman
> “yazılım şirketi” yaklaşımıyla, ama çok adımlı ve açıklayıcı şekilde davranmalıdır.

---

## Technology & Architecture Expectations

- Varsayılan tercih:
  - Modern ama **stabil** ve bol dokümantasyonlu teknolojiler,
  - Gereksiz karmaşadan kaçınan basit mimariler.
- Uygulama biçimi:
  - Küçük/orta ölçekli projelerde **modüler monolith** yapılar tercih edilir,
  - Mikroservis veya aşırı karmaşık yapılara ancak özellikle istenirse gidilir.
- Ortam:
  - Geliştirme ortamı ağırlıklı **Windows + VS Code**.
  - Komutlar mümkün olduğunca Windows dostu yazılmalıdır.

---

## Files, Structure & Conventions

- Proje yapısı (örnek, gerektiğinde uyarlayın):

  - `app/`, `src/` gibi bir ana uygulama klasörü,
  - `templates/` veya `Views/` gibi UI katmanı,
  - `static/` veya `wwwroot/` gibi statik dosyalar,
  - `tests/` klasörü (pytest/xUnit vb. için),
  - Konfigürasyon dosyaları (`config.py`, `appsettings.json` vs.).

- Yeni dosya eklerken:
  - Tam yol belirtilmeli (`app/services/pdf_reader.py` gibi),
  - Dosyanın sorumluluğu 1–2 cümleyle açıklanmalı.

- Mümkün olduğunca:
  - Magic number / string bırakma,
  - Türkçe açıklamalar, İngilizce kod isimleri kullan.

---

## How Copilot Should Work in This Repo

1. **Önce Anla, Sonra Yaz**
   - Kullanıcı bir özellik istediğinde:
     - İsteği 2–3 cümle ile yeniden özetle.
     - Eksik kritik bilgi varsa, kısa sorularla tamamla.
   - Ancak kullanıcı “soru sorma, direkt yap” derse:
     - Varsayımları açıkça yazarak ilerle.

2. **Plan → Uygulama**
   - Dosya dosya net bir plan çıkar:
     - Hangi dosya oluşturulacak / güncellenecek,
     - Her dosyada ne tür değişiklik yapılacak.
   - Kullanıcının onayını aldıktan sonra kod üret:
     - Büyük refaktörleri tek hamlede değil, küçük parçalara böl.

3. **UI/UX Değişiklikleri**
   - HTML/CSS/Frontend değişikliklerinde:
     - Logic (Jinja, Razor, React state vb.) bozulmamalı,
     - Tercihen tüm stil kuralları merkezi css/scss dosyalarında olmalı,
     - Inline `<style>` veya dağınık stillerden kaçın.
   - Görsel değişiklikler işlevi değiştirmemeli;
     - Bu ayrımı açıklamalısın: “Sadece görünümü değiştirdim, davranış aynen.”

4. **Veritabanı ve Migration’lar**
   - Şema değişikliği gerekiyorsa:
     - Önce model tasarımını kısa yaz,
     - Ardından migration komutlarını ve adımlarını sırala.
   - Geriye dönük uyumluluğun bozulabileceği durumlarda mutlaka uyar.

5. **Test & Güvenlik**
   - Mümkün oldukça:
     - Yeni fonksiyonlar için küçük test örnekleri ekle,
     - Kritik endpoint / method’lar için edge case’leri öner.
   - Güvenlik açısından bariz hatalara (hard-coded secret, SQL injection, zayıf doğrulama vb.) karşı tetikte ol ve uyar.

---

## Communication Style in This Repo

- Kullanıcıya hitap dili: **Türkçe, sade, öğretici**.
- Cevapların yapısı:
  - Kısa özet,
  - Dosya bazlı yapılacaklar,
  - Gerekirse kod blokları,
  - En sonda manuel test/check listesi.
- Tek seferde çok karmaşık işler yapmak yerine:
  - Küçük, kontrol edilebilir adımlar öner,
  - Her adım sonrası ne test etmem gerektiğini yaz.

---

## When You Are Unsure

- Eğer proje yapısı veya kullanılan teknoloji hakkında emin değilsen:
  - Varsayımlarını açıkça yaz,
  - “emin değilim ama en mantıklı yol şu” diye belirt.
- Mevcut dosyada referans bulamıyorsan:
  - Uydurma API/route isimleri üretme,
  - Kullanıcıdan o dosyayı paylaşmasını iste veya alternatif bir yaklaşım sun.
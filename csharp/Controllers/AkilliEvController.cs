using Microsoft.AspNetCore.Mvc;
using AkilliEv.Services;
using AkilliEv.Models;

namespace AkilliEv.Controllers
{
    public class AkilliEvController : Controller
    {
        
        private readonly EvKontrolService _evServis;

public AkilliEvController(EvKontrolService evServis)
{
    _evServis = evServis;
}

        // YANGIN DURUMUNU TUTAN DEĞİŞKEN (Static olması önemli, tüm isteklerde aynı değeri korur)
        public static bool YanginVarMi = false;

        public IActionResult Index() => View();

        [HttpPost]
        public JsonResult GirisKontrol(string user, string pass)
        {
            if (user == "admin" && pass == "1234") return Json(new { basarili = true });
            return Json(new { basarili = false });
        }

        // --- YANGIN ALARMI METOTLARI ---

        // 1. Ufuk'un Python kodunun çağıracağı kapı
        [HttpPost]
        public IActionResult AlarmGonder([FromBody] AlarmModel model)
        {
            if (model != null && model.Status == "fire") 
            {
                YanginVarMi = true; // Alarmı aktif et
                return Ok(new { mesaj = "C# tarafında yangın alarmı alındı!" });
            }
            YanginVarMi = false; // Resetle
            return Ok(new { mesaj = "Sistem normale döndü." });
        }

        // 2. Tarayıcının (JS) her 2 saniyede bir soracağı kapı
        [HttpGet]
        public JsonResult YanginDurumuSorgula()
        {
            return Json(new { yangin = YanginVarMi });
        }

        // --- CİHAZ KONTROL METOTLARI ---

        [HttpPost]
        public async Task<JsonResult> IsikKontrol(bool durum)
        {
            string aksiyon = durum ? "on" : "off";
            bool basariliMi = await _evServis.KomutGonderAsync("light", aksiyon);
            return Json(new { mesaj = basariliMi ? (durum ? "Lamba AÇILDI 💡" : "Lamba KAPANDI ⚫") : "Hata: Bağlantı koptu!" });
        }

        [HttpPost]
        public async Task<JsonResult> Havalandirma(bool durum)
        {
            string aksiyon = durum ? "on" : "off";
            bool basariliMi = await _evServis.KomutGonderAsync("fan", aksiyon);
            return Json(new { mesaj = basariliMi ? (durum ? "Fan ÇALIŞIYOR 🌀" : "Fan DURDU 🛑") : "Hata: Bağlantı koptu!" });
        }

        [HttpPost]
        public async Task<JsonResult> GuvenliMod(bool durum)
        {
            string aksiyon = durum ? "on" : "off";
            bool basariliMi = await _evServis.KomutGonderAsync("securitymode", aksiyon);
            return Json(new { mesaj = basariliMi ? (durum ? "GÜVENLİK AKTİF 🛡️" : "GÜVENLİK KAPALI 🔓") : "Hata!" });
        }

        [HttpPost]
        public async Task<JsonResult> KapiKilidi(bool durum)
        {
            string aksiyon = durum ? "lock" : "unlock";
            bool basariliMi = await _evServis.KomutGonderAsync("door", aksiyon);
            return Json(new { mesaj = basariliMi ? (durum ? "KAPI KİLİTLENDİ 🔒" : "KAPI AÇILDI 🔑") : "Hata!" });
        }

        [HttpPost]
        public async Task<JsonResult> KapiDurumuKontrol(bool durum)
        {
            string aksiyon = durum ? "open" : "close";
            bool basariliMi = await _evServis.KomutGonderAsync("door_on", aksiyon);
            return Json(new
            {
                mesaj = basariliMi
                    ? (durum ? "KAPI AÇILDI 🚪" : "KAPI KAPATILDI ✅")
                    : "Hata: Kapı kontrol komutu gönderilemedi!"
            });
        }
        [HttpPost]
public async Task<JsonResult> YanginSistemiKontrol(bool durum)
{
    // Ufuk'un listesindeki firesystem on/off komutu
    string aksiyon = durum ? "on" : "off";
    bool basariliMi = await _evServis.KomutGonderAsync("firesystem", aksiyon);
    
    return Json(new { 
        mesaj = basariliMi 
            ? (durum ? "Otomatik Yangın Koruması AKTİF ✅" : "Otomatik Yangın Koruması DEVRE DIŞI ⚪") 
            : "Hata: Cihazla iletişim kurulamadı!" 
    });
}
// 3. Tüm cihazların durumunu Python'dan çeker
       [HttpGet]
public async Task<JsonResult> CihazDurumlariniGetir()
{
    var durum = await _evServis.DurumGetirAsync();
    if (durum != null)
    {
        var parsed = System.Text.Json.JsonSerializer.Deserialize<object>(durum);
        return Json(parsed);
    }
    return Json(new { hata = "Python'a ulaşılamıyor" });
}
    }

    // Python'dan gelen veriyi karşılamak için gereken model
    
}
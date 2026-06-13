using System.Net.Http.Json;

namespace AkilliEv.Services
{
    public class EvKontrolService
    {
        private static readonly HttpClient _httpClient = new HttpClient();
        private const string PythonUrl = "http://127.0.0.1:8000";

        public async Task<bool> KomutGonderAsync(string cihaz, string islem)
        {
            try
            {
                var paket = new { device = cihaz, action = islem };
                var cevap = await _httpClient.PostAsJsonAsync($"{PythonUrl}/device", paket);
                return cevap.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        public async Task<string?> DurumGetirAsync()
        {
            try
            {
                var cevap = await _httpClient.GetAsync($"{PythonUrl}/status");
                if (cevap.IsSuccessStatusCode)
                    return await cevap.Content.ReadAsStringAsync();
                return null;
            }
            catch
            {
                return null;
            }
        }
    }
}
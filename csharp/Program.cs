/*var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRouting();

app.UseAuthorization();

app.MapStaticAssets();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();


app.Run();
*/
using AkilliEv.Services; // Servis klasörünü tanıması için şart

var builder = WebApplication.CreateBuilder(args);

// 1. SERVİS KAYDI: Sistemin EvKontrolService'i tanımasını sağlıyoruz.
// AddSingleton kullanıyoruz çünkü HttpClient'ın uygulama boyunca tek bir örneği olması performansı artırır.
builder.Services.AddSingleton<EvKontrolService>();

// 2. JSON AYARI: Python'dan gelen büyük/küçük harf farklarını (Status vs status) sorunsuz okumak için.
builder.Services.AddControllersWithViews()
    .AddJsonOptions(options => {
        options.JsonSerializerOptions.PropertyNamingPolicy = null;
    });

var app = builder.Build();

// Geliştirme ortamı kontrolleri
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

// app.UseHttpsRedirection(); // Ufuk ile yerel ağda (localhost) çalışırken bazen sorun çıkarabilir, gerekirse yorum satırı yapabilirsin.
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

// 3. VARSAYILAN SAYFA AYARI: 
// Uygulama açılır açılmaz senin AkilliEv panelinin gelmesi için Home yerine AkilliEv yazdık.
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=AkilliEv}/{action=Index}/{id?}");

app.Run();
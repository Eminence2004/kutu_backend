from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from accounts.views_stats import stats_json
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required

APK_URL = "https://expo.dev/artifacts/eas/5idGTUH6ycxc2tGuKSMdqy.apk"

def landing(request):
    return HttpResponse("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kutu — KsTU Campus Hub</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    :root {
      --bg: #0a0a0f; --surface: #12121a; --border: rgba(255,255,255,0.07);
      --primary: #4f6ef7; --accent: #f7704f; --text: #f0f0f5; --muted: #6b6b80;
    }
    html { scroll-behavior: smooth; }
    body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }
    body::before {
      content: ''; position: fixed; inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
      pointer-events: none; z-index: 0; opacity: 0.4;
    }
    .blob { position: fixed; border-radius: 50%; filter: blur(100px); opacity: 0.12; pointer-events: none; z-index: 0; }
    .blob-1 { width: 600px; height: 600px; background: var(--primary); top: -200px; left: -200px; }
    .blob-2 { width: 400px; height: 400px; background: var(--accent); bottom: -100px; right: -100px; }
    .wrap { position: relative; z-index: 1; max-width: 960px; margin: 0 auto; padding: 0 24px; }
    nav { position: relative; z-index: 10; padding: 24px 0; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
    .nav-logo { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 22px; letter-spacing: -0.5px; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero { padding: 100px 0 80px; text-align: center; }
    .hero-tag { display: inline-flex; align-items: center; gap: 8px; background: rgba(79,110,247,0.1); border: 1px solid rgba(79,110,247,0.25); border-radius: 100px; padding: 6px 16px; font-size: 12px; font-weight: 500; color: #8ba4fb; margin-bottom: 32px; animation: fadeUp 0.6s ease both; }
    .hero-tag::before { content: '●'; font-size: 8px; color: #4f6ef7; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    h1 { font-family: 'Syne', sans-serif; font-size: clamp(42px, 8vw, 76px); font-weight: 800; line-height: 1.05; letter-spacing: -2px; margin-bottom: 24px; animation: fadeUp 0.6s 0.1s ease both; }
    h1 span { background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { font-size: 18px; color: var(--muted); max-width: 500px; margin: 0 auto 48px; line-height: 1.6; font-weight: 300; animation: fadeUp 0.6s 0.2s ease both; }
    .hero-cta { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; animation: fadeUp 0.6s 0.3s ease both; }
    .btn-primary { display: inline-flex; align-items: center; gap: 10px; background: var(--primary); color: #fff; text-decoration: none; font-weight: 700; font-size: 15px; padding: 16px 32px; border-radius: 14px; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 0 40px rgba(79,110,247,0.3); cursor: pointer; border: none; font-family: inherit; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 40px rgba(79,110,247,0.45); }
    .btn-secondary { display: inline-flex; align-items: center; gap: 10px; background: var(--surface); color: var(--text); text-decoration: none; font-weight: 600; font-size: 15px; padding: 16px 32px; border-radius: 14px; border: 1px solid var(--border); transition: transform 0.2s, border-color 0.2s; }
    .btn-secondary:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.2); }

    /* Phone mockup with screenshot */
    .phone-wrap { margin: 80px auto 0; max-width: 260px; animation: fadeUp 0.6s 0.4s ease both; }
    .phone { background: #1a1a2e; border: 2px solid rgba(255,255,255,0.1); border-radius: 44px; padding: 14px 12px; box-shadow: 0 40px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.05), inset 0 0 0 1px rgba(255,255,255,0.03); }
    .phone-notch { width: 80px; height: 22px; background: #1a1a2e; border-radius: 0 0 16px 16px; margin: 0 auto 8px; position: relative; z-index: 2; }
    .phone-screen { border-radius: 32px; height: 460px; overflow: hidden; position: relative; }
    .phone-screen img { width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 32px; display: block; }

    /* Download modal */
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(8px); }
    .modal-overlay.open { display: flex; }
    .modal { background: #12121a; border: 1px solid rgba(255,255,255,0.1); border-radius: 28px; padding: 40px 32px; max-width: 400px; width: 90%; text-align: center; animation: modalIn 0.3s ease; }
    @keyframes modalIn { from { opacity:0; transform: scale(0.9) translateY(20px); } to { opacity:1; transform: scale(1) translateY(0); } }
    .modal-icon { font-size: 48px; margin-bottom: 16px; }
    .modal-title { font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 800; margin-bottom: 8px; }
    .modal-sub { color: var(--muted); font-size: 14px; line-height: 1.6; margin-bottom: 28px; }
    .modal-info { background: rgba(79,110,247,0.08); border: 1px solid rgba(79,110,247,0.2); border-radius: 14px; padding: 14px 16px; margin-bottom: 24px; }
    .modal-info-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
    .modal-info-row:last-child { margin-bottom: 0; }
    .modal-info-label { color: var(--muted); }
    .modal-info-value { color: var(--text); font-weight: 600; }
    .modal-btns { display: flex; flex-direction: column; gap: 10px; }
    .btn-download { display: flex; align-items: center; justify-content: center; gap: 10px; background: var(--primary); color: #fff; text-decoration: none; font-weight: 700; font-size: 16px; padding: 16px; border-radius: 14px; transition: transform 0.2s; box-shadow: 0 0 30px rgba(79,110,247,0.3); }
    .btn-download:hover { transform: translateY(-2px); }
    .btn-cancel { background: transparent; border: 1px solid var(--border); color: var(--muted); font-size: 14px; padding: 12px; border-radius: 12px; cursor: pointer; font-family: inherit; transition: border-color 0.2s; }
    .btn-cancel:hover { border-color: rgba(255,255,255,0.2); color: var(--text); }

    .features { padding: 100px 0; }
    .section-label { font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: var(--primary); margin-bottom: 16px; }
    .section-title { font-family: 'Syne', sans-serif; font-size: clamp(28px, 5vw, 42px); font-weight: 800; letter-spacing: -1px; margin-bottom: 60px; line-height: 1.1; }
    .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
    .feature-card { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 28px; transition: border-color 0.2s, transform 0.2s; }
    .feature-card:hover { border-color: rgba(79,110,247,0.3); transform: translateY(-4px); }
    .feature-icon { font-size: 32px; margin-bottom: 16px; display: block; }
    .feature-name { font-family: 'Syne', sans-serif; font-size: 17px; font-weight: 700; margin-bottom: 8px; }
    .feature-desc { font-size: 14px; color: var(--muted); line-height: 1.6; }
    .download { padding: 80px 0 120px; text-align: center; }
    .download-card { background: linear-gradient(135deg, rgba(79,110,247,0.1), rgba(247,112,79,0.05)); border: 1px solid rgba(79,110,247,0.2); border-radius: 28px; padding: 60px 40px; }
    .download-title { font-family: 'Syne', sans-serif; font-size: clamp(28px, 5vw, 44px); font-weight: 800; letter-spacing: -1px; margin-bottom: 16px; }
    .download-sub { color: var(--muted); font-size: 16px; margin-bottom: 40px; }
    .platform-note { margin-top: 20px; font-size: 13px; color: var(--muted); }
    .platform-note span { color: var(--text); font-weight: 500; }
    footer { border-top: 1px solid var(--border); padding: 32px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    .footer-text { font-size: 13px; color: var(--muted); }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
    @media (max-width: 600px) { .hero { padding: 60px 0 40px; } .hero-cta { flex-direction: column; align-items: center; } footer { flex-direction: column; text-align: center; } }
  </style>
</head>
<body>
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>

  <!-- Download Modal -->
  <div class="modal-overlay" id="downloadModal">
    <div class="modal">
      <div class="modal-icon">📱</div>
      <h2 class="modal-title">Download Kutu</h2>
      <p class="modal-sub">Get the KsTU Campus Hub app on your Android device. Free for all KsTU students.</p>
      <div class="modal-info">
        <div class="modal-info-row"><span class="modal-info-label">Platform</span><span class="modal-info-value">Android APK</span></div>
        <div class="modal-info-row"><span class="modal-info-label">Version</span><span class="modal-info-value">1.0.0</span></div>
        <div class="modal-info-row"><span class="modal-info-label">Access</span><span class="modal-info-value">KsTU Students Only</span></div>
        <div class="modal-info-row"><span class="modal-info-label">Price</span><span class="modal-info-value">Free</span></div>
      </div>
      <div class="modal-btns">
        <a href="https://expo.dev/artifacts/eas/5idGTUH6ycxc2tGuKSMdqy.apk" class="btn-download" download>
          ⬇ Download APK Now
        </a>
        <button class="btn-cancel" onclick="closeModal()">Maybe later</button>
      </div>
    </div>
  </div>

  <div class="wrap">
    <nav>
      <span class="nav-logo">Kutu</span>
    </nav>

    <section class="hero">
      <div class="hero-tag">KsTU Campus Hub · Now Live</div>
      <h1>Your campus,<br><span>in your pocket.</span></h1>
      <p class="hero-sub">Navigate KsTU, connect with students, share vibes, and find everything on campus — all in one app.</p>
      <div class="hero-cta">
        <button class="btn-primary" onclick="openModal()">⬇ Download APK</button>
        <a href="/api/navigation/locations/" class="btn-secondary">View API ↗</a>
      </div>

      <!-- Phone mockup with real screenshot -->
      <div class="phone-wrap">
        <div class="phone">
          <div class="phone-notch"></div>
          <div class="phone-screen">
            <img src="https://res.cloudinary.com/dbe0l5g7w/image/upload/kutu_app_screenshot.png"
                 onerror="this.style.display='none'; this.parentElement.style.background='linear-gradient(180deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%)'; this.parentElement.innerHTML += '<div style=&quot;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:12px&quot;><div style=&quot;font-family:Syne,sans-serif;font-size:42px;font-weight:800;background:linear-gradient(135deg,#4f6ef7,#f7704f);-webkit-background-clip:text;-webkit-text-fill-color:transparent&quot;>KUTU</div><div style=&quot;color:rgba(255,255,255,0.4);font-size:12px&quot;>KsTU Campus Hub</div></div>'"
                 alt="Kutu App Screenshot" />
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <p class="section-label">What's inside</p>
      <h2 class="section-title">Everything you need<br>on campus.</h2>
      <div class="features-grid">
        <div class="feature-card"><span class="feature-icon">🗺️</span><div class="feature-name">Campus Navigation</div><p class="feature-desc">Turn-by-turn directions to any building, gate, or office on campus with real-time GPS tracking.</p></div>
        <div class="feature-card"><span class="feature-icon">💬</span><div class="feature-name">Student Chat</div><p class="feature-desc">Private messaging and group chats with fellow KsTU students. Stay connected on campus.</p></div>
        <div class="feature-card"><span class="feature-icon">📸</span><div class="feature-name">Campus Vibes</div><p class="feature-desc">Share moments, discover what's happening around campus, and explore trending posts.</p></div>
        <div class="feature-card"><span class="feature-icon">🔍</span><div class="feature-name">Find Friends</div><p class="feature-desc">Search and connect with other students. Build your campus network from day one.</p></div>
        <div class="feature-card"><span class="feature-icon">🚻</span><div class="feature-name">Nearby Facilities</div><p class="feature-desc">Find the nearest washrooms, ATMs, and campus facilities with distance and walking time.</p></div>
        <div class="feature-card"><span class="feature-icon">🎓</span><div class="feature-name">KsTU Exclusive</div><p class="feature-desc">Built specifically for Kumasi Technical University students. Your campus, your app.</p></div>
      </div>
    </section>

    <section class="download">
      <div class="download-card">
        <h2 class="download-title">Ready to explore<br>your campus?</h2>
        <p class="download-sub">Download the Kutu app and get started in minutes.</p>
        <button class="btn-primary" onclick="openModal()" style="margin: 0 auto;">⬇ Download for Android</button>
        <p class="platform-note">Android APK · <span>KsTU Students Only</span> · Free</p>
      </div>
    </section>

    <footer>
      <span class="footer-text">© 2026 Kutu — KsTU Campus Hub</span>
      <span class="footer-text">Built for KsTU students 🎓</span>
    </footer>
  </div>

  <script>
    function openModal() {
      document.getElementById('downloadModal').classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function closeModal() {
      document.getElementById('downloadModal').classList.remove('open');
      document.body.style.overflow = '';
    }
    document.getElementById('downloadModal').addEventListener('click', function(e) {
      if (e.target === this) closeModal();
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') closeModal();
    });
  </script>
</body>
</html>""")


urlpatterns = [
    path('', landing, name='landing'),
    path('admin/dashboard/', staff_member_required(
        TemplateView.as_view(template_name='admin/dashboard.html')
    ), name='admin-dashboard'),
    path('admin/stats-json/', stats_json, name='admin-stats-json'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('accounts.urls')),
    path('api/navigation/', include('navigation.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in production via Django
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from accounts.views_stats import stats_json
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required


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
      --bg: #0a0a0f;
      --surface: #12121a;
      --border: rgba(255,255,255,0.07);
      --primary: #4f6ef7;
      --accent: #f7704f;
      --text: #f0f0f5;
      --muted: #6b6b80;
      --glow: rgba(79,110,247,0.15);
    }

    html { scroll-behavior: smooth; }

    body {
      font-family: 'DM Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* ── Noise overlay ── */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
      pointer-events: none;
      z-index: 0;
      opacity: 0.4;
    }

    /* ── Gradient blob ── */
    .blob {
      position: fixed;
      border-radius: 50%;
      filter: blur(100px);
      opacity: 0.12;
      pointer-events: none;
      z-index: 0;
    }
    .blob-1 { width: 600px; height: 600px; background: var(--primary); top: -200px; left: -200px; }
    .blob-2 { width: 400px; height: 400px; background: var(--accent); bottom: -100px; right: -100px; }

    /* ── Layout ── */
    .wrap {
      position: relative;
      z-index: 1;
      max-width: 960px;
      margin: 0 auto;
      padding: 0 24px;
    }

    /* ── Nav ── */
    nav {
      position: relative;
      z-index: 10;
      padding: 24px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
    }
    .nav-logo {
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: 22px;
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .nav-link {
      color: var(--muted);
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      transition: color 0.2s;
    }
    .nav-link:hover { color: var(--text); }

    /* ── Hero ── */
    .hero {
      padding: 100px 0 80px;
      text-align: center;
    }
    .hero-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(79,110,247,0.1);
      border: 1px solid rgba(79,110,247,0.25);
      border-radius: 100px;
      padding: 6px 16px;
      font-size: 12px;
      font-weight: 500;
      color: #8ba4fb;
      margin-bottom: 32px;
      animation: fadeUp 0.6s ease both;
    }
    .hero-tag::before { content: '●'; font-size: 8px; color: #4f6ef7; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

    h1 {
      font-family: 'Syne', sans-serif;
      font-size: clamp(42px, 8vw, 76px);
      font-weight: 800;
      line-height: 1.05;
      letter-spacing: -2px;
      margin-bottom: 24px;
      animation: fadeUp 0.6s 0.1s ease both;
    }
    h1 span {
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-sub {
      font-size: 18px;
      color: var(--muted);
      max-width: 500px;
      margin: 0 auto 48px;
      line-height: 1.6;
      font-weight: 300;
      animation: fadeUp 0.6s 0.2s ease both;
    }

    .hero-cta {
      display: flex;
      gap: 14px;
      justify-content: center;
      flex-wrap: wrap;
      animation: fadeUp 0.6s 0.3s ease both;
    }

    .btn-primary {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: var(--primary);
      color: #fff;
      text-decoration: none;
      font-weight: 700;
      font-size: 15px;
      padding: 16px 32px;
      border-radius: 14px;
      transition: transform 0.2s, box-shadow 0.2s;
      box-shadow: 0 0 40px rgba(79,110,247,0.3);
    }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 40px rgba(79,110,247,0.45); }

    .btn-secondary {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: var(--surface);
      color: var(--text);
      text-decoration: none;
      font-weight: 600;
      font-size: 15px;
      padding: 16px 32px;
      border-radius: 14px;
      border: 1px solid var(--border);
      transition: transform 0.2s, border-color 0.2s;
    }
    .btn-secondary:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.2); }

    /* ── Phone mockup ── */
    .phone-wrap {
      margin: 80px auto 0;
      max-width: 280px;
      animation: fadeUp 0.6s 0.4s ease both;
    }
    .phone {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 40px;
      padding: 16px;
      box-shadow: 0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05);
    }
    .phone-screen {
      background: #1a0533;
      border-radius: 28px;
      height: 420px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      overflow: hidden;
      position: relative;
    }
    .phone-screen::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(circle at 50% 40%, rgba(79,110,247,0.2), transparent 60%);
    }
    .phone-logo {
      font-family: 'Syne', sans-serif;
      font-size: 48px;
      font-weight: 800;
      background: linear-gradient(135deg, #4f6ef7, #f7704f);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      position: relative;
      z-index: 1;
    }
    .phone-tagline {
      color: rgba(255,255,255,0.5);
      font-size: 12px;
      position: relative;
      z-index: 1;
    }
    .phone-dots {
      display: flex;
      gap: 6px;
      position: relative;
      z-index: 1;
    }
    .phone-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.2); }
    .phone-dot.active { background: var(--primary); }

    /* ── Features ── */
    .features {
      padding: 100px 0;
    }
    .section-label {
      font-family: 'Syne', sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--primary);
      margin-bottom: 16px;
    }
    .section-title {
      font-family: 'Syne', sans-serif;
      font-size: clamp(28px, 5vw, 42px);
      font-weight: 800;
      letter-spacing: -1px;
      margin-bottom: 60px;
      line-height: 1.1;
    }
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }
    .feature-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 28px;
      transition: border-color 0.2s, transform 0.2s;
    }
    .feature-card:hover { border-color: rgba(79,110,247,0.3); transform: translateY(-4px); }
    .feature-icon {
      font-size: 32px;
      margin-bottom: 16px;
      display: block;
    }
    .feature-name {
      font-family: 'Syne', sans-serif;
      font-size: 17px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .feature-desc { font-size: 14px; color: var(--muted); line-height: 1.6; }

    /* ── Download section ── */
    .download {
      padding: 80px 0 120px;
      text-align: center;
    }
    .download-card {
      background: linear-gradient(135deg, rgba(79,110,247,0.1), rgba(247,112,79,0.05));
      border: 1px solid rgba(79,110,247,0.2);
      border-radius: 28px;
      padding: 60px 40px;
    }
    .download-title {
      font-family: 'Syne', sans-serif;
      font-size: clamp(28px, 5vw, 44px);
      font-weight: 800;
      letter-spacing: -1px;
      margin-bottom: 16px;
    }
    .download-sub { color: var(--muted); font-size: 16px; margin-bottom: 40px; }
    .platform-note {
      margin-top: 20px;
      font-size: 13px;
      color: var(--muted);
    }
    .platform-note span { color: var(--text); font-weight: 500; }

    /* ── Footer ── */
    footer {
      border-top: 1px solid var(--border);
      padding: 32px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }
    .footer-text { font-size: 13px; color: var(--muted); }
    .footer-link { color: var(--muted); text-decoration: none; font-size: 13px; }
    .footer-link:hover { color: var(--text); }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 600px) {
      .hero { padding: 60px 0 40px; }
      .hero-cta { flex-direction: column; align-items: center; }
      footer { flex-direction: column; text-align: center; }
    }
  </style>
</head>
<body>
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>

  <div class="wrap">
    <nav>
      <span class="nav-logo">Kutu</span>
      <a href="/admin/" class="nav-link">Admin →</a>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-tag">KsTU Campus Hub · Now Live</div>
      <h1>Your campus,<br><span>in your pocket.</span></h1>
      <p class="hero-sub">Navigate KsTU, connect with students, share vibes, and find everything on campus — all in one app.</p>
      <div class="hero-cta">
        <a href="https://expo.dev/accounts/eminence2004/projects/kutu_frontend/builds/652b5709-504d-4523-af52-c3609a0b1c15" class="btn-primary">
          ⬇ Download APK
        </a>
        <a href="/api/navigation/locations/" class="btn-secondary">
          View API ↗
        </a>
      </div>

      <!-- Phone mockup -->
      <div class="phone-wrap">
        <div class="phone">
          <div class="phone-screen">
            <div class="phone-logo">KUTU</div>
            <div class="phone-tagline">KsTU Campus Hub</div>
            <div class="phone-dots">
              <div class="phone-dot active"></div>
              <div class="phone-dot"></div>
              <div class="phone-dot"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features">
      <p class="section-label">What's inside</p>
      <h2 class="section-title">Everything you need<br>on campus.</h2>
      <div class="features-grid">
        <div class="feature-card">
          <span class="feature-icon">🗺️</span>
          <div class="feature-name">Campus Navigation</div>
          <p class="feature-desc">Turn-by-turn directions to any building, gate, or office on campus with real-time GPS tracking.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">💬</span>
          <div class="feature-name">Student Chat</div>
          <p class="feature-desc">Private messaging and group chats with fellow KsTU students. Stay connected on campus.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">📸</span>
          <div class="feature-name">Campus Vibes</div>
          <p class="feature-desc">Share moments, discover what's happening around campus, and explore trending posts.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">🔍</span>
          <div class="feature-name">Find Friends</div>
          <p class="feature-desc">Search and connect with other students. Build your campus network from day one.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">🚻</span>
          <div class="feature-name">Nearby Facilities</div>
          <p class="feature-desc">Find the nearest washrooms, ATMs, and campus facilities with distance and walking time.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">🎓</span>
          <div class="feature-name">KsTU Exclusive</div>
          <p class="feature-desc">Built specifically for Kumasi Technical University students. Your campus, your app.</p>
        </div>
      </div>
    </section>

    <!-- Download -->
    <section class="download">
      <div class="download-card">
        <h2 class="download-title">Ready to explore<br>your campus?</h2>
        <p class="download-sub">Download the Kutu app and get started in minutes.</p>
        <a href="https://expo.dev/accounts/eminence2004/projects/kutu_frontend/builds/652b5709-504d-4523-af52-c3609a0b1c15" class="btn-primary" style="display:inline-flex;">
          ⬇ Download for Android
        </a>
        <p class="platform-note">Android APK · <span>KsTU Students Only</span> · Free</p>
      </div>
    </section>

    <footer>
      <span class="footer-text">© 2026 Kutu — KsTU Campus Hub</span>
      <a href="/admin/" class="footer-link">Admin Panel</a>
    </footer>
  </div>
</body>
</html>""")


urlpatterns = [
    # ── Landing page ──
    path('', landing, name='landing'),
    # ── Item 6: Stats — MUST come before admin/ catch-all ──
    path('admin/dashboard/', staff_member_required(
        TemplateView.as_view(template_name='admin/dashboard.html')
    ), name='admin-dashboard'),
    path('admin/stats-json/', stats_json, name='admin-stats-json'),
    # ── Django admin ──
    path('admin/', admin.site.urls),
    # ── API ──
    path('api/auth/', include('accounts.urls')),
    path('api/', include('accounts.urls')),
    path('api/navigation/', include('navigation.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
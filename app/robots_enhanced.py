from flask import Blueprint, make_response, request

robots_bp = Blueprint('robots_enhanced', __name__)

@robots_bp.route('/robots.txt')
def robots_txt():
    """Serve comprehensive robots.txt with multilingual SEO directives"""
    robots_content = f"""# Robots.txt for SAML Testing Tool
# Multilingual SAML SSO Testing Tool

User-agent: *
Allow: /

# Allow all language versions
Allow: /en/
Allow: /es/
Allow: /fr/
Allow: /de/
Allow: /pt/
Allow: /ru/
Allow: /ko/
Allow: /ja/
Allow: /zh_Hant/
Allow: /zh_Hans/
Allow: /ar/

# Allow important pages
Allow: /attrs/
Allow: /metadata/

# Block any potential sensitive paths
Disallow: /saml/
Disallow: /static/admin/
Disallow: /api/
Disallow: /admin/
Disallow: /private/

# Crawl delay (optional - be respectful to server)
Crawl-delay: 1

# Sitemaps
Sitemap: {request.url_root.rstrip('/')}/sitemap.xml

# Language-specific sitemaps
Sitemap: {request.url_root.rstrip('/')}/sitemap_en.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_es.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_fr.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_de.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_pt.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_ru.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_ko.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_ja.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_zh_Hant.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_zh_Hans.xml
Sitemap: {request.url_root.rstrip('/')}/sitemap_ar.xml

# Google-specific directives
User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Googlebot-Mobile
Allow: /

# Bing-specific directives
User-agent: Bingbot
Allow: /

# Additional search engines
User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: YandexBot
Allow: /
"""
    response = make_response(robots_content)
    response.headers['Content-Type'] = 'text/plain'
    return response 
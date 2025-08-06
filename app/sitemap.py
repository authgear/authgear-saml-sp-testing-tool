from flask import Blueprint, make_response, request
from datetime import datetime
import xml.etree.ElementTree as ET

sitemap_bp = Blueprint('sitemap', __name__)

# Supported languages - should match app.py SUPPORTED_LANGUAGES
LANGUAGES = ['en', 'es', 'fr', 'de', 'pt', 'ru', 'ko', 'ja', 'zh_Hant', 'zh_Hans', 'ar']

# Language names for hreflang
LANGUAGE_NAMES = {
    'en': 'en',
    'es': 'es', 
    'fr': 'fr',
    'de': 'de',
    'pt': 'pt',
    'ru': 'ru',
    'ko': 'ko',
    'ja': 'ja',
    'zh_Hant': 'zh-Hant',
    'zh_Hans': 'zh-Hans',
    'ar': 'ar'
}

def indent(elem, level=0):
    """Add proper indentation to XML elements"""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def create_sitemap_index(base_url):
    """Create sitemap index with all language sitemaps"""
    root = ET.Element('sitemapindex')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    for lang in LANGUAGES:
        sitemap = ET.SubElement(root, 'sitemap')
        loc = ET.SubElement(sitemap, 'loc')
        loc.text = f"{base_url}/sitemap_{lang}.xml"
        lastmod = ET.SubElement(sitemap, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
    
    indent(root)
    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'

def create_language_sitemap(lang, base_url):
    """Create sitemap for a specific language"""
    root = ET.Element('urlset')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    root.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
    
    # Main page
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = f"{base_url}/{lang}/"
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'weekly'
    priority = ET.SubElement(url, 'priority')
    priority.text = '1.0'
    
    # Add hreflang alternatives
    for alt_lang in LANGUAGES:
        xhtml_link = ET.SubElement(url, 'xhtml:link')
        xhtml_link.set('rel', 'alternate')
        xhtml_link.set('hreflang', LANGUAGE_NAMES[alt_lang])
        xhtml_link.set('href', f"{base_url}/{alt_lang}/")
    
    # Attrs page
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = f"{base_url}/{lang}/attrs/"
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'monthly'
    priority = ET.SubElement(url, 'priority')
    priority.text = '0.8'
    
    # Add hreflang alternatives for attrs
    for alt_lang in LANGUAGES:
        xhtml_link = ET.SubElement(url, 'xhtml:link')
        xhtml_link.set('rel', 'alternate')
        xhtml_link.set('hreflang', LANGUAGE_NAMES[alt_lang])
        xhtml_link.set('href', f"{base_url}/{alt_lang}/attrs/")
    
    # Metadata page
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = f"{base_url}/{lang}/metadata/"
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'monthly'
    priority = ET.SubElement(url, 'priority')
    priority.text = '0.6'
    
    # Add hreflang alternatives for metadata
    for alt_lang in LANGUAGES:
        xhtml_link = ET.SubElement(url, 'xhtml:link')
        xhtml_link.set('rel', 'alternate')
        xhtml_link.set('hreflang', LANGUAGE_NAMES[alt_lang])
        xhtml_link.set('href', f"{base_url}/{alt_lang}/metadata/")
    
    indent(root)
    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'

@sitemap_bp.route('/sitemap.xml')
def sitemap_index():
    """Serve sitemap index"""
    base_url = request.url_root.rstrip('/')
    response = make_response(create_sitemap_index(base_url))
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response

@sitemap_bp.route('/sitemap_<lang>.xml')
def language_sitemap(lang):
    """Serve language-specific sitemap"""
    if lang not in LANGUAGES:
        return 'Language not found', 404
    
    base_url = request.url_root.rstrip('/')
    response = make_response(create_language_sitemap(lang, base_url))
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response

 
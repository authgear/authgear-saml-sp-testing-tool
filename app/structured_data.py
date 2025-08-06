import json
from flask import Blueprint, make_response, request

structured_data_bp = Blueprint('structured_data', __name__)

def get_web_site_structured_data():
    """Generate WebSite structured data"""
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "SAML Testing Tool",
        "alternateName": ["SAML SP Testing Tool", "samlsp.com"],
        "url": request.url_root.rstrip('/'),
        "description": "Test SAML authentication flows with Authgear or any other Identity Provider. Configure and validate SAML SSO integration.",
        "inLanguage": ["en", "es", "fr", "pt", "ru", "ko", "ja", "zh-Hant", "zh-Hans"],
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": request.url_root.rstrip('/') + "/en/?search={search_term_string}"
            },
            "query-input": "required name=search_term_string"
        }
    }

def get_web_application_structured_data():
    """Generate WebApplication structured data"""
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "SAML Testing Tool",
        "description": "A comprehensive SAML testing tool that acts as a Service Provider (SP) for testing SAML authentication flows with various Identity Providers including Authgear, Auth0, Okta, and Entra ID.",
        "url": request.url_root.rstrip('/'),
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Web Browser",
        "browserRequirements": "Requires JavaScript. Requires HTML5.",
        "featureList": [
            "SAML 2.0 authentication flow testing",
            "User attributes and claims viewing",
            "Various SAML bindings configuration",
            "Different NameID formats testing",
            "SAML response validation",
            "Metadata upload and parsing",
            "Multi-language support"
        ],
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        },
        "author": {
            "@type": "Organization",
            "name": "Authgear",
            "url": "https://www.authgear.com"
        },
        "creator": {
            "@type": "Organization",
            "name": "Authgear",
            "url": "https://www.authgear.com"
        }
    }

def get_organization_structured_data():
    """Generate Organization structured data for Authgear"""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Authgear",
        "url": "https://www.authgear.com",
        "logo": request.url_root.rstrip('/') + "/static/authgear-logo.svg",
        "description": "Authgear provides seamless, secure, and scalable identity management solutions.",
        "sameAs": [
            "https://github.com/authgear",
            "https://www.linkedin.com/company/authgear"
        ]
    }

def get_breadcrumb_structured_data(current_path, current_lang):
    """Generate BreadcrumbList structured data"""
    base_url = request.url_root.rstrip('/')
    
    breadcrumbs = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": f"{base_url}/{current_lang}/"
        }
    ]
    
    if "attrs" in current_path:
        breadcrumbs.append({
            "@type": "ListItem",
            "position": 2,
            "name": "User Attributes",
            "item": f"{base_url}/{current_lang}/attrs/"
        })
    elif "metadata" in current_path:
        breadcrumbs.append({
            "@type": "ListItem",
            "position": 2,
            "name": "SAML Metadata",
            "item": f"{base_url}/{current_lang}/metadata/"
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumbs
    }

@structured_data_bp.route('/structured-data.json')
def structured_data_json():
    """Serve all structured data as JSON"""
    data = {
        "webSite": get_web_site_structured_data(),
        "webApplication": get_web_application_structured_data(),
        "organization": get_organization_structured_data()
    }
    
    response = make_response(json.dumps(data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    return response 
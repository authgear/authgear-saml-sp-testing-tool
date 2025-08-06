import os
from datetime import timedelta
from .login_form import LoginForm

from flask import (
    Flask,
    request,
    Request,
    render_template,
    redirect,
    session,
    make_response,
)

from flask_babel import Babel, gettext as _
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.errors import OneLogin_Saml2_Error
from .config import USE_HTTPS, GTM_ID
from .sitemap import sitemap_bp
from .robots_enhanced import robots_bp
from .structured_data import structured_data_bp


# Supported languages
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'pt', 'ru', 'ko', 'ja', 'zh_Hant', 'zh_Hans', 'ar']

# RTL languages
RTL_LANGUAGES = ['ar']


app = Flask(__name__)
app.config["SECRET_KEY"] = "authgeardemosamlsp"
app.config["SESSION_COOKIE_NAME"] = "authgeardemosamlspsession"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
app.config["SAML_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "saml"
)

def get_locale():
    # Try to get locale from URL path first
    path_parts = request.path.strip('/').split('/')
    if path_parts and path_parts[0] in SUPPORTED_LANGUAGES:
        return path_parts[0]
    # Try to get locale from session
    if 'lang' in session:
        return session['lang']
    # Try to get locale from request args (for backward compatibility)
    if request.args.get('lang'):
        return request.args.get('lang')
    # Try to get locale from Accept-Language header
    return request.accept_languages.best_match(['en'])


def validate_language(lang):
    """Validate if the given language is supported"""
    return lang in SUPPORTED_LANGUAGES


# Babel configuration
babel = Babel(app, locale_selector=get_locale)

# Register blueprints
app.register_blueprint(sitemap_bp)
app.register_blueprint(robots_bp)
app.register_blueprint(structured_data_bp)


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.context_processor
def inject_gtm_id():
    """Inject GTM_ID into all templates"""
    return dict(gtm_id=GTM_ID)


@app.context_processor
def inject_gettext():
    """Inject gettext function into all templates"""
    return dict(_=_)

@app.context_processor
def inject_current_language():
    """Inject current language from URL path into all templates"""
    # Get language from URL path
    path_parts = request.path.strip('/').split('/')
    current_lang = 'en'  # default
    if path_parts and path_parts[0] in SUPPORTED_LANGUAGES:
        current_lang = path_parts[0]
    
    # Check if current language is RTL
    is_rtl = current_lang in RTL_LANGUAGES
    
    return dict(current_language=current_lang, is_rtl=is_rtl)


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://plausible.io https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://plausible.io;"
    
    # Add cache headers
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
    elif request.path.endswith('.xml'):
        response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
    else:
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
    
    return response


@app.route('/language/<lang>')
def set_language(lang):
    """Set the language for the session and redirect to language-specific URL"""
    session['lang'] = lang
    # Get the current path without language prefix
    current_path = request.referrer or '/'
    if current_path.startswith(request.host_url):
        current_path = current_path[len(request.host_url):]
    
    # Remove any existing language prefix
    path_parts = current_path.strip('/').split('/')
    if path_parts and path_parts[0] in SUPPORTED_LANGUAGES:
        path_parts = path_parts[1:]
    
    # Build new path with language prefix
    new_path = f'/{lang}/'
    if path_parts:
        new_path += '/'.join(path_parts)
    
    return redirect(new_path)


def init_saml_auth(req, request: Request, login_form: LoginForm):
    auth = OneLogin_Saml2_Auth(
        req,
        old_settings={
            **login_form.to_saml_settings(request),
            "strict": True,
            "debug": True,
        },
    )
    return auth


def prepare_flask_request(request: Request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    return {
        "https": "on" if USE_HTTPS else "off",
        "http_host": request.host,
        "script_name": request.path,
        "get_data": request.args.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        "post_data": request.form.copy(),
    }


@app.route("/health")
def health():
    """Health check endpoint for monitoring and liveness probes"""
    return "OK", 200


@app.route("/")
def root_redirect():
    """Redirect root to default language (English)"""
    return redirect("/en/")

@app.route("/<lang>/", methods=["GET", "POST"])
def index(lang):
    # Validate language
    if not validate_language(lang):
        return redirect("/en/")
    
    # Handle language selection from query parameter (for backward compatibility)
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    
    req = prepare_flask_request(request)
    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False
    # Create a form with stored values
    login_form = LoginForm.parse(request, session.get(LoginForm.session_key(), dict()))
    auth = None
    init_error = None
    try:
        auth = init_saml_auth(req, request, login_form)
    except OneLogin_Saml2_Error as e:
        # If the stored values are invalid, init will fail.
        # Ignore the error at the moment.
        pass

    if "sso2" in request.args:
        login_form = LoginForm.parse(request, request.form)
        session[LoginForm.session_key()] = login_form.to_dict()
        try:
            auth = init_saml_auth(req, request, login_form)
        except OneLogin_Saml2_Error as e:
            return render_template("invalid.html", init_error=init_error)

        return_to = "%sattrs/" % request.host_url

        return redirect(
            auth.login(
                return_to,
                force_authn=login_form.force_authn,
                is_passive=login_form.is_passive,
                name_id_value_req=login_form.maybe_subject_nameid(),
            ),
        )
    elif "slo" in request.args:
        # Check if IdP supports Single Logout (Logout URL is provided)
        if not login_form.idp_slo_url:
            # IdP doesn't support Single Logout, just clear authentication session data
            # Preserve form data
            form_data = session.get(LoginForm.session_key(), {})
            session.clear()
            session[LoginForm.session_key()] = form_data
            return redirect(request.url + "?logout_success=1")
        
        name_id = session_index = nameid_format = name_id_nq = name_id_spnq = None
        if "samlNameId" in session:
            name_id = session["samlNameId"]
        if "samlSessionIndex" in session:
            session_index = session["samlSessionIndex"]
        if "samlNameIdFormat" in session:
            nameid_format = session["samlNameIdFormat"]
        if "samlNameIdNameQualifier" in session:
            name_id_nq = session["samlNameIdNameQualifier"]
        if "samlNameIdSPNameQualifier" in session:
            name_id_spnq = session["samlNameIdSPNameQualifier"]
        
        if auth is None:
            # Auth object is not available, just clear authentication session data
            # Preserve form data
            form_data = session.get(LoginForm.session_key(), {})
            session.clear()
            session[LoginForm.session_key()] = form_data
            return redirect(request.url)
        
        try:
            return redirect(
                auth.logout(
                    name_id=name_id,
                    session_index=session_index,
                    nq=name_id_nq,
                    name_id_format=nameid_format,
                    spnq=name_id_spnq,
                )
            )
        except OneLogin_Saml2_Error as e:
            # Handle logout errors gracefully
            errors.append(f"Logout failed: {str(e)}")
            # Clear authentication session data but preserve form data
            form_data = session.get(LoginForm.session_key(), {})
            session.clear()
            session[LoginForm.session_key()] = form_data
            return redirect(request.url)
    elif "acs" in request.args:
        request_id = None
        if "AuthNRequestID" in session:
            request_id = session["AuthNRequestID"]
        if auth is None:
            return "Failed to initialize. Session is missing."
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            if "AuthNRequestID" in session:
                del session["AuthNRequestID"]
            session["samlUserdata"] = auth.get_attributes()
            session["samlNameId"] = auth.get_nameid()
            session["samlNameIdFormat"] = auth.get_nameid_format()
            session["samlNameIdNameQualifier"] = auth.get_nameid_nq()
            session["samlNameIdSPNameQualifier"] = auth.get_nameid_spnq()
            session["samlSessionIndex"] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if "RelayState" in request.form and self_url != request.form["RelayState"]:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the request.form['RelayState'] is a trusted URL.
                if request.form["RelayState"]:
                    return redirect(auth.redirect_to(request.form["RelayState"]))
                else:
                    return redirect(f"/{lang}/attrs/")
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()
    elif "sls" in request.args:
        request_id = None
        if "LogoutRequestID" in session:
            request_id = session["LogoutRequestID"]

        def delete_session():
            # Safely delete session keys that might not exist
            session_keys = [
                "samlUserdata",
                "samlNameId", 
                "samlNameIdFormat",
                "samlNameIdNameQualifier",
                "samlNameIdSPNameQualifier",
                "samlSessionIndex"
            ]
            for key in session_keys:
                session.pop(key, None)

        url = auth.process_slo(request_id=request_id, delete_session_cb=delete_session)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the url is a trusted URL.
                return redirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    if "samlUserdata" in session:
        paint_logout = True
        if len(session["samlUserdata"]) > 0:
            attributes = session["samlUserdata"].items()

    # Check for logout success parameter
    if request.args.get('logout_success'):
        success_slo = True
    
    login_form = login_form.update_from_query(request)

    return render_template(
        "index.html",
        request=request,
        errors=errors,
        error_reason=error_reason,
        not_auth_warn=not_auth_warn,
        success_slo=success_slo,
        attributes=attributes,
        paint_logout=paint_logout,
        login_form=login_form,
    )


@app.route("/<lang>/attrs/")
def attrs(lang):
    # Validate language
    if not validate_language(lang):
        return redirect("/en/attrs/")
    
    paint_logout = False
    attributes = False
    nameid = None
    nameid_format = None

    if "samlUserdata" in session:
        paint_logout = True

        if len(session["samlUserdata"]) > 0:
            attributes = session["samlUserdata"].items()
            nameid = session["samlNameId"]
            nameid_format = session["samlNameIdFormat"]

    return render_template(
        "attrs.html",
        paint_logout=paint_logout,
        attributes=attributes,
        nameid=nameid,
        nameid_format=nameid_format,
    )


@app.route("/<lang>/metadata/")
def metadata(lang):
    # Validate language
    if not validate_language(lang):
        return redirect("/en/metadata/")
    
    req = prepare_flask_request(request)
    login_form = LoginForm.parse(request, session.get(LoginForm.session_key(), dict()))
    auth = init_saml_auth(req, request, login_form)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
    else:
        resp = make_response(", ".join(errors), 500)
    return resp

# Backward compatibility routes
@app.route("/attrs/")
def attrs_legacy():
    """Legacy route - redirect to English version"""
    return redirect("/en/attrs/")

@app.route("/metadata/")
def metadata_legacy():
    """Legacy route - redirect to English version"""
    return redirect("/en/metadata/")

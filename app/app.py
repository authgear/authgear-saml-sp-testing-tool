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


app = Flask(__name__)
app.config["SECRET_KEY"] = "authgeardemosamlsp"
app.config["SESSION_COOKIE_NAME"] = "authgeardemosamlspsession"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
app.config["SAML_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "saml"
)

def get_locale():
    # Try to get locale from session
    if 'lang' in session:
        return session['lang']
    # Try to get locale from request args
    if request.args.get('lang'):
        return request.args.get('lang')
    # Try to get locale from Accept-Language header
    return request.accept_languages.best_match(['en'])


# Babel configuration
babel = Babel(app, locale_selector=get_locale)


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


@app.route('/language/<lang>')
def set_language(lang):
    """Set the language for the session"""
    session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


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


@app.route("/", methods=["GET", "POST"])
def index():
    # Handle language selection from query parameter
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
                    return redirect("./attrs/")
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


@app.route("/attrs/")
def attrs():
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


@app.route("/metadata/")
def metadata():
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

from typing import NamedTuple, Self
from flask import Request
from urllib import parse


class LoginForm(NamedTuple):
    is_passive: bool
    force_authn: bool
    nameid_format: str
    sp_audience: str
    acs_binding: str
    idp_issuer: str
    idp_sso_url: str
    idp_sso_binding: str
    idp_cert: str

    @classmethod
    def session_key(cls) -> str:
        return "login_form_values"

    @classmethod
    def nameid_format_options(cls) -> list[str]:
        return [
            "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
            "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        ]

    @classmethod
    def acs_binding_options(cls) -> list[str]:
        return [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        ]

    @classmethod
    def idp_sso_binding_options(cls) -> list[str]:
        return [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        ]

    @classmethod
    def sp_recipient(cls, request: Request) -> str:
        parsed_uri = parse.urlparse(request.url)
        return "{uri.scheme}://{uri.netloc}/?acs".format(uri=parsed_uri)

    @classmethod
    def sp_destination(cls, request: Request) -> str:
        parsed_uri = parse.urlparse(request.url)
        return "{uri.scheme}://{uri.netloc}/?acs".format(uri=parsed_uri)

    @classmethod
    def default_sp_audience(cls, request: Request) -> str:
        parsed_uri = parse.urlparse(request.url)
        return "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)

    @classmethod
    def parse(cls, request: Request, form_data: dict) -> Self:
        is_passive = str(form_data.get("is_passive", "false")).lower() == "true"
        force_authn = str(form_data.get("force_authn", "false")).lower() == "true"

        nameid_format = form_data.get(
            "nameid_format", "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
        )
        sp_audience = form_data.get("sp_audience", "") or cls.default_sp_audience(
            request
        )
        acs_binding = form_data.get(
            "acs_binding", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        )
        idp_issuer = form_data.get("idp_issuer", "")
        idp_sso_url = form_data.get("idp_sso_url", "")
        idp_sso_binding = form_data.get(
            "idp_sso_binding", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        )
        idp_cert = form_data.get("idp_cert", "")

        return LoginForm(
            is_passive=is_passive,
            force_authn=force_authn,
            nameid_format=nameid_format,
            sp_audience=sp_audience,
            acs_binding=acs_binding,
            idp_issuer=idp_issuer,
            idp_sso_url=idp_sso_url,
            idp_sso_binding=idp_sso_binding,
            idp_cert=idp_cert,
        )

    def to_dict(self) -> dict:
        return self._asdict()

    def to_saml_settings(self) -> dict:
        print("self.idp_sso_url", self.idp_sso_url)
        return {
            "sp": {
                "entityId": self.sp_audience,
                "assertionConsumerService": {
                    "url": "http://localhost:5001/?acs",
                    "binding": self.acs_binding,
                },
                "singleLogoutService": {
                    "url": "http://localhost:5001/?sls",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "NameIDFormat": self.nameid_format,
                "x509cert": "",
                "privateKey": "",
            },
            "idp": {
                "entityId": self.idp_issuer,
                "singleSignOnService": {
                    "url": self.idp_sso_url,
                    "binding": self.idp_sso_binding,
                },
                "x509cert": self.idp_cert,
            },
        }

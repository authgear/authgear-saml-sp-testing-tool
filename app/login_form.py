import os
from typing import Self
from dataclasses import dataclass, replace, asdict
from flask import Request
from urllib import parse
from enum import StrEnum
from .config import USE_HTTPS


class NameID(StrEnum):
    unspecified = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
    emailAddress = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"


class Binding(StrEnum):
    HTTPPost = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    HTTPRedirect = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"


def get_scheme() -> str:
    if USE_HTTPS:
        return "https"
    return "http"


@dataclass
class LoginForm:
    is_passive: bool
    force_authn: bool
    nameid_format: NameID
    sp_audience: str
    acs_binding: Binding
    idp_issuer: str
    idp_sso_url: str
    idp_sso_binding: Binding
    idp_cert: str
    idp_slo_url: str
    subject_nameid: str

    @classmethod
    def session_key(cls) -> str:
        return "login_form_values"

    @classmethod
    def nameid_format_options(cls) -> list[NameID]:
        return [
            NameID.unspecified,
            NameID.emailAddress,
        ]

    @classmethod
    def acs_binding_options(cls) -> list[Binding]:
        return [
            Binding.HTTPPost,
        ]

    @classmethod
    def idp_sso_binding_options(cls) -> list[Binding]:
        return [
            Binding.HTTPRedirect,
        ]

    @classmethod
    def acs_url(cls, request: Request) -> str:
        parsed_uri = parse.urlparse(request.url)
        return "{scheme}://{uri.netloc}/?acs".format(
            scheme=get_scheme(), uri=parsed_uri
        )

    @classmethod
    def sp_recipient(cls, request: Request) -> str:
        return cls.acs_url(request)

    @classmethod
    def sp_destination(cls, request: Request) -> str:
        return cls.acs_url(request)

    @classmethod
    def default_sp_audience(cls, request: Request) -> str:
        parsed_uri = parse.urlparse(request.url)
        return "{scheme}://{uri.netloc}".format(scheme=get_scheme(), uri=parsed_uri)

    @classmethod
    def default_acs_binding(cls) -> Binding:
        return Binding.HTTPPost

    @classmethod
    def default_sso_binding(cls) -> Binding:
        return Binding.HTTPRedirect

    @classmethod
    def default_nameid_format(cls) -> NameID:
        return NameID.unspecified

    @classmethod
    def parse(cls, request: Request, form_data: dict) -> Self:
        is_passive = _parse_strbool_from_dict(form_data, "is_passive")
        force_authn = _parse_strbool_from_dict(form_data, "force_authn")

        nameid_format = form_data.get("nameid_format", cls.default_nameid_format())
        sp_audience = form_data.get("sp_audience", "") or cls.default_sp_audience(
            request
        )
        acs_binding = form_data.get("acs_binding", cls.default_acs_binding())
        idp_issuer = form_data.get("idp_issuer", "")
        idp_sso_url = form_data.get("idp_sso_url", "")
        idp_sso_binding = form_data.get("idp_sso_binding", cls.default_sso_binding())
        idp_cert = form_data.get("idp_cert", "")
        idp_slo_url = form_data.get("idp_slo_url", "")
        subject_nameid = form_data.get("subject_nameid", "")

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
            idp_slo_url=idp_slo_url,
            subject_nameid=subject_nameid,
        )

    def update_from_query(self, request: Request) -> Self:
        result = replace(self)
        if request.args.get("is_passive"):
            result.is_passive = _parse_strbool_from_dict(request.args, "is_passive")
        if request.args.get("force_authn"):
            result.force_authn = _parse_strbool_from_dict(request.args, "force_authn")
        if request.args.get("nameid_format"):
            result.nameid_format = request.args.get(
                "nameid_format", self.default_nameid_format()
            )
        if request.args.get("sp_audience"):
            result.sp_audience = request.args.get(
                "sp_audience", self.default_sp_audience(request)
            )
        if request.args.get("acs_binding"):
            result.acs_binding = request.args.get(
                "acs_binding", self.default_acs_binding()
            )
        if request.args.get("idp_issuer"):
            result.idp_issuer = request.args.get("idp_issuer", "")
        if request.args.get("idp_sso_url"):
            result.idp_sso_url = request.args.get("idp_sso_url", "")
        if request.args.get("idp_sso_binding"):
            result.idp_sso_binding = request.args.get(
                "idp_sso_binding", self.default_sso_binding()
            )
        if request.args.get("idp_cert"):
            result.idp_cert = request.args.get("idp_cert", "")
        if request.args.get("idp_slo_url"):
            result.idp_slo_url = request.args.get("idp_slo_url", "")
        if request.args.get("subject_nameid"):
            result.subject_nameid = request.args.get("subject_nameid", "")
        return result

    def to_dict(self) -> dict:
        return asdict(self)

    def to_saml_settings(self, request: Request) -> dict:
        settings = {
            "sp": {
                "entityId": self.sp_audience,
                "assertionConsumerService": {
                    "url": self.acs_url(request),
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
        if self.idp_slo_url:
            settings["idp"]["singleLogoutService"] = {
                "url": self.idp_slo_url,
                "responseUrl": self.idp_slo_url,
            }
        return settings

    def maybe_subject_nameid(self) -> str | None:
        if self.subject_nameid == "":
            return None
        return self.subject_nameid


def _parse_strbool_from_dict(d: dict, key: str) -> bool:
    return str(d.get(key, "false")).lower() == "true"

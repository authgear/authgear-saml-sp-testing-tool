# Authgear Demo SAML SP

A SAML Service Provider testing tool for configuring and testing SAML authentication flows with Authgear or any other Identity Provider.

## Quick Start

```sh
cd app
make setup
make start
```

Visit `http://localhost:5001` to access the tool.

**Requirements**: Python 3.11

## Usage

1. **Configure IdP Settings**: Enter your Identity Provider details (Entity ID, SSO URL, certificate)
2. **Set SP Configuration**: Configure Service Provider settings (audience, bindings, NameID format)
3. **Test Authentication**: Click "Login" to initiate SAML authentication flow
4. **View Results**: Check returned user attributes and authentication status

The tool supports various SAML bindings, NameID formats, and provides detailed error messages for troubleshooting.

## Deploy

```sh
make -C app push-image
make -C deploy deploy
```

## Dependencies

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [python3-saml](https://github.com/SAML-Toolkits/python3-saml) - SAML toolkit
- [python-xmlsec](https://github.com/xmlsec/python-xmlsec) - XML signature verification
- [lxml](https://lxml.de/) - XML processing

## License

This project is licensed under the MIT License.

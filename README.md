# Authgear Demo SAML SP

## Development

This project uses pipenv to manage packages.

https://github.com/pypa/pipenv

```sh
cd ./demo-flask
pipenv install
```

Start the server

```sh
# In ./demo-flask
make start
```

## Deploying to Pandawork

```sh
make -C demo-flask push-image
make -C deploy deploy
```

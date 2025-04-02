# Authgear Demo SAML SP

Assume you have python3 installed globally on your machine, or
you are a user of https://github.com/nix-community/nix-direnv

## Development

```sh
make -C demo-flask setup
make -C demo-flask start
```

## Deploying to Pandawork

```sh
make -C demo-flask push-image
make -C deploy deploy
```

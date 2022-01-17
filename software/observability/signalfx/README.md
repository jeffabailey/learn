# Learn Signal FX

This repository is a companion to [this blog post](https://jeffbailey.us/blog/2020/05/24/learn-signalfx/). If you follow along there you should be able to make use of it.

Enable SignalFx monitoring for a Postgresql database.

- Find your SignalFx API key and Realm by going to [your profile](https://app.us1.signalfx.com/#/myprofile).

In my case the realm is us1.

## Set Up

You'll need to get your SignalFx token.

![SignalFx Tokens](https://jeffbailey.us/wp-content/uploads/2020/05/image-5.png)

Copy the token to a file with this command.

```bash
printf <YourToken> > config/signalfx-access-token.txt
```

## Build the container

```bash
docker build --rm --name learn-signalfx --build-arg signalfx_access_token=$(cat config/signalfx-access-token.txt) --build-arg signalfx_realm=<YourRealm> .
```

## Run the container

```bash
docker run --rm -t learn-signalfx -it learn-signalfx /bin/bash
```

## Attach to a running container

```bash
docker exec -it learn-signalfx /bin/bash
```

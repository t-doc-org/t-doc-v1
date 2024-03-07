# Création d'une image:
# $ docker build -t t-doc .
#
# Démarrage d'un conteneur:
# $ docker run --it --mount type=bind,source=${REPO},target=/repo,readonly \
#       --publish 8000:8000 t-doc

# Alpine Linux a une version récente de texlive, mais le binaire tex4ht manque.
# De plus, dans la version 3.19, luatex est compilé pour la mauvaise version de
# zlib <https://gitlab.alpinelinux.org/alpine/aports/-/issues/15742>.
#FROM alpine:3.18
#RUN apk add --no-cache python3 py3-django texlive-full

# Ubuntu a une version plus ancienne de texlive, avec laquelle la conversion en
# HTML ne fonctionne pas.
#FROM ubuntu:latest
#ARG DEBIAN_FRONTEND=noninteractive
#RUN apt-get update \
#    && apt-get install -y python3 python3-django texlive-full \
#    && rm -rf /var/lib/apt/lists/*

# L'image texlive/texlive a une version récente de texlive.
FROM texlive/texlive:latest
WORKDIR /
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y python3 python3-django \
    && rm -rf /var/lib/apt/lists/*

# Préparation du mountpoint pour les fichiers externes.
RUN mkdir /repo
VOLUME /repo

# Préparation du cache.
RUN mkdir /var/cache/t-doc

# Définition du port du serveur web.
EXPOSE 8000

# Démarrage de l'application.
CMD ["python3", "/repo/server/manage.py", "runserver", "0.0.0.0:8000"]

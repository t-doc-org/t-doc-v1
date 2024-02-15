FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    git-all \
    texlive-full \
    python3-django

EXPOSE 8000

# Start the app
#CMD ["python", "manage.py", "runserver, "0.0.0.0:8000]

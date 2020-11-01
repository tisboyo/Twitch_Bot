FROM python:3.8

# Any environment variables that are stored in
# the .env file must be loaded in docker-compose.yml
# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1 \
    PYTHONUNBUFFERED=1


# Create the working directory
WORKDIR /workspace/web

# Install files
COPY ./ /workspace/web

# Install needed libraries
RUN apt-get update && apt-get install -y \
    git


# Setup pipenv
RUN pip install --upgrade pip pipenv
RUN pipenv install --system --deploy

# Expose port for debugging
#EXPOSE 5678:5678

CMD ["python", "main.py"]

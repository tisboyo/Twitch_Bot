FROM python:3.8

# Any environment variables that are stored in
# the .env file must be loaded in docker-compose.yml
# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1 \
    PYTHONUNBUFFERED=1 \
    PIPENV_PIPFILE=/workspace/web/Pipfile

#Copy the dependencies first so they are built as their own layer
COPY ./requirements.txt /workspace/web/

# Install python dependencies
RUN pip install --upgrade -r /workspace/web/requirements.txt

# Install needed libraries
RUN apt-get update && apt-get install -y \
    git

# Create the working directory
WORKDIR /workspace/web

# Install files
COPY ./ /workspace/web

# Expose port for debugging
#EXPOSE 5678:5678

CMD ["python", "main.py"]

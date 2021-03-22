FROM python:3.8

# Any environment variables that are stored in
# the .env file must be loaded in docker-compose.yml
# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1 \
    PYTHONUNBUFFERED=1 \
    PIPENV_PIPFILE=/workspace/bot/Pipfile

#Copy the dependencies first so they are built as their own layer
COPY ./requirements.txt /workspace/bot/

# Install python dependencies
RUN pip install --upgrade -r /workspace/bot/requirements.txt

# Install needed libraries
RUN apt-get update && apt-get install -y \
    git


# Create the working directory
WORKDIR /workspace/bot/

EXPOSE 13337

#Copy the bot to a working directory
COPY ./ /workspace/bot/


# Expose port for debugging
#EXPOSE 5678:5678

CMD ./wait_for_it.sh mysql:3306 --timeout=60 --strict -- ./wait_for_it.sh api.twitch.tv:443 --timeout=60 --strict -- ./wait_for_it.sh tmi.twitch.tv:443 --timeout=60 --strict -- start.sh

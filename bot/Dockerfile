FROM python:3.9@sha256:5caa9a0f034e56693e096ac4562097d9167a2509d22fb970cb4a2b5465a48d95

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

# Any environment variables that are stored in
# the .env file must be loaded in docker-compose.yml
# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=$PIP_INDEX_URL\
    PIP_TRUSTED_HOST=$PIP_TRUSTED_HOST

#Create non-root user
RUN useradd --uid 1000 -U -m twitch_bot
USER twitch_bot
ENV PATH="/home/twitch_bot/.local/bin:${PATH}"

#Copy the dependencies first so they are built as their own layer
COPY --chown=twitch_bot:twitch_bot ./requirements.txt /workspace/bot/

# Install python dependencies
RUN pip install --upgrade -r /workspace/bot/requirements.txt

# Install needed libraries
# RUN apt-get update && apt-get install -y \
#     git


# Create the working directory
WORKDIR /workspace/bot/

EXPOSE 13337

#Copy the bot to a working directory
COPY --chown=twitch_bot:twitch_bot ./ /workspace/bot/


# Expose port for debugging
#EXPOSE 5678:5678

CMD ./wait_for_it.sh mysql:3306 --timeout=60 --strict -- ./wait_for_it.sh api.twitch.tv:443 --timeout=60 --strict -- ./wait_for_it.sh tmi.twitch.tv:443 --timeout=60 --strict -- ./start.sh

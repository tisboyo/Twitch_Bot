FROM python:3.9

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

# Any environment variables that are stored in
# the .env file must be loaded in docker-compose.yml
# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=$PIP_INDEX_URL\
    PIP_TRUSTED_HOST=$PIP_TRUSTED_HOST

#Copy the dependencies first so they are built as their own layer
COPY ./requirements.txt /workspace/mqtt_logger/

# Install python dependencies
RUN pip install --upgrade -r /workspace/mqtt_logger/requirements.txt

# Install needed libraries
# RUN apt-get update && apt-get install -y \
#     git


# Create the working directory
WORKDIR /workspace/mqtt_logger/

#Copy the bot to a working directory
COPY ./ /workspace/mqtt_logger/


# Expose port for debugging
#EXPOSE 5678:5678

CMD ./wait_for_it.sh mqtt:1883 --timeout=60 --strict -- python main.py

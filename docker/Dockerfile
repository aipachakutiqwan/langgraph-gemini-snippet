FROM europe-west3-docker.pkg.dev/prj-caip-prod-shared-14pl/docker-images/ai-python-3-12-slim:1.0.0

USER root
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev libssl-dev curl gnupg2
RUN apt-get install -y ldap-utils
RUN apt-get install -y stunnel4
RUN apt-get update

ARG USERNAME=python

USER ${USERNAME}
ARG WORKSPACE=/home/${USERNAME}/agent
WORKDIR ${WORKSPACE}

RUN mkdir -p /home/${USERNAME}/agent/logs
RUN touch /home/${USERNAME}/agent/logs/${PACKAGE_NAME}.log

COPY app_config /home/${USERNAME}/agent/app_config
COPY log_config /home/${USERNAME}/agent/log_config
COPY data /home/${USERNAME}/agent/data
COPY src /home/${USERNAME}/agent/src
COPY pyproject.toml /home/${USERNAME}/agent/

# WORKAROUND
USER root
RUN chmod 777 -R /home/${USERNAME}/agent/
USER ${USERNAME}

ENV PYTHONPATH "${PYTHONPATH}:/home/${USERNAME}/agent:/home/${USERNAME}/agent/src"
ENV PYTHONUNBUFFERED=0

CMD ["python", "-m", "src"]

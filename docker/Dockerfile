FROM europe-west3-docker.pkg.dev/prj-caip-prod-shared-14pl/docker-images/ai-python-3-12-slim:1.0.0

USER root
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev libssl-dev curl gnupg2
RUN apt-get install -y ldap-utils
RUN apt-get install -y stunnel4
RUN apt-get update

ARG USERNAME=python

ARG AI_ARCH_COMMONS_NAME=ai-arch-commons
ARG AI_ARCH_COMMONS_VERSION=0.4.0

ARG AI_IO_CONNECTORS_NAME=ai-io-connectors
ARG AI_IO_CONNECTORS_VERSION=0.5.0

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

RUN pip install keyrings.google-artifactregistry-auth
RUN pip install --extra-index-url https://europe-west3-python.pkg.dev/prj-caip-prod-shared-14pl/python-packages/simple/ ${AI_ARCH_COMMONS_NAME}==${AI_ARCH_COMMONS_VERSION}
RUN pip install --extra-index-url https://europe-west3-python.pkg.dev/prj-caip-prod-shared-14pl/python-packages/simple/ ${AI_IO_CONNECTORS_NAME}==${AI_IO_CONNECTORS_VERSION}
RUN pip install .


ENV PYTHONPATH "${PYTHONPATH}:/home/${USERNAME}/agent:/home/${USERNAME}/agent/src"
ENV PYTHONUNBUFFERED=0

CMD ["python", "-m", "src"]

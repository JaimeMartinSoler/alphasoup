FROM python:3.9

# paths local
ENV PATH_ROOT_LOCAL=.
ENV PATH_SRC_LOCAL=${PATH_ROOT_LOCAL}/src
ENV PATH_CONFIG_LOCAL=${PATH_ROOT_LOCAL}/config/config.yml
ENV PATH_TEMPLATES_LOCAL=${PATH_ROOT_LOCAL}/templates
# paths image
ENV PATH_ROOT=/alphasoup
ENV PATH_SRC=${PATH_ROOT}/src
ENV PATH_CONFIG=${PATH_ROOT}/config/config.yml
ENV PATH_TEMPLATES=${PATH_ROOT}/templates

# requirements
COPY ${PATH_ROOT_LOCAL}/requirements.txt ${PATH_ROOT}/requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install -r ${PATH_ROOT}/requirements.txt

# apt-get
RUN apt-get update
RUN apt-get install -y wkhtmltopdf && \
    apt-get install -y pdftk && \
    apt-get install -y ghostscript pdftk psutils

# src, config, templates
COPY ${PATH_SRC_LOCAL} ${PATH_SRC}
COPY ${PATH_CONFIG_LOCAL} ${PATH_CONFIG}
COPY ${PATH_TEMPLATES_LOCAL} ${PATH_TEMPLATES}

WORKDIR ${PATH_SRC}

# sudo docker image build -t alphasoup .
# docker container run -it --name alphasoup_000 alphasoup bash
# docker container run -it --name alphasoup_000 -v $(pwd)/config:/alphasoup/config -v $(pwd)/templates:/alphasoup/templates -v $(pwd)/output:/alphasoup/output alphasoup bash
# docker container run -it --name alphasoup_000 -v $(pwd)/config:/alphasoup/config -v $(pwd)/templates:/alphasoup/templates -v $(pwd)/output:/alphasoup/output alphasoup python3 -m main
# docker container rm alphasoup_000

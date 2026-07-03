FROM odoo:18

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nano \
        vim \
    && rm -rf /var/lib/apt/lists/*

COPY odoo.conf /etc/odoo/odoo.conf

USER odoo

CMD ["odoo"]

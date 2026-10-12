FROM certbot/certbot:v3.2.0

USER root

RUN apk add --no-cache docker-cli

COPY reload-nginx-hook.sh /usr/local/bin/reload-nginx-hook.sh
COPY renew-entrypoint.sh /usr/local/bin/renew-entrypoint.sh
RUN chmod +x /usr/local/bin/reload-nginx-hook.sh /usr/local/bin/renew-entrypoint.sh

# Root is required for docker.sock access (nginx reload via deploy-hook).
ENTRYPOINT ["/usr/local/bin/renew-entrypoint.sh"]

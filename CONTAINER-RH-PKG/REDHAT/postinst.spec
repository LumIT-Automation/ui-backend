%post
#!/bin/bash

printf "\n* Container postinst...\n" | tee -a /dev/tty

printf "\n* Building podman image...\n" | tee -a /dev/tty
cd /usr/lib/ui-backend

# Build container image.
buildah bud -t ui-backend . | tee -a /dev/tty

printf "\n* The container will start in few seconds.\n\n"

function containerSetup()
{
    wallBanner="RPM automation-interface-ui-backend-container post-install configuration message:\n"
    cd /usr/lib/ui-backend

    # First container run: associate name, bind ports, bind fs volume, define init process, ...
    # backend folder will be bound to /var/lib/containers/storage/volumes/.
    podman run --name ui-backend -v ui-backend:/var/www/ui-backend/backend -dt localhost/ui-backend /sbin/init
    podman exec ui-backend chown www-data:www-data /var/www/ui-backend/backend # uid 33 on host (www-data on Debian).

    printf "$wallBanner Starting Container Service on HOST..." | wall -n
    systemctl daemon-reload

    systemctl start automation-interface-ui-backend-container # (upon installation, container is already run).
    systemctl enable automation-interface-ui-backend-container

    printf "$wallBanner Configuring container..." | wall -n
    # Setup a Django secret key: using host-bound folders.
    djangoSecretKey=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)
    sed -i "s|^SECRET_KEY =.*|SECRET_KEY = \"$djangoSecretKey\"|g" /var/lib/containers/storage/volumes/ui-backend/_data/settings.py

    # Setup the JWT token public key (taken from SSO): using host-bound folders.
    cp -f /var/lib/containers/storage/volumes/sso/_data/settings_jwt.py /var/lib/containers/storage/volumes/ui-backend/_data/settings_jwt.py
    sed -i -e ':a;N;$!ba;s|\s*"privateKey.*}|\n}|g' /var/lib/containers/storage/volumes/ui-backend/_data/settings_jwt.py

    # Activate MariaDB audit plugin if MariaDB is installed.
    podman exec ui-backend bash -c "if dpkg -l | grep -q mariadb-server; then \
            cp /usr/share/automation-interface-ui-backend/51-mariadb.cnf /etc/mysql/mariadb.conf.d; \
            chmod 644 /etc/mysql/mariadb.conf.d/51-mariadb.cnf; \
            systemctl restart mariadb; \
        fi"

    printf "$wallBanner Restarting container's services..." | wall -n
    podman exec ui-backend systemctl restart apache2

    diffOutput=$(podman exec ui-backend diff /var/www/ui-backend_default_settings.py /var/www/ui-backend/backend/settings.py | grep '^[<>].*' | grep -v SECRET | grep -v PASSWORD | grep -v VENV || true)
    if [ -n "$diffOutput" ]; then
        printf "$wallBanner Differences from package's stock config file and the installed one (please import NEW directives in your installed config file, if any):\n* $diffOutput" | wall -n
    fi

    # syslog-ng seems going into a catatonic state while updating a package: restarting the whole thing.
    if rpm -qa | grep -q automation-interface-log; then
        if systemctl list-unit-files | grep -q syslog-ng.service; then
            systemctl restart syslog-ng || true # on host.
            podman exec ui-backend systemctl restart syslog-ng # on this container.
        fi
    fi

    printf "$wallBanner Installation completed." | wall -n
}

systemctl start atd

{ declare -f; cat << EOM; } | at now
containerSetup
EOM

exit 0


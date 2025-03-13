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

    # Grab the host timezone.
    timeZone=$(timedatectl show| awk -F'=' '/Timezone/ {print $2}')

    # First container run: associate name, bind ports, bind fs volume, define init process, ...
    # backend folder will be bound to /var/lib/containers/storage/volumes/.
    podman run --name ui-backend -v ui-backend:/var/www/ui-backend/backend -v ui-backend-db:/var/lib/mysql -dt localhost/ui-backend /lib/systemd/systemd
    podman exec ui-backend chown www-data:www-data /var/www/ui-backend/backend # uid 33 on host (www-data on Debian).
    podman exec ui-backend chown -R mysql:mysql /var/lib/mysql

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

    printf "$wallBanner Set the timezone of the container to be the same as the host timezone..." | wall -n
    podman exec ui-backend bash -c "timedatectl set-timezone $timeZone"

printf "$wallBanner Internal database configuration...\n"
    if podman exec ui-backend mysql -e "exit"; then
        # User uib.
        # Upon podman image creation, a password is generated for the user uib.
        databaseUserPassword=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

        if [ "$(podman exec ui-backend mysql --vertical -e "SELECT User FROM mysql.user WHERE User = 'uib';" | tail -1 | awk '{print $2}')" == "" ]; then
            # User uib not present: create.
            echo "Creating uib user..."
            podman exec ui-backend mysql -e "CREATE USER 'uib'@'localhost' IDENTIFIED BY '$databaseUserPassword';"
            podman exec ui-backend mysql -e "GRANT USAGE ON *.* TO 'uib'@'localhost' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
            podman exec ui-backend mysql -e 'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER, CREATE TEMPORARY TABLES, CREATE VIEW, SHOW VIEW, EXECUTE ON `uib`.* TO `uib`@`localhost`;'
        else
            # Update user's password.
            echo "Updating uib user's password..."
            podman exec ui-backend mysql -e "SET PASSWORD FOR 'uib'@'localhost' = PASSWORD('$databaseUserPassword');"
        fi

        # Change database password into Django config file, too.
        echo "Configuring Django..."
        sed -i "s/^.*DATABASE_USER$/        'USER': 'uib', #DATABASE_USER/g" /var/lib/containers/storage/volumes/ui-backend/_data/settings.py
        sed -i "s/^.*DATABASE_PASSWORD$/        'PASSWORD': '$databaseUserPassword', #DATABASE_PASSWORD/g" /var/lib/containers/storage/volumes/ui-backend/_data/settings.py

        # Database uib.
        if [ "$(podman exec ui-backend mysql --vertical -e "SHOW DATABASES LIKE 'uib';" | tail -1 | awk -F': ' '{print $2}')" == "" ]; then
            # Database not present: create.
            echo "Creating database uib and restoring SQL dump..."
            pkgVer=`dpkg-query --show --showformat='${Version}' automation-interface-ui-backend-container`
            commit=$(podman exec ui-backend dpkg-query --show --showformat='${Description}' automation-interface-ui-backend | sed -r -e 's/.*commit: (.*)/\1/' -e 's/\)\.//')
            podman exec ui-backend mysql -e 'CREATE DATABASE `uib` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT ='"'"'pkgVersion='${pkgVer}' commit='${commit}"'"';'

            podman exec ui-backend mysql uib -e "source /var/www/ui-backend/ui_backend/sql/uib.schema.sql" # restore database schema.
            podman exec ui-backend mysql uib -e "source /var/www/ui-backend/ui_backend/sql/uib.data.sql" # restore database data.
        fi

        # Database uib.
        if [ "$(podman exec ui-backend mysql --vertical -e "SHOW DATABASES LIKE 'uib';" | tail -1 | awk -F': ' '{print $2}')" == "" ]; then
            # Database not present: create.
            echo "Creating database uib and restoring SQL dump..."
            podman exec ui-backend mysql -e 'CREATE DATABASE uib DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;' # create database.
            podman exec ui-backend mysql uib -e "source /var/www/ui-backend/ui_backend/sql/uib.schema.sql" # restore database schema.
            podman exec ui-backend mysql uib -e "source /var/www/ui-backend/ui_backend/sql/uib.data.sql" # restore database data.
        fi

        # Database update via diff.sql (migrations).
        echo "Applying migrations..."
        podman exec ui-backend bash /var/www/ui-backend/ui_backend/sql/migrate.sh
    else
        echo "Failed to access MariaDB RDBMS, auth_socket plugin must be enabled for the database root user. Quitting."
        exit 1
    fi

    printf "$wallBanner Restarting container's services..." | wall -n
    podman exec ui-backend systemctl restart apache2
    podman exec ui-backend systemctl restart mysql

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


%postun
#!/bin/bash

printf "\n* Container postrm...\n"

# $1 is the number of time that this package is present on the system. If this script is run from an upgrade and not
if [ "$1" -eq "0" ]; then
    if podman volume ls | awk '{print $2}' | grep ^ui-backend$; then
        printf "\n* Clean up ui-backend volume...\n"
        podman volume rm ui-backend
    fi
fi

exit 0

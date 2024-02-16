#!/bin/bash

set -e

function System()
{
    base=$FUNCNAME
    this=$1

    # Declare methods.
    for method in $(compgen -A function)
    do
        export ${method/#$base\_/$this\_}="${method} ${this}"
    done

    # Properties list.
    ACTION="$ACTION"
}

# ##################################################################################################################################################
# Public
# ##################################################################################################################################################

#
# Void System_run().
#
function System_run()
{
    if [ "$ACTION" == "deb" ]; then
        if System_checkEnvironment; then
            System_definitions
            System_cleanup

            System_systemFilesSetup
            System_debianFilesSetup

            System_codeCollect
            System_codeConfig
            System_codeFilesPermissions
            System_venv
            System_fixDebVersion

            System_debCreate
            System_cleanup

            echo "Created /tmp/$projectName.deb"
        else
            echo "A Debian Bullseye operating system is required for the deb-ification. Aborting."
            exit 1
        fi
    else
        exit 1
    fi
}

# ##################################################################################################################################################
# Private static
# ##################################################################################################################################################

function System_checkEnvironment()
{
    if [ -f /etc/os-release ]; then
        if ! grep -q 'Debian GNU/Linux 11 (bullseye)' /etc/os-release; then
            return 1
        fi
    else
        return 1
    fi

    return 0
}


function System_definitions()
{
    declare -g debPackageRelease
    declare -g currentGitCommit

    declare -g projectName
    declare -g workingFolder
    declare -g workingFolderPath

    if [ -f DEBIAN-PKG/deb.release ]; then
        # Get program version from the release file.
        debPackageRelease=$(echo $(cat DEBIAN-PKG/deb.release))
    else
        echo "Error: deb.release missing."
        echo "Usage: bash DEBIAN-PKG/make-release.sh --action deb"
        exit 1
    fi

    git config --global --add safe.directory $(cd .. && pwd)
    currentGitCommit=$(git log --pretty=oneline | head -1 | awk '{print $1}')

    projectName="automation-interface-ui-backend_${debPackageRelease}_amd64"
    workingFolder="/tmp"
    workingFolderPath="${workingFolder}/${projectName}"
}


function System_cleanup()
{
    if [ -n "$workingFolderPath" ]; then
        if [ -d "$workingFolderPath" ]; then
            rm -fR "$workingFolderPath"
        fi
    fi
}


function System_codeCollect()
{
    mkdir -p $workingFolderPath/var/www/ui-backend
    mkdir -p $workingFolderPath/var/lib/ui-backend-venv

    # Copy files.
    cp -R ../ui_backend $workingFolderPath/var/www/ui-backend
    cp -R ../backend $workingFolderPath/var/www/ui-backend
    cp ../license.txt $workingFolderPath/var/www/ui-backend

    # Remove __pycache__ folders and not-required ones.
    rm -fR $(find $workingFolderPath/var/www/ui-backend -name __pycache__)
}


function System_codeConfig()
{
    sed -i "s/^DEBUG =.*/DEBUG = False/g" $workingFolderPath/var/www/ui-backend/backend/settings.py
    sed -i "s/^DISABLE_AUTHENTICATION =.*/DISABLE_AUTHENTICATION = False/g" $workingFolderPath/var/www/ui-backend/backend/settings.py

    # The following settings are emptied here and filled-in by postinst/s (debconf).
    sed -i "s/^SECRET_KEY =.*/SECRET_KEY = \"1234567890\"/g" $workingFolderPath/var/www/ui-backend/backend/settings.py
    sed -i "s/^ALLOWED_HOSTS =.*/ALLOWED_HOSTS = ['*']/g" $workingFolderPath/var/www/ui-backend/backend/settings.py

    sed -i -e ':a;N;$!ba;s|"publicKey.*,|"publicKey": '\'\'\'\'\'\','|g' $workingFolderPath/var/www/ui-backend/backend/settings_jwt.py

    # Also, copy the settings.py file into another location in order to keep the default config saved.
    cp -f $workingFolderPath/var/www/ui-backend/backend/settings.py $workingFolderPath/var/www/ui-backend_default_settings.py
}


function System_codeFilesPermissions()
{
    # Forcing standard permissions (755 for folders, 644 for files, owned by www-data:www-data).
    chown -R www-data:www-data $workingFolderPath/var/www/ui-backend
    find $workingFolderPath/var/www/ui-backend -type d -exec chmod 750 {} \;
    find $workingFolderPath/var/www/ui-backend -type f -exec chmod 640 {} \;

    # Particular permissions.
    #resources=( "$projectName/var/www/ui-backend" )
    #for res in "${resources[@]}"; do
    #    find $res -type d -exec chmod 750 {} \;
    #    find $res -type f -exec chmod 640 {} \;
    #done
}


function System_venv()
{
    # Put all pip dependencies in a virtual env.
    # All dependencies will be then included in the .deb package; Apache virtual host is set up accordingly.
    cp ../backend/pip.requirements $workingFolderPath/var/lib/ui-backend-venv

    # Start virtual environment for the collection of the dependencies.
    cd $workingFolderPath
    python3 -m venv var/lib/ui-backend-venv
    source var/lib/ui-backend-venv/bin/activate

    # Install pip dependencies in the virtual environment.
    python -m pip install --upgrade pip
    python -m pip install -r var/lib/ui-backend-venv/pip.requirements
    python -m pip freeze > /tmp/pip.freeze.venv

    # Exit from the virtual env.
    deactivate
    cd -

    rm $workingFolderPath/var/lib/ui-backend-venv/pip.requirements

    # Removing cached information within the venv (--> cleanup the venv).
    rm -R $(find $workingFolderPath/var/lib/ui-backend-venv/ -name __pycache__)
    sed -i "s|$workingFolderPath||g" $(grep -iR $workingFolderPath $workingFolderPath/var/lib/ui-backend-venv/ | awk -F: '{print $1}')

    # Configure the app.
    # Add the PATH the bin folder of the python venv.
    # API_VENV='/var/lib/ui-backend-venv'
    # sed -i -r -e "s#VENV_BIN =.*#VENV_BIN = \"${API_VENV}/bin/\"#" $workingFolderPath/var/www/ui-backend/backend/settings.py
}


function System_fixDebVersion()
{
    debVer=`echo $debPackageRelease | awk -F'-' '{print $1'}`
    if [ -r ../backend/pip.lock ]; then
        SameVer="y"
        for pyPack in $(cat /tmp/pip.freeze.venv | awk -F'==' '{print $1}'); do
            # Get version from new freeze file.
            nVer=$(cat /tmp/pip.freeze.venv | grep -E "^$pyPack==" | awk -F'==' '{print $2}')
            # Get version from old freeze file.
            if grep -Eq "^$pyPack==" ../backend/pip.lock; then
                oVer=$(cat ../backend/pip.lock | grep -E "^$pyPack==" | awk -F'==' '{print $2}')
            else
                oVer='missing'
            fi

            if [ "$nVer" != "$oVer" ]; then
                SameVer="n"
                echo -e "Package \e[92m${pyPack}\e[0m have a different version than before: Old: $oVer, New: $nVer"
            fi
        done

        if [ "$SameVer" != "y" ]; then
            echo " - Overwriting pip.lock file..."
            cp /tmp/pip.freeze.venv ../backend/pip.lock
            echo "Some python package version is changed, please adjust debian version file."
        else
            echo "Versions of the python packages are not changed."
        fi
    else
        echo " - File pip.lock was not present."
        cp /tmp/pip.freeze.venv ../backend/pip.lock
    fi
}


function System_systemFilesSetup()
{
    # Create a new working folder.
    mkdir $workingFolderPath

    # Setting up system files.
    cp -R DEBIAN-PKG/etc $workingFolderPath
    cp -R DEBIAN-PKG/usr $workingFolderPath

    find $workingFolderPath -type d -exec chmod 0755 {} \;
    find $workingFolderPath -type f -exec chmod 0644 {} \;

    chmod +x $workingFolderPath/usr/bin/consul.sh
    chmod +x $workingFolderPath/usr/bin/consul-template
    chmod +x $workingFolderPath/usr/bin/consul-template.sh
	chmod +x $workingFolderPath/usr/bin/syslogng-target.sh
}


function System_debianFilesSetup()
{
    # Setting up all the files needed to build the package (DEBIAN folder).
    cp -R DEBIAN-PKG/DEBIAN $workingFolderPath

    sed -i "s/^Version:.*/Version:\ $debPackageRelease/g" $workingFolderPath/DEBIAN/control
    sed -i "s/GITCOMMIT/$currentGitCommit/g" $workingFolderPath/DEBIAN/control

    chmod +x $workingFolderPath/DEBIAN/postinst
}


function System_debCreate()
{
    cd $workingFolder
    dpkg-deb --build $projectName
}

# ##################################################################################################################################################
# Main
# ##################################################################################################################################################

ACTION=""

# Must be run as root.
ID=$(id -u)
if [ $ID -ne 0 ]; then
    echo "This script needs super cow powers."
    exit 1
fi

# Parse user input.
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --action)
            ACTION="$2"
            shift
            shift
            ;;

        *)
            shift
            ;;
    esac
done

if [ -z "$ACTION" ]; then
    echo "Missing parameters. Use --action deb."
else
    System "system"
    $system_run
fi

exit 0

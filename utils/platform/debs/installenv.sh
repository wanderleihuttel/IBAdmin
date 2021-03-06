#!/bin/sh

# Update OS
apt-get -y update
apt-get -y upgrade
# Install required packages
apt-get -y install postgresql python-pip python-virtualenv python-setuptools python-psycopg2 python-crypto bacula-enterprise-postgresql mtx mt-st sudo apache2 libapache2-mod-wsgi lsscsi
# prepare empty bacula database
systemctl stop bacula-dir
systemctl stop bacula-sd
systemctl stop bacula-fd
systemctl stop ibadstatd
systemctl stop apache2
systemctl restart postgresql
su - postgres -c "dropdb bacula"
su - postgres -c "dropuser bacula"
sed -i 's/XXX_REPLACE_WITH_DBUSER_XXX/bacula/' /opt/bacula/scripts/grant_postgresql_privileges
su - postgres -c "/opt/bacula/scripts/create_postgresql_database"
su - postgres -c "/opt/bacula/scripts/make_postgresql_tables"
su - postgres -c "/opt/bacula/scripts/grant_postgresql_privileges"
PWGEN=`ip addr | md5sum | awk '{print $1}'`
sed -i "s/'PASSWORD': 'bacula123',/'PASSWORD': '$PWGEN',/" /opt/ibadmin/ibadmin/settings.py
su - postgres -c "psql -c \"alter user bacula with password '$PWGEN';\" bacula"
# create virtualenv for ibadmin application
virtualenv --system-site-packages /opt/ibadengine
# enable it in current shell
. /opt/ibadengine/bin/activate
# install required python packages
pip install --upgrade django==1.10
pip install --upgrade python-dateutil
pip install --upgrade pytz
/opt/ibadmin/manage.py migrate
# initialize required system configuration and scripts
cp /opt/ibadmin/utils/ibadmin.conf /etc/apache2/conf-enabled/
cp /opt/ibadmin/utils/SYS-Admin.sh /opt/ibadmin/utils/delete_catalog_backup_ibadmin /opt/ibadmin/utils/make_catalog_backup_ibadmin.pl /opt/bacula/scripts
# ibadmin require a dedicated bacula directories
mkdir -p /opt/bacula/bsr/
chown bacula:bacula /opt/bacula/bsr/
mkdir -p /opt/bacula/working/bkp
chown bacula:bacula /opt/bacula/working/bkp
# and apache user needs to run bconsole and have access to the system logs and services
usermod -G bacula,systemd-journal www-data
cp /opt/ibadmin/utils/platform/debs/ibadmin_sudoers /etc/sudoers.d/
systemctl restart apache2
# permissions to manage configs
chown bacula:bacula /opt/bacula/etc/bacula-dir.conf /opt/bacula/etc/bacula-fd.conf /opt/bacula/etc/bacula-sd.conf /opt/bacula/etc/bconsole.conf
chmod 660 /opt/bacula/etc/bacula-dir.conf /opt/bacula/etc/bacula-fd.conf /opt/bacula/etc/bacula-sd.conf /opt/bacula/etc/bconsole.conf
# install ibadstatd service
cp /opt/ibadmin/utils/ibadstatd.service /lib/systemd/system/
systemctl enable ibadstatd

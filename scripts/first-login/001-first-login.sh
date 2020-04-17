#!/bin/bash


# This script will be installed in /var/opt/meilisearch/scripts/first-login
# and will be run automatically when user logs via ssh

GREEN="\033[32;5;11m"
BLUE="\033[34;5;11m"
YELLOW="\033[33;5;11m"
RED="\033[31;5;11m"
BOLD="\033[1m"
RESET="\033[0m"

echo "\n\nThank you for using$BLUE MeiliSearch.$RESET\n\n"
echo "This is the first login here, and we need to set some basic configuration first.\n"
echo "If you don't mind...\n"



# ask_master_key_setup

while true; do
    read -p "$(echo $BOLD$GREEN"Do you wish to setup a MEILI_API_KEY for your search engine [y/n]?  "$RESET)" yn
    case $yn in
        [Yy]* ) set_master_key=true; break;;
        [Nn]* ) set_master_key=false; break;;
        * ) echo "Please answer yes or no.";
    esac
done

if [ $set_master_key = true ]; then
    # set_master_key

    while true; do
        read -p "$(echo $BOLD$GREEN"Do you wish to specify you MEILI_API_KEY (otherwise it will be generated) [y/n]? "$RESET)" yn
        case $yn in
            [Yy]* ) read -p "MEILI_API_KEY: " api_key; break;;
            [Nn]* ) api_key=$(date +%s | sha256sum | base64 | head -c 32); echo "You MEILI_API_KEY is $api_key"; echo "You should keep it somewhere safe."; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done

    cat << EOF >/etc/systemd/system/meilisearch.service
[Unit]
Description=MeiliSearch
After=systend-user-sessions.service

[Service]
Type=simple
ExecStart=/usr/bin/meilisearch
Environment="MEILI_API_KEY=$api_key"

[Install]
WantedBy=default.target
EOF
systemctl daemon-reload
systemctl restart meilisearch

fi



# ask_domain_name_setup

while true; do
    read -p "$(echo $BOLD$BLUE"Do you wish to setup a domain name [y/n]? "$RESET)" yn
    case $yn in
        [Yy]* ) ask_domain_name=true; break;;
        [Nn]* ) ask_domain_name=false; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

# ask_domain_name

if [ $ask_domain_name != true ]; then
    echo "$BOLD$GREEN Configuration is over. Thanks$RESET"
    cp -f /etc/skel/.bashrc /root/.bashrc
    exit
fi

while true; do
    read -p "$(echo $BOLD$BLUE"What is your domain name? "$RESET)" domainname
    case $domainname in
        "" ) echo "Please enter a valid domain name";;
        * ) break;;
    esac
done


# ask_ssl_configure

while true; do
    read -p "$(echo $BOLD$BLUE"Do you wish to setup ssl with certbot [y/n]? "$RESET)" yn
    case $yn in
        [Yy]* ) want_ssl=true; break;;
        [Nn]* ) want_ssl=false; break;;
        * ) echo "Please answer by writting 'y' for yes or 'n' for no.";
    esac
done

if [ $want_ssl != true ]; then
    # set_domain_name_in_nginx

    cat << EOF > /etc/nginx/sites-enabled/meilisearch
server {
listen 80 default_server;
listen [::]:80 default_server;
server_name $domainname;
location / {
    proxy_pass  http://127.0.0.1:7700;
}
}
EOF
systemctl restart nginx
    exit

else

    echo "Ok! Cool we'll setup SSL with Certbot";

    certbot --nginx -d $domainname

fi



echo "$BOLD$GREEN Configuration is over. Thanks$RESET"
cp -f /etc/skel/.bashrc /root/.bashrc


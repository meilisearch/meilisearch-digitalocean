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

USE_API_KEY="false"
MEILISEARCH_API_KEY=""
DOMAIN_NAME=""
USE_SSL="false"
USE_CERTBOT="false"

exit_with_message() {

    echo "export USE_API_KEY="$USE_API_KEY >> /var/opt/meilisearch/env
    echo "export MEILISEARCH_API_KEY="$MEILISEARCH_API_KEY >> /var/opt/meilisearch/env
    echo "export DOMAIN_NAME="$DOMAIN_NAME >> /var/opt/meilisearch/env
    echo "export USE_SSL="$USE_SSL >> /var/opt/meilisearch/env
    echo "export USE_CERTBOT="$USE_CERTBOT >> /var/opt/meilisearch/env
    source /var/opt/meilisearch/env

    echo "$BOLD$GREEN     --- OK, now we will set up MeiliSearch for you! --- $RESET"
    sh /var/opt/meilisearch/scripts/first-login/001-setup-prod.sh
    exit
}

ask_master_key_setup() {
    while true; do
        read -p "$(echo $BOLD$BLUE"Do you wish to setup a MEILI_API_KEY for your search engine [y/n]?  "$RESET)" yn
        case $yn in
            [Yy]* ) set_master_key=true; break;;
            [Nn]* ) set_master_key=false; break;;
            * ) echo "Please answer yes or no.";
        esac
    done
}

generate_master_key() {
    while true; do
        read -p "$(echo $BOLD$BLUE"Do you wish to specify you MEILI_API_KEY (otherwise it will be generated) [y/n]? "$RESET)" yn
        case $yn in
            [Yy]* ) read -p "MEILI_API_KEY: " api_key; break;;
            [Nn]* ) api_key=$(date +%s | sha256sum | base64 | head -c 32); echo "You MEILI_API_KEY is $api_key"; echo "You should keep it somewhere safe."; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

ask_domain_name_setup() {
    while true; do
        read -p "$(echo $BOLD$BLUE"Do you wish to setup a domain name [y/n]? "$RESET)" yn
        case $yn in
            [Yy]* ) ask_domain_name=true; break;;
            [Nn]* ) ask_domain_name=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

ask_domain_name_input() {
    while true; do
        read -p "$(echo $BOLD$BLUE"What is your domain name? "$RESET)" domainname
        case $domainname in
            "" ) echo "Please enter a valid domain name";;
            * ) break;;
        esac
    done
}

ask_ssl_configure() {
    while true; do
        read -p "$(echo $BOLD$BLUE"Do you wish to setup ssl with certbot [y/n]? "$RESET)" yn
        case $yn in
            [Yy]* ) want_ssl_certbot=true; break;;
            [Nn]* ) want_ssl_certbot=false; break;;
            * ) echo "Please answer by writting 'y' for yes or 'n' for no.";
        esac
    done
}

ask_has_own_ssl() {
    while true; do
        read -p "$(echo $BOLD$BLUE"Do you wish to provide your own SSL certificate [y/n]? "$RESET)" yn
        case $yn in
            [Yy]* ) has_own_ssl=true; break;;
            [Nn]* ) has_own_ssl=false; break;;
            * ) echo "Please answer by writting 'y' for yes or 'n' for no.";
        esac
    done
}

# Ask user if he wants to setup a master key for MeiliSearch

ask_master_key_setup

if [ $set_master_key = true ]; then
    generate_master_key
    USE_API_KEY="true"
    MEILISEARCH_API_KEY=$api_key
fi

# Ask user if he wants to setup a domain name for MeiliSearch

ask_domain_name_setup

if [ $ask_domain_name != true ]; then
    exit_with_message
fi

ask_domain_name_input

DOMAIN_NAME=$domainname

# Ask user if he wants to setup an SSL configuration for MeiliSearch
# [certbot or own SSL]

ask_ssl_configure

if [ $want_ssl_certbot = true ]; then
    USE_SSL="true"
    USE_CERTBOT="true"
else
    ask_has_own_ssl
fi

if [ $want_ssl_certbot = false ] && [ $has_own_ssl = true ]; then
    USE_SSL="true"
    USE_CERTBOT="false"
fi

exit_with_message
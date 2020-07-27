#!/usr/bin/env bash

# shellcheck disable=SC2154

export DEBIAN_FRONTEND="noninteractive"
sudo apt update -y
sudo apt install python3.8 git nginx certbot python3-pip tesseract-ocr tesseract-ocr-eng -y
sudo certbot certonly --noninteractive --webroot --webroot-path /var/www/html --agree-tos --email akhilnarang@thescriptgroup.in --domain poseidon.thescriptgroup.in
cat << EOF | sudo tee /etc/nginx/sites-available/poseidon.thescriptgroup.in
server {
    listen 80;
    server_name poseidon.thescriptgroup.in;
    return 301 https://poseidon.thescriptgroup.in;
}

server {
    listen 443 ssl;
    server_name poseidon.thescriptgroup.in;
    ssl_certificate /etc/letsencrypt/live/poseidon.thescriptgroup.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/poseidon.thescriptgroup.in/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location /static {
        root /home/akhil/Poseidon;
        try_files $uri $uri/ =404;
    }

    location ^~ / {
        add_header \'Access-Control-Allow-Origin\' \'*\';

        proxy_pass        http://127.0.0.1:5501;
        proxy_redirect    off;

        proxy_set_header   Host                 \$host;
        proxy_set_header   X-Real-IP            \$remote_addr;
        proxy_set_header   X-Forwarded-For      \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    \$scheme;
       
    }
}

EOF
sudo ln -s /etc/nginx/sites-available/poseidon.thescriptgroup.in /etc/nginx/sites-enabled/poseidon.thescriptgroup.in
sudo rm -fv /etc/nginx/sites-{available,enabled}/default
sudo nginx -s reload

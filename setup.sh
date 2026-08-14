#!/bin/bash
##
## # SPDX-License-Identifier: Apache-2.0
## # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
## ###
set -e

docker compose down -v
docker compose up -d

until [ "$(docker inspect -f '{{.State.Health.Status}}' woocommerce_db)" = "healthy" ]; do
  sleep 2
done

docker compose run --rm wpcli core install \
  --url=http://localhost:8080 \
  --title="My WooCommerce Store" \
  --admin_user=admin \
  --admin_password=admin123 \
  --admin_email=admin@example.com \
  --skip-email \
  --allow-root

docker compose exec wordpress sh -lc '
mkdir -p /var/www/html/wp-content/upgrade \
         /var/www/html/wp-content/uploads \
         /var/www/html/wp-content/mu-plugins &&
chown -R www-data:www-data /var/www/html/wp-content &&
chmod -R 755 /var/www/html/wp-content
'

docker compose exec wordpress sh -lc "cat > /var/www/html/wp-content/mu-plugins/enable-app-passwords.php <<'PHP'
<?php
/*
Plugin Name: Enable Application Passwords
*/
add_filter('wp_is_application_passwords_available', '__return_true');
PHP"

docker compose run --rm wpcli plugin install woocommerce --activate --allow-root

docker compose restart wordpress

python3 add_users.py

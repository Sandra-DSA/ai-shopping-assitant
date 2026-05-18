# WooCommerce Docker Setup

## Stack
- **WordPress** (latest official image) — PHP 8.3 + Apache
- **MySQL 8.0** — database
- **WP-CLI** — auto-installs WooCommerce on first boot

## Quick Start

```bash
# 1. Start everything
docker compose up -d

# 2. Watch WP-CLI install WooCommerce (takes ~30s)
docker compose logs -f wpcli

# 3. Open your store
#    Frontend: http://localhost:8080
#    Admin:    http://localhost:8080/wp-admin
```

## Default Credentials

| Field    | Value                   |
|----------|-------------------------|
| Admin    | `admin`                 |
| Password | `admin123`              |
| Email    | `admin@example.com`     |

> ⚠️ Change these before deploying to production!

## Files

| File               | Purpose                            |
|--------------------|------------------------------------|
| `docker-compose.yml` | Main compose configuration       |
| `uploads.ini`      | PHP settings (upload limits, etc.) |

## Useful Commands

```bash
# Stop all containers
docker compose down

# Stop and delete all data (fresh start)
docker compose down -v

# Open a WP-CLI shell
docker compose run --rm wpcli bash --allow-root

# Install another plugin
docker compose run --rm wpcli wp plugin install <plugin-slug> --activate --allow-root

# View logs
docker compose logs -f wordpress
```

## Production Notes

- Replace `wppassword` / `admin123` with strong secrets
- Put a reverse proxy (NGINX/Traefik) in front for HTTPS
- Mount a real SMTP plugin or configure `WORDPRESS_CONFIG_EXTRA` for email
- Use `--read-only` container flags + named upload volume for hardened deployments

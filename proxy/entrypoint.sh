#!/bin/sh

# Start Nginx in the background
nginx &

# Wait for Nginx to fully start
sleep 5s

# Request Let's Encrypt SSL certificate
certbot certonly --webroot --webroot-path=/var/www/certbot -d assignments.qrata.ai --email your-email@example.com --agree-tos --non-interactive

# Reload Nginx with the new certificate
nginx -s reload

# Run Nginx in the foreground
nginx -g "daemon off;"

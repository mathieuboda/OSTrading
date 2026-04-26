#!/bin/bash
set -e

# Export env vars so cron jobs can access them
printenv | grep -v "^_=" | grep -v "^SHLVL=" > /etc/environment

echo "Starting trading-agents cron daemon (TZ=$TZ)"
echo "Loaded $(wc -l < /etc/environment) environment variables"

exec cron -f

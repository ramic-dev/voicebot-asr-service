#!/bin/bash
set -e

echo "[entrypoint] Starting ZeroTier..."
zerotier-one -d
sleep 2

echo "[entrypoint] Joining network ${ZT_NETWORK}..."
zerotier-cli join "${ZT_NETWORK}"

echo "[entrypoint] Waiting for ZeroTier IP..."
for i in $(seq 1 60); do
    ZT_IP=$(zerotier-cli listnetworks | grep "${ZT_NETWORK}" | awk '{print $NF}' | grep -oP '[\d.]+(?=/)')
    if [ -n "$ZT_IP" ] && [ "$ZT_IP" != "-" ]; then
        echo "[entrypoint] ZeroTier IP: ${ZT_IP}"
        break
    fi
    echo "[entrypoint] Waiting... ($i/60)"
    sleep 5
done

if [ -z "$ZT_IP" ] || [ "$ZT_IP" = "-" ]; then
    echo "[entrypoint] WARNING: No ZeroTier IP. Starting on 0.0.0.0"
    ZT_IP="0.0.0.0"
fi

echo "[entrypoint] Starting ASR service on ${ZT_IP}:8001..."
exec python app.py --host "${ZT_IP}"

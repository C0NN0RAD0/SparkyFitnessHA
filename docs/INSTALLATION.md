# Installation Guide

## Prerequisites

- Home Assistant 2024.1.0 or later
- A reachable SparkyFitness server
- A valid SparkyFitness API token

## Method 1: HACS

1. Open Home Assistant Settings -> Devices and Services.
2. Open Custom repositories.
3. Add https://github.com/C0NN0RAD0/SparkyFitnessHA as Integration.
4. Install SparkyFitness.
5. Restart Home Assistant.

## Method 2: Manual

1. Copy the folder custom_components/sparkyfitness into your Home Assistant
   configuration directory under custom_components.
2. Restart Home Assistant.

## Configure the Integration

1. Open Home Assistant Settings -> Devices and Services.
2. Click Add Integration.
3. Search for SparkyFitness.
4. Enter:
   - Integration name
   - Host URL (example: http://192.168.1.100:8080)
   - API token

## Connectivity Checks

You can test your SparkyFitness API from a terminal:

curl http://192.168.1.100:8080/api/health

curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.1.100:8080/api/health

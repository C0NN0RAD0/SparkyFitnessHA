# SparkyFitness Home Assistant Integration

SparkyFitness for Home Assistant exposes nutrition, activity, sleep, hydration,
and body metrics as native sensor entities.

## Features

- Daily nutrition sensors (calories, protein, carbs, fat)
- Exercise sensors (duration, calories burned)
- Sleep sensor (hours slept)
- Body metrics (weight, body fat percentage)
- Hydration sensor (water intake)
- Mood sensor
- Config flow setup from Home Assistant UI
- Multi-entry support for multiple users/accounts
- 15-minute polling using Home Assistant coordinator pattern

## Installation

### HACS (Recommended)

1. In Home Assistant, open Settings -> Devices and Services.
2. Open Custom repositories.
3. Add repository URL: https://github.com/C0NN0RAD0/SparkyFitnessHA
4. Select category Integration.
5. Install and restart Home Assistant.

### Manual

1. Copy custom_components/sparkyfitness into your Home Assistant
   custom_components directory.
2. Restart Home Assistant.

## Configuration

1. In Home Assistant, open Settings -> Devices and Services.
2. Click Add Integration.
3. Search for SparkyFitness.
4. Enter:
   - Name: Friendly integration name
   - Host: SparkyFitness URL, for example http://192.168.1.100:8080
   - Token: API token from SparkyFitness

## Sensors

- sensor.daily_calories
- sensor.daily_protein
- sensor.daily_carbs
- sensor.daily_fat
- sensor.sleep_duration
- sensor.body_weight
- sensor.body_fat_percentage
- sensor.exercise_duration
- sensor.exercise_calories
- sensor.water_intake
- sensor.current_mood

## Documentation

- docs/INSTALLATION.md
- docs/USAGE.md
- docs/EXAMPLES.md

## License

MIT. See LICENSE.

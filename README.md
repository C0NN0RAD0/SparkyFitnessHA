# SparkyFitness Home Assistant Integration

SparkyFitness for Home Assistant exposes daily nutrition, activity, sleep, fasting, hydration, goals, and body metrics from SparkyFitness as native Home Assistant sensor entities, and registers custom actions (services) to log data back.

## Features

- **Daily Nutrition Sensors**: calories, protein, carbs, fat
- **Exercise Sensors**: duration, calories burned
- **Sleep Sensors**: duration (hours slept)
- **Fasting Tracker**: fasting status (`Fasting` / `Not Fasting`), total completed fasts, and average fast duration (hours) with active fast attributes (`start_time`, `target_end_time`, `fasting_type`, `duration_hours`)
- **Daily Goals / Targets**: daily calorie goal, daily protein goal, daily carbs goal, daily fat goal, and daily water goal
- **Hydration Sensors**: water intake (ml) with state attributes listing all available water containers (`id`, `name`, `volume`, `unit`, `is_primary`)
- **Mood Sensors**: user-friendly mood rating
- **Body Metrics**: body weight, body fat percentage, BMI, steps, and 8 body measurement sensors (neck, chest, waist, hips, thigh, calf, bicep, forearm)
- **Custom Actions (Services)**: log water (by ml or drinks), log mood, start/end fasts, and log check-ins from Home Assistant
- **Config Flow Setup**: configure directly from the Home Assistant UI
- **Multi-Entry Support**: configure multiple accounts/entries
- **5-Minute Polling**: automatic updates using Home Assistant's coordinator pattern

## Available Sensors

Once configured, the integration creates the following sensor entities in Home Assistant (prefixed with `sensor.sparky_fitness_`):

### Daily Nutrition
- `daily_calories` (kcal)
- `daily_protein` (g)
- `daily_carbs` (g)
- `daily_fat` (g)

### Hydration & Mood
- `water_intake` (ml) - includes `containers` attribute with name, volume, unit, and UUIDs
- `current_mood` (Awful, Bad, Okay, Good, Excellent)

### Daily Goals
- `daily_calorie_goal` (kcal)
- `daily_protein_goal` (g)
- `daily_carbs_goal` (g)
- `daily_fat_goal` (g)
- `daily_water_goal` (ml)

### Fasting Tracker
- `fasting_status` (State: `Fasting` or `Not Fasting` - includes `fast_id`, `start_time`, `target_end_time`, `fasting_type`, and `duration_hours` attributes)
- `total_completed_fasts`
- `average_fast_duration` (hours)

### Sleep & Exercise
- `sleep_duration` (hours)
- `exercise_duration` (minutes)
- `exercise_calories` (kcal)

### Check-in Metrics (Body Measurements)
- `body_weight` (kg)
- `body_fat` (%)
- `bmi`
- `steps`
- `neck` (cm)
- `chest` (cm)
- `waist` (cm)
- `hips` (cm)
- `thigh` (cm)
- `calf` (cm)
- `bicep` (cm)
- `forearm` (cm)

## Installation

### HACS (Recommended)

1. Open **Settings** > **Devices & Services** in Home Assistant.
2. Click the three dots in the top-right and open **Custom repositories**.
3. Add repository URL: `https://github.com/C0NN0RAD0/SparkyFitnessHA`
4. Select category: **Integration**.
5. Install and restart Home Assistant.

### Manual

1. Copy `custom_components/sparkyfitness` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. In Home Assistant, open **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Sparky Fitness**.
4. Enter:
   - **Integration name**: Friendly name for this integration instance
   - **Scheme**: `http` or `https`
   - **SparkyFitness URL**: Hostname and port (e.g. `192.168.1.100:8080`)
   - **API token**: Your API token from SparkyFitness

---

## Custom Actions (Services)

The integration registers the following custom actions (services) under the `sparkyfitness` domain:

### 1. `sparkyfitness.log_water`
Logs water intake in Sparky Fitness. You must provide either `amount_ml` or `drinks`.
- **`amount_ml`** (optional): Volume in milliliters (automatically calculated into drinks/servings based on container size).
- **`drinks`** (optional): Number of drinks/servings consumed (e.g. `1` or `4`).
- **`container`** (optional): Name (case-insensitive) or UUID of the container to log. Falls back to your primary container if omitted.

### 2. `sparkyfitness.log_mood`
Logs a daily mood entry in Sparky Fitness.
- **`mood_value`** (required): Rating from 1 (Awful) to 5 (Excellent).
- **`notes`** (optional): Notes about your day.

### 3. `sparkyfitness.start_fast`
Starts a new fasting period in Sparky Fitness.
- **`fasting_type`** (required): Fast type name (e.g., `Intermittent Fasting`, `16:8`).
- **`target_duration_hours`** (optional): Fasting goal duration.

### 4. `sparkyfitness.end_fast`
Ends the currently active fasting period in Sparky Fitness.
- **`mood_value`** (optional): Fast completion mood rating (1-5).
- **`notes`** (optional): Completion notes.

### 5. `sparkyfitness.log_check_in`
Logs daily check-in measurements.
- **`weight`** (optional): Body weight in kilograms.
- **`body_fat`** (optional): Body fat percentage.

---

## Troubleshooting & Logs

To enable debug logging for this integration:

1. Go to **Settings** > **Devices & Services** in the Home Assistant UI.
2. Click the **Sparky Fitness** integration card.
3. Click the **three dots menu** and select **Enable debug logging**.
4. Trigger the action/service you want to debug.
5. Click **Disable debug logging** in the same menu to download the log file.

Alternatively, add this to your `configuration.yaml` file:
```yaml
logger:
  default: info
  logs:
    custom_components.sparkyfitness: debug
```

## License

MIT. See LICENSE.

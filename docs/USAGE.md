# Usage Guide

## Available Sensors

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

## Automation Example

automation:
  - alias: Daily Calorie Goal Alert
    trigger:
      - platform: time
        at: "21:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.daily_calories
        below: 1800
    action:
      - service: notify.notify
        data:
          title: Fitness Goal
          message: "Calorie intake is below goal."

## Template Example

template:
  - sensor:
      - name: Daily Macros Summary
        unique_id: daily_macros_summary
        state: >
          {% set p = states('sensor.daily_protein') | float(0) %}
          {% set c = states('sensor.daily_carbs') | float(0) %}
          {% set f = states('sensor.daily_fat') | float(0) %}
          P:{{ p|round(0) }}g C:{{ c|round(0) }}g F:{{ f|round(0) }}g

## Update Interval

Data refreshes every 15 minutes by default.

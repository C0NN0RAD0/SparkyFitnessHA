# Examples

## Fitness Dashboard (Lovelace)

views:
  - title: Fitness
    path: fitness
    cards:
      - type: entities
        title: Daily Nutrition
        entities:
          - sensor.daily_calories
          - sensor.daily_protein
          - sensor.daily_carbs
          - sensor.daily_fat
          - sensor.water_intake

      - type: glance
        title: Sleep and Activity
        entities:
          - sensor.sleep_duration
          - sensor.exercise_duration
          - sensor.exercise_calories
          - sensor.current_mood

      - type: statistics-graph
        title: Weight Trend
        entities:
          - sensor.body_weight
        days_to_show: 30

## Hydration Reminder

automation:
  - alias: Hydration Reminder
    trigger:
      - platform: time_pattern
        minutes: "0"
    condition:
      - condition: numeric_state
        entity_id: sensor.water_intake
        below: 1500
    action:
      - service: notify.notify
        data:
          title: Hydration
          message: "Time to drink water."

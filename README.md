# terraform-aws-ecs-saver

A module for shutting down or scaling down ECS Service during the specified time.

## Usage

Deploy the module.

```terraform
module "ecs-saver" {
  source  = "kota65535/ecs-saver/aws"
  version = "0.4.0"

  # Default is UTC
  timezone = "Asia/Tokyo"
}
```

Then add following tags to your ECS Service.

| Tag              | Description                                                                   |
|------------------|-------------------------------------------------------------------------------|
| AutoStartTime    | Start time in 24-hour format (0-23)                                           |
| AutoStartWeekday | Space-seperated list of weekdays as integers to start (1-7, Monday to Sunday) |
| AutoStopTime     | Stop time in 24-hour format (0-23)                                            |
| AutoStopWeekday  | Space-seperated list of weekdays as integers to stop (1-7, Monday to Sunday)  |
| AutoStopCount    | Number of tasks when stopped. Default: 0                                      |

## Examples

Start at 9:00 AM and stop at 6:00 PM every day:

- AutoStartTime: `9`
- AutoStopTime: `18`

Start at 7:00 AM and stop at 10:00 PM on Tuesday:

- AutoStartTime: `7`
- AutoStopTime: `22`
- AutoStartWeekday: `2`

Start at 10:00 AM and scale down to 1 task at 2:00 AM the next day on weekdays:

- AutoStartTime: `10`
- AutoStopTime: `2`
- AutoStartWeekday: `1 2 3 4 5`
- AutoStopCount: `1`
 

# terraform-aws-ecs-saver

A module for shutting down or scaling down ECS Service during the specified time.

## Usage

Deploy the module.

```terraform
module "ecs-saver" {
  source  = "kota65535/ecs-saver/aws"
  version = "0.6.0"

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
 

## Invoke Lambda function manually

You can start/stop ECS Services manually by invoking the Lambda function.

```
aws lambda invoke --function-name ecs-saver --payload '<payload>' out
```

### Payload format

| Key      | Type           | Description                                                                                               | Example                                    |
|----------|----------------|-----------------------------------------------------------------------------------------------------------|--------------------------------------------|
| action   | string         | Operation to perform (`start` or `stop`)                                                                  | `"stop"`                                   |
| cluster  | string         | ECS cluster name. Must be used with `services`.                                                           | `"my-cluster"`                             |
| services | list of string | List of ECS service names. Must be used with `cluster`.                                                   | `["my-service-1", "my-service-2"]`         |
| tags     | list of object | List of ECS service tags in the format `{"key": <key>, "value": <value>}`. All values must match exactly. | `[{"key": "Project", "value": "awesome"}]` |

### Example

Stop `my-service-1` and `my-service-2` in `my-cluster`.

```json
{
  "action": "stop",
  "cluster": "my-cluster",
  "services": ["my-service-1", "my-service-2"]
}
```

Start all services with the tags `Project: awesome` and `Env: dev`.

```json
{
  "action": "start",
  "tags": [{"key": "Project", "value": "awesome"}, {"key": "Env", "value": "dev"}]
}
```

# terraform-aws-ecs-saver

A module for shutting down or scaling down ECS Service during the specified time.

| Tag           | Description                              |
|---------------|------------------------------------------|
| AutoStopTime  | Stop time in 24-hour format (0-23)       |
| AutoStartTime | Start time in 24-hour format (0-23)      |
| StoppedCount  | Number of tasks when stopped. Default: 0 |

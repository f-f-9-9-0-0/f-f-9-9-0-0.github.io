---
title: "Logging in Apache Airflow"
layout: post
date: 2024-03-14 01:00
image: /assets/images/001/skycrapers.jpg
illustration: /assets/images/articles/execution-log.svg
headerImage: true
tag:
- logging
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Can you see your logs? DEBUG vs. INFO
excerpt_separator: <!--more-->
---
## Logging for tasks

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.8.2!
    </p>
</aside>

Logging is very important for each application, as without supporting lines of operation history it would be challenging to understand what happened.  

Airflow is using the standard Python `logging` module to handle logs efforts from tasks. This module is extensively documented on [python.org].  

Logging in Airflow is pretty much documented here: [logging_for_tasks]
<!--more-->

## Where is my log? I am debugging..

Ok, so we have logs and we are still deep in development. Perfect use case for writing some debug information into the logs. Wait! I cannot find that..  

The reason is, by default, logging is set to level `INFO` in Airflow configuration, e.g. check in [Airflow configuration][airflow_configuration]
This means that logs at the level of `DEBUG` aren't logged. To see `DEBUG` logs when debugging your Python tasks, you need to set `AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG` or change the value of `logging_level` in `airflow.cfg`  

## If you have ever wondered about where INFO level is being set

The [settings module][settings.py] includes an `INFO` logging constant, but effective task logging is configured through Airflow’s logging configuration and handlers. Use the `[logging] logging_level` setting for the standard setup; custom logging configurations can impose additional logger or handler thresholds.

## Samples, samples

Below you can see a sample DAG specification to highlight logging capabilities:

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_logging.py</span> <span>Python</span></figcaption>

```python
import pendulum, logging
from airflow.decorators import dag, task

# Creates logger object
# By default, logging is set to level INFO in Airflow configuration
# e.g. chek here https://{ID}-{region}.composer.googleusercontent.com/configuration
#   For example, by default the airflow.task logger is set at the level of INFO,
#   which means that logs at the level of DEBUG aren't logged. To see DEBUG logs
#   when debugging your Python tasks, you need to set
#   AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG or change the value of logging_level
#   in airflow.cfg
task_logger = logging.getLogger(__name__)
task_logger.setLevel(logging.DEBUG)

doc_md_task = """
  # Purpose of this task:
  This is an empty task
"""
@task(
  doc_md = doc_md_task
)
def another_empty_task():
  pass

doc_md_task = """
  # Purpose of this task:
  Print something, using the Python function `print` to stdout
"""
@task(
  doc_md = doc_md_task
)
def print_something():
  print("This is a test `print`")

doc_md_task = """
  # Purpose of this task:
  Log messages at different levels
"""
@task(
  doc_md    = doc_md_task
)
def log_something():
  task_logger.debug("This is a test DEBUG log")
  task_logger.info("This is a test INFO log")
  task_logger.warning("This is a test WARNING log")
  task_logger.error("This is a test ERROR log")
  task_logger.critical("This is a test CRITICAL log")

  task_logger.log(logging.INFO, "This is a test INFO log again")

doc_md_DAG = """
  # This DAG is about to test logging

  ## Creating a logger object
  By default, logging is set to level **INFO** in Airflow configuration,  
  e.g. check here [Airflow configuration]  
  > For example, by default the airflow.task logger is set at the level of INFO,  
  > which means that logs at the level of DEBUG aren't logged. To see DEBUG logs  
  > when debugging your Python tasks, you need to set  
  > AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG or change the value of logging_level  
  > in airflow.cfg  

  [Airflow configuration]: <https://{ID}-{region}.composer.googleusercontent.com/configuration>
"""
@dag(
  dag_id      = "dag_example_logging",
  start_date  = pendulum.datetime(2021, 1, 1, tz="UTC"),
  schedule    = None,
  tags        = [ "example" ],
  doc_md      = doc_md_DAG
)
def dag_example_logging():
  another_empty_task()
  print_something()
  log_something()

dag_example_logging()
```

</figure>

[logging_for_tasks]: https://airflow.apache.org/docs/apache-airflow/2.8.2/administration-and-deployment/logging-monitoring/logging-tasks.html#writing-to-task-logs-from-your-code
[python.org]: https://docs.python.org/3/howto/logging.html
[airflow_configuration]: https://airflow.apache.org/docs/apache-airflow/2.8.2/configurations-ref.html#logging-level
[settings.py]: https://github.com/apache/airflow/blob/2.8.2/airflow/settings.py

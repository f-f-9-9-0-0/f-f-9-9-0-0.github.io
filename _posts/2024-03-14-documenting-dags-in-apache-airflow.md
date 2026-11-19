---
title: "Documenting DAGs in Apache Airflow"
layout: post
date: 2024-03-14 02:00
image: /assets/images/001/reading.jpg
illustration: /assets/images/articles/documented-workflow.svg
headerImage: true
tag:
- docs
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Add it, use it, documentation!
excerpt_separator: <!--more-->
---
## Documenting DAGs

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.8.2!
    </p>
</aside>

One of the most important tasks a developer can do is documenting, at least, the non-straightforward parts of the logic behing the code.  
Airflow provides a wide range of options for this effort which are ready to use and help out.  
<!--more-->

## At which level shall I add docs?

Documentation can be added at different levels in Airflow:
- at the DAG's level
- at the tasks' level

## Which form of docs?

At the **task level**, Airflow supports `doc` for monospace text and the following rich-content attributes: `doc_md`, `doc_yaml`, `doc_rst` and `doc_json`. At the **DAG level**, only `doc_md` is interpreted. See the [Airflow 2.8.2 documentation][airflow_docs].
- markdown ([->][markdown])
- YAML ([->][yaml])
- reStructuredText ([->][reStructuredText])
- JSON ([->][json])

## Where is docs in the UI?

DAG level docs can be found in a dropdown box below the top menu.  
Task level docs can be reached through the *More details* link.
{% include article-image.html src="/assets/images/001/dag_docs.png" alt="DAG level docs" %}
{% include article-image.html src="/assets/images/001/task_docs.png" alt="DAG level docs" %}

## Samples

Find a basic sample of code how it looks like in Python:

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_documentation.py</span> <span>Python</span></figcaption>

```python
import datetime
import logging
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
doc_monospace_task = """
  This is another form of creating docs.
"""
doc_yaml_task = """
  overall_topic: logging
  details: |
      - docs: true
      - logging: true
"""
doc_rst_task = """
  ===========
  This feature is pretty neat
  ===========

  * there are many ways to add docs
  * luckily Airflow supports a lot of them
"""
doc_json_task = """
{
  "logging levels": {
    "notset": {
      "level"         : "logging.NOTSET",
      "numeric_value" : 0,
      "usage"         : "When set on a logger, indicates that ancestor loggers are to be consulted to determine the effective level. If that still resolves to NOTSET, then all events are logged. When set on a handler, all events are handled."
    },
    "notset": {
      "level"         : "logging.DEBUG",
      "numeric_value" : 10,
      "usage"         : "Detailed information, typically only of interest to a developer trying to diagnose a problem."
    },
    "notset": {
      "level"         : "logging.INFO",
      "numeric_value" : 20,
      "usage"         : "Confirmation that things are working as expected."
    },
    "notset": {
      "level"         : "logging.WARNING",
      "numeric_value" : 30,
      "usage"         : "An indication that something unexpected happened, or that a problem might occur in the near future (e.g. ‘disk space low’). The software is still working as expected."
    },
    "notset": {
      "level"         : "logging.ERROR",
      "numeric_value" : 40,
      "usage"         : "Due to a more serious problem, the software has not been able to perform some function."
    },
    "notset": {
      "level"         : "logging.CRITICAL",
      "numeric_value" : 50,
      "usage"         : "A serious error, indicating that the program itself may be unable to continue running."
    }
  }
}
"""
@task(
  doc_md    = doc_md_task,
  doc       = doc_monospace_task,
  doc_json  = doc_json_task,
  doc_yaml  = doc_yaml_task,
  doc_rst   = doc_rst_task
)
def log_something():
  task_logger.debug("This is a test DEBUG log")
  task_logger.info("This is a test INFO log")
  task_logger.warning("This is a test WARNING log")
  task_logger.error("This is a test ERROR log")
  task_logger.critical("This is a test CRITICAL log")

  task_logger.log(logging.INFO, "This is a test INFO log again")

doc_md_DAG = """
  # This DAG is about to test DAG documentation
"""
@dag(
  dag_id      = "dag_example_documentation",
  start_date  = datetime.datetime(2023, 1, 1),
  schedule    = None,
  tags        = [ "example" ],
  doc_md      = doc_md_DAG
)
def dag_example_documentation():
  another_empty_task()
  print_something()
  log_something()

dag_example_documentation()
```

</figure>

[markdown]: https://www.markdownguide.org/
[yaml]: https://yaml.org/
[reStructuredText]: https://docutils.sourceforge.io/rst.html
[json]: https://www.json.org/json-en.html

[airflow_docs]: https://airflow.apache.org/docs/apache-airflow/2.8.2/core-concepts/dags.html#dag-task-documentation

---
title: "Logging in Apache Airflow"
layout: post
date: 2024-03-14 01:00
image: /assets/images/001/airflow.png
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
# Logging for tasks
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.8.2!
    </p>
</div>

Logging is very important for each application, as without supporting lines of operation history it would be challenging to understand what happened.  
<br>

Airflow is using the standard Python `logging` module to handle logs efforts from tasks. This module is extensively documented on [python.org].  
<br>

Logging in Airflow is pretty much documented here: [logging_for_tasks]
<br>
<!--more-->
<br>
<br>

# Where is my log? I am debugging..

Ok, so we have logs and we are still deep in development. Perfect use case for writing some debug information into the logs. Wait! I cannot find that..  
<br>

The reason is, by default, logging is set to level `INFO` in Airflow configuration, e.g. check in [Airflow configuration][airflow_configuration]
This means that logs at the level of `DEBUG` aren't logged. To see `DEBUG` logs when debugging your Python tasks, you need to set `AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG` or change the value of `logging_level` in `airflow.cfg`  
<br>
<br>

# If you have ever wondered about where INFO level is being set

Logging level is being set in Python code, explicitly in the [airflow/settings.py][settings.py] file: `LOGGING_LEVEL = logging.INFO`
<br>
<br>

# Samples, samples

Below you can see a sample DAG specification to highlight logging capabilities:
<script src="https://gist.github.com/f-f-9-9-0-0/66a923aeb0b005f5ce7c6d5b8784ecad.js"></script>


[logging_for_tasks]: https://airflow.apache.org/docs/apache-airflow/2.8.2/administration-and-deployment/logging-monitoring/logging-tasks.html#writing-to-task-logs-from-your-code
[python.org]: https://docs.python.org/3/howto/logging.html
[airflow_configuration]: https://{ID}-{region}.composer.googleusercontent.com/configuration
[settings.py]: https://github.com/apache/airflow/blob/main/airflow/settings.py

---
title: "Apache Airflow Dataset Dependencies"
layout: post
date: 2024-02-09 00:00
image: /assets/images/airflow.png
headerImage: true
tag:
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Airflow datasets unleashed
---

## Datasets in Apache Airflow
<div>
    <p style="background-color:#7569CC;color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.7.3!
    </p>
</div>


There are multiple ways of triggering a DAG Run in Airflow:
- Through a `schedule interval` specified when [creating the DAG][creating_the_DAG]
- Using [*Data-aware scheduling*][data_aware_scheduling] which introduces the concept of `datasets`
- Trigger from another DAG Run using operator [*TriggerDagRunOperator*][triggerdagrunoperator]
- Manually trigger a DAG Run
- Programmatically using [*Airflow REST Api*][airflow_rest_api]

[Sensors][sensors], a special type of [Operator][operator], are a way of controlling an already triggered DAG Run by making it deferred until certain events occur and re-trigger its execution from the point it stopped running.

[creating_the_DAG]: https://airflow.apache.org/docs/apache-airflow/2.7.3/administration-and-deployment/scheduler.html
[data_aware_scheduling]: https://airflow.apache.org/docs/apache-airflow/2.7.3/authoring-and-scheduling/datasets.html
[triggerdagrunoperator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/_api/airflow/operators/trigger_dagrun/index.html
[airflow_rest_api]: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run
[sensors]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/sensors.html
[operator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/operators.html

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
- Through a `schedule interval` specified when [creating the DAG](https://airflow.apache.org/docs/apache-airflow/2.7.3/administration-and-deployment/scheduler.html)
- Using [*Data-aware scheduling*](https://airflow.apache.org/docs/apache-airflow/2.7.3/authoring-and-scheduling/datasets.html) which introduces the concept of `datasets`
- Trigger from another DAG Run using operator [*TriggerDagRunOperator*](https://airflow.apache.org/docs/apache-airflow/2.7.3/_api/airflow/operators/trigger_dagrun/index.html)
- Manually trigger a DAG Run
- Programmatically using [*Airflow REST Api*](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run)

[Sensors](https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/sensors.html), a special type of [Operator](https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/operators.html), are a way of controlling an already triggered DAG Run by making it deferred until certain events occur and re-trigger its execution from the point it stopped running.

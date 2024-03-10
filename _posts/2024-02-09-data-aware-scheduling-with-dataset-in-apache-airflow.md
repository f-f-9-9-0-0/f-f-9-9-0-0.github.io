---
title: "Data-aware scheduling with Datasets in Apache Airflow"
layout: post
date: 2024-02-09 00:00
image: /assets/images/001/airflow.png
headerImage: true
tag:
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Airflow datasets unleashed
excerpt_separator: <!--more-->
---
# Datasets in Apache Airflow
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
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
<!--more-->
[Sensors][sensors], a special type of [Operator][operator], are a way of controlling an already triggered DAG Run by making it deferred until certain events occur and re-trigger its execution from the point it stopped running.

---

Dependencies are **very much required** in a complex environment, especially if you need to deal with a data analytics platform.  
Certain data moves can happen only after some transformation already being done on source or other loads completed successfully.  

There are several ways of expressing these dependencies in code, such as using *tasks in a DAG implementing all the steps of data manipulation*, or simply just *triggering other DAGs with Operators* which group together all tasks related to steps on a specific tables.  

There are even more crazy solutions, for example storing all dependencies in an external storage (e.g. file or database) and use **Dynamic Task Mapping** to build *all dependencies among tables in one single DAG*.  
Or another way is to take full control of dependencies and build a meta table somewhere, which can be *polled with a certain frequency by DAGs checking for dependencies*, or even build an **event-driven system** by introducing a messaging service or application, which can trigger DAGs.

---

All these can work, however would come with more effort when it comes to development and can introduce a lot of customizations, which would make maintenance difficult and cause a hard time for new comers to get up to speed with.

For this exact use case, to build a data platform with Airflow, there is a **built-in feature** Airflow provides, called `datasets`.

Do not think of anything related to data from data management perspective when you hear the term *dataset*, especially do not associate it with datasets in Google's BigQuery. A dataset in Airflow's world refers to a [URI][uri_wiki] (*Uniform Resource Identifier*) only (actually a string) which can be used as a way of communication among DAGs.

While a dataset does not represent data on its own, we can still consider this solution as a **data-aware scheduling** solution, as if we identify a certain set of data with a dataset.  

This is how the *official documentation* describes a `dataset`:
> An Airflow dataset is a stand-in for a logical grouping of data.  
> Airflow makes no assumptions about the content or location of the data represented by the URI.




[creating_the_DAG]: https://airflow.apache.org/docs/apache-airflow/2.7.3/administration-and-deployment/scheduler.html
[data_aware_scheduling]: https://airflow.apache.org/docs/apache-airflow/2.7.3/authoring-and-scheduling/datasets.html
[triggerdagrunoperator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/_api/airflow/operators/trigger_dagrun/index.html
[airflow_rest_api]: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run
[sensors]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/sensors.html
[operator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/operators.html
[uri_wiki]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

---
title: "Data-aware scheduling with Datasets in Apache Airflow"
layout: post
date: 2024-02-09 00:00
image: /assets/images/001/airflow.png
headerImage: true
tag:
- data-aware scheduling
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
## Complex environments lead to.. dependencies

Dependencies are **very much required** in a complex environment, especially if you need to deal with a data analytics platform.  
Certain data moves can happen only after some transformation already being done on source or other loads completed successfully.  

There are several ways of expressing these dependencies in code, such as using *tasks in a DAG implementing all the steps of data manipulation*, or simply just *triggering other DAGs with Operators* which group together all tasks related to steps on a specific tables.  

There are even more crazy solutions, for example storing all dependencies in an external storage (e.g. file or database) and use **Dynamic Task Mapping** to build *all dependencies among tables in one single DAG*.  
Or another way is to take full control of dependencies and build a meta table somewhere, which can be *polled with a certain frequency by DAGs checking for dependencies*, or even build an **event-driven system** by introducing a messaging service or application, which can trigger DAGs.

---
## Less effort, datasets!

All these can work, however would come with more effort when it comes to development and can introduce a lot of customizations, which would make maintenance difficult and cause a hard time for new comers to get up to speed with.

For this exact use case, to build a data platform with Airflow, there is a **built-in feature** Airflow provides, called `datasets`.

Do not think of anything related to data from data management perspective when you hear the term *dataset*, especially do not associate it with datasets in Google's BigQuery. A dataset in Airflow's world refers to a [URI][uri_wiki] (*Uniform Resource Identifier*) only (actually a string) which can be used as a way of communication among DAGs.

While a dataset does not represent data on its own, we can still consider this solution as a **data-aware scheduling** solution, as if we identify a certain set of data with a dataset.  

This is how the *official documentation* describes a `dataset`:
> An Airflow dataset is a stand-in for a logical grouping of data.  
> Airflow makes no assumptions about the content or location of the data represented by the URI.

---
## The concept

Datasets are there like `OK files` on a Linux file system. If an application wants to trigger another, for example when it completes its operation, it creates an empty file with the proper timestamp, just like an OK file. The other application can realise the completion of the first one by checking on the file, and can get event the exact timestamp of that event.  

Datasets are the same, one DAG updates them (specially the timestamp associated with them) and other DAGs can be triggered depending on those.  

One DAG can depend on multiple datasets and can also update multiple datasets during its run. To be more precise, datasets are updated by *task instances*, not the DAG itself, which means those updates can happen even before the DAG completes, so other DAGs can start their execution and run in parallel with the source DAG.  
Another interesting aspect of this is that datasets are not necessarily updated by a DAG, during a run, just imagine a branch of the acyclic graph of tasks which gets skipped.

---
## Let's code

When it comes to coding, we can specify upstream and downstream datasets, not other DAGs themselves.  
Upstream datasets are passed in argument `schedule` of a DAG. So the DAG itself depends on the dataset.  
Downstream datasets are specified in the argument `outlets` of tasks when those are specified.  
Both can accept lists of instances of class `Dataset`.

There are two upstream datasets which DAG `example_upstream_datasets` depends on in the below example:  
<script src="https://gist.github.com/f-f-9-9-0-0/6d22dbe61ff4b1717d1e53eb88ae395b.js"></script>

And this is the DAG which updates those two datasets: `example_downstream_datasets`  
**NOTE:** While the name of the *Python variables* are different (`ds_003` and `ds_004`) than in the previous DAG, the string for the datasets are the same (`any_string_001` and `any_string_002`)  
<script src="https://gist.github.com/f-f-9-9-0-0/ddf908525fed6fc99618b19a297d8bed.js"></script>

On the *Airflow UI*, you can get a nice representation of these dependencies in the form of a directed acyclic graph, by clicking on the **Datasets** item in the navbar:  
![Airflow UI Datasets](/assets/images/001/airflow_ui.png)

---

Ok, you can ask a very valid question: *What if there is no guarantee in the Python code that the task instance, updating the datasets, gets executed? Would Airflow still identify a dependency between the DAG and the datasets or the Processor results in an error when parsing the file?*  
The answer is **yes**, Airflow still record the dependency, however datasets might not be updated by all the runs of the actual DAG.  
  
Let's see the below example DAG, which has a branch in itself, resulting in an update for only one of the two datasets at a time:  
<script src="https://gist.github.com/f-f-9-9-0-0/3dd72b1f003512556edc065c61d4c84a.js"></script>

Still the dependencies are recorded by Airflow, even though datasets are not updated by every run:  
![Airflow UI Branch Datasets](/assets/images/001/airflow_ui2.png)
![Airflow UI Branch DAG](/assets/images/001/airflow_ui3.png)


[creating_the_DAG]: https://airflow.apache.org/docs/apache-airflow/2.7.3/administration-and-deployment/scheduler.html
[data_aware_scheduling]: https://airflow.apache.org/docs/apache-airflow/2.7.3/authoring-and-scheduling/datasets.html
[triggerdagrunoperator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/_api/airflow/operators/trigger_dagrun/index.html
[airflow_rest_api]: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run
[sensors]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/sensors.html
[operator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/operators.html
[uri_wiki]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

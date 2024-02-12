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

Do not think of anything related to data from data management perspective, when you here the term *dataset*. Dataset here refers to a [URI][uri_wiki] (*Uniform Resource Identifier*) only (a string) which can be used as a way of communication among DAGs.

While a dataset does not represent data on its own, we can still consider this solution as a **data-aware scheduling** solution, as if we identify a certain set of data with a dataset.  

This is how the *official documentation* describes a `dataset`:
> An Airflow dataset is a stand-in for a logical grouping of data.  
> Airflow makes no assumptions about the content or location of the data represented by the URI.

<br>
<br>

# How does this work?
<br>

The concept is simple, one DAG *touches* the dataset (updates its `last updated timestamp`) while another depends on the same.  
The **Scheduler** periodically checks on the DAGs and datasets in its [database backend][database_backend], and if there is a match, *which means a DAG can be triggered as the dataset (it depends on) was updated already*, then the latter DAG is selected for a run.

<div style="margin:10px;padding:5px;background-color:#fef0d2">
    <p>
        <b style="font-weight: bold">IMPORTANT</b><br>
        The <b style="font-weight: bold">Scheduler</b> compares the dependant DAG's last execution time to the dataset's last update time (<b style="font-weight: bold">for datasets one timestamp is being preserved only for updates</b>)
        <br>
        <img src="/assets/images/001/dataset_erd.png" alt="ERD Schema of the Database">
    </p>
</div>

---

References from a DAG to a dataset of which it is a consumer (**consuming DAGs**) are being stored in table `dag_schedule_dataset_reference`
This table is being populated when the the DAG Processor processes Python files (with the followinf chain of functions):
1. processor.py [def process_file] ->  
2. processor.py [def save_dag_to_db] ->
3. dagbag.py [def _sync_to_db] ->
4. dag.py [def bulk_write_to_db] ->
5. DagScheduleDatasetReference()

---

When a new **dataset** is being created then a record is being added to the backend database table `dataset` ([def create_datasets][def_create_datasets])

If a **task updates a dataset** then a record is being added to the table `dataset_event` with all the DAG Run's details ([def register_dataset_change][def_register_dataset_change])  
At the same time puts all DAGs, which consumes the updated dataset, into the queue and creates a record in table `dataset_dag_run_queue` (*storing dataset events that need processing*)

---

The scheduler gathers all DAGs where a DAG Run is needed after a dataset update, and triggers a DAG Run for each of them. The following chain of function calls serves this purpose: [def _execute -> def _do_scheduling -> def _run_scheduler_loop -> def _create_dagruns_for_dags -> def _create_dag_runs_dataset_triggered][func_chain]  
The DAG IDs, *where all datasets are updated which the DAG depends on*, are being retrieved by this query from the backend database ([def dags_needing_dagruns][def_dags_needing_dagruns]):
```sql
select
    dsdr.dag_id,
    max(ddrq.created_at) last_queued_time,
    min(ddrq.created_at) first_queued_time
from
        dag_schedule_dataset_reference dsdr
    left outer join
        dataset_dag_run_queue ddrq
    on
        dsdr.dataset_id = ddrq.dataset_id and
        dsdr.dag_id = ddrq.target_dag_id
group by
    dsdr.dag_id
having
    count() = sum(
                    case
                        when ddrq.target_dag_id <> NULL then 1
                        else 0
                    end
                )
```
The **latest dataset update timestamp** is being considered (`last_queued_time` from the query above) for each consumer DAG as a filter later on.  
<br>
For each consumer DAG (collected above), gets the last **DAG Run** execution with the below 2 conditions satisfied:
- execution started before the **latest dataset update timestamp** and
- triggered by **datasets**  

```sql
select
    *
from
    dag_run
where
    dag_id = <dag_id> and
    execution_date < <last_queued_time> and
    run_type = 'dataset_triggered'
order by
    execution_date desc
limit 1
```

```sql
select
    de.*
from
        dag_schedule_dataset_reference dsdr
    inner join
        dataset_event de
    on
        dsdr.dataset_id = de.dataset_id
    inner join
        # retrieve DAG Run details which updated the dataset (NOT the consumer)
        dag_run dr
    on
        dr.dag_id = de.source_dag_id and
        dr.run_id = de.source_run_id
where
    # this filter is for the consumer DAG ID
    dsdr.dag_id = <dag_id> and
    de.timestamp < <last_queued_time> and
    # this condition is applicable only if there is a previous DAG Run available
    # for the CONSUMER DAG
    # execution_date comes from the previous query
    de.timestamp > <execution_date from previous DAG Run, if any>
```

---

Once the DAG Run is started, all records for the triggered DAG is being removed from table `dataset_dag_run_queue` with the below SQL:
```sql
delete from dataset_dag_run_queue where target_dag_id = <dag_id>
```


```python
    def create_datasets(self, dataset_models: list[DatasetModel], session: Session) -> None:
        """Create new datasets."""
        for dataset_model in dataset_models:
            session.add(dataset_model)
        session.flush()

        for dataset_model in dataset_models:
            self.notify_dataset_created(dataset=Dataset(uri=dataset_model.uri, extra=dataset_model.extra))
```



dataset_dag_run_queue: Model for storing dataset events that need processing.
dag_schedule_dataset_reference: References from a DAG to a dataset of which it is a consumer.
task_outlet_dataset_reference: References from a task to a dataset that it updates / produces.

dataset_event: A table to store datasets events.
dagrun_dataset_event: ?




[creating_the_DAG]: https://airflow.apache.org/docs/apache-airflow/2.7.3/administration-and-deployment/scheduler.html
[data_aware_scheduling]: https://airflow.apache.org/docs/apache-airflow/2.7.3/authoring-and-scheduling/datasets.html
[triggerdagrunoperator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/_api/airflow/operators/trigger_dagrun/index.html
[airflow_rest_api]: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run
[sensors]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/sensors.html
[operator]: https://airflow.apache.org/docs/apache-airflow/2.7.3/core-concepts/operators.html
[uri_wiki]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
[database_backend]: https://airflow.apache.org/docs/apache-airflow/2.7.3/howto/set-up-database.html
[def_create_datasets]: https://github.com/apache/airflow/blob/main/airflow/datasets/manager.py
[def_register_dataset_change]: https://github.com/apache/airflow/blob/main/airflow/datasets/manager.py
[func_chain]: https://github.com/apache/airflow/blob/main/airflow/jobs/scheduler_job_runner.py
[def_dags_needing_dagruns]: https://github.com/apache/airflow/blob/main/airflow/models/dag.py

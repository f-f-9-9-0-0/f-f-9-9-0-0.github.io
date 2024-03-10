---
title: "Apache Airflow Datasets Under The Hoods"
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
description: Airflow datasets under the hoods
excerpt_separator: <!--more-->
---
# Datasets in Apache Airflow
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.8.1!
    </p>
</div>

You can find a general introduction to `datasets` in [my other post][link_to_other_post], while I go into details in this one and show you what happens under the hoods if you start to deal with `datasets` in Apache Airflow.
<!--more-->
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

When a new **dataset** is being specified as the value for the `outlet` parameter in a *task* then a record is being added to the backend database table `dataset`.

References from a DAG to a dataset of which it is a consumer (**consuming DAGs**) are being stored in table `dag_schedule_dataset_reference`

These above tables are being populated when the the DAG Processor parses Python files (with the following chain of functions):
1. [airflow\dag_processing\processor.py][airflow\dag_processing\processor.py] [`DagFileProcessor::process_file()`] ->
    Process a Python file containing Airflow DAGs.

    This includes:

    1. Execute the file and look for DAG objects in the namespace.
    2. Execute any Callbacks if passed to this method.
    3. Serialize the DAGs and save it to DB (or update existing record in the DB).
    4. Pickle the DAG and save it to the DB (if necessary).
    5. Mark any DAGs which are no longer present as inactive
    6. Record any errors importing the file into ORM

2. processor.py [def save_dag_to_db] ->
3. dagbag.py [def _sync_to_db] ->
4. dag.py [def bulk_write_to_db] ->
5. DagScheduleDatasetReference()

---

If a **DAG Run's task updates a dataset** then a record is being added to the table `dataset_event` with all the DAG Run's details ([def register_dataset_change][def_register_dataset_change])  
At the same time all DAGs, which consumes the updated dataset, are being put into the queue and a record is added to the table `dataset_dag_run_queue` (*storing dataset events that need processing*)

---

The *Scheduler* gathers all DAGs in its loop where a DAG Run is needed after a dataset update, and triggers a DAG Run for each of them. The following [chain of function calls][func_chain]  serves this purpose:
1. def _execute ->
2. def _do_scheduling ->
3. def _run_scheduler_loop ->
4. def _create_dagruns_for_dags ->
5. def _create_dag_runs_dataset_triggered
  
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

[link_to_other_post]: /data-aware-scheduling-with-dataset-in-apache-airflow

[airflow\dag_processing\processor.py]: https://github.com/apache/airflow/blob/main/airflow/dag_processing/processor.py

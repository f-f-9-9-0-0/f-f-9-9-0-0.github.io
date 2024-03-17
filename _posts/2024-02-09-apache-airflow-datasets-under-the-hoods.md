---
title: "Apache Airflow Datasets Under The Hoods"
layout: post
date: 2024-02-09 01:00
image: /assets/images/001/ufo.jpg
headerImage: true
tag:
- data-aware scheduling
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
        &nbsp;This post is created based on the Airflow version 2.8.2!
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

---

Datasets, as per above, are being used as:
- for `schedule` at the *DAG level*
- `outlets` at the *task level*
  
Based on this, datasets used for scheduling a DAG are being registered (stored in Airflows internal database) when the DAG Processor processes the DAG's file.  
While datasets used as outlets of tasks are not necessarily updated throughout the execution of the DAG (imagine a branch which got skipped) these are still getting registered.  

<div style="margin:10px;padding:5px;background-color:#fef0d2">
    <p>
        <b style="font-weight: bold">IMPORTANT</b><br>
        The <b style="font-weight: bold">Scheduler</b> compares the dependant DAG's last execution time to the dataset's last update time (<b style="font-weight: bold">for datasets one timestamp is being preserved only for updates</b>)
        <br>
        <a href="https://airflow.apache.org/docs/apache-airflow/stable/database-erd-ref.html" alt="ERD Schema of the Database"><img src="/assets/images/001/dataset_erd.png" alt="ERD Schema of the Database"></a>
        <br>
        <a href="https://airflow.apache.org/docs/apache-airflow/stable/database-erd-ref.html" alt="ERD Schema of the Database"><img src="/assets/images/001/dataset_erd2.png" alt="ERD Schema of the Database"></a>
    </p>
</div>

---

When a new **dataset** is being specified as the value for the `outlet` parameter in a *task* then a record is being added to the backend database table `dataset`.

References from a DAG to a dataset of which it is a consumer (**consuming DAGs**) are being stored in table `dag_schedule_dataset_reference`

These above tables are being populated when the the DAG Processor parses Python files (with the following chain of functions):
1. [airflow\dag_processing\processor.py][airflow\dag_processing\processor.py]  
   [`DagFileProcessor::process_file()`]

    > Process a Python file containing Airflow DAGs.
    > 
    > This includes:
    > 
    > 1. Execute the file and look for DAG objects in the namespace.
    > 2. Execute any Callbacks if passed to this method.
    > 3. Serialize the DAGs and save it to DB (or update existing record in the DB).
    > 4. Pickle the DAG and save it to the DB (if necessary).
    > 5. Mark any DAGs which are no longer present as inactive
    > 6. Record any errors importing the file into ORM

2. [airflow\dag_processing\processor.py][airflow\dag_processing\processor.py]  
   [`DagFileProcessor::save_dag_to_db()`]

3. [airflow\models\dagbag.py][airflow\models\dagbag.py]  
   [`DagFileProcessor::_sync_to_db()`]
    > Save attributes about list of DAG to the DB.

4. [airflow\models\dag.py][airflow\models\dag.py]  
   [`DAG.bulk_write_to_db()`]

   > Ensure the DagModel rows for the given dags are up-to-date in the dag table in the DB.

5. [airflow\models\dataset.py][airflow\models\dataset.py]  
   [`DagScheduleDatasetReference()`]
   > reconcile dag-schedule-on-dataset references

   [`TaskOutletDatasetReference()`]
   > reconcile task-outlet-dataset references

---

If a **DAG Run's task updates a dataset** then a record is being added to the table `dataset_event` with all the DAG Run's details ([airflow\models\manager.py][airflow\models\manager.py])  
[`DatasetManager::register_dataset_change()`]
> Register dataset related changes.
> For local datasets, look them up, record the dataset event, queue dagruns, and broadcast the dataset event

At the same time all DAGs, which consumes the updated dataset, are being put into the queue and a record is added to the table `dataset_dag_run_queue` ([airflow\models\manager.py][airflow\models\manager.py])  
[`DatasetManager::_queue_dagruns()`]  
-> [`DatasetManager::_postgres_queue_dagruns()`]  
-> -> [airflow\models\dataset.py][airflow\models\dataset.py] [`DatasetDagRunQueue`]

---

The *Scheduler* gathers all DAGs in its loop where a DAG Run is needed after a dataset update, and triggers a DAG Run for each of them. The following chain of function calls serves this purpose ([airflow\jobs\scheduler_job_runner.py][airflow\jobs\scheduler_job_runner.py]):
1. [`SchedulerJobRunner::_execute()`]  
   
2. [`SchedulerJobRunner::_run_scheduler_loop()`]  
   
3. [`SchedulerJobRunner::_do_scheduling()`]  
    > Make the main scheduling decisions.
    >
    > Creates any necessary DAG runs by examining the next_dagrun_create_after column of DagModel
    >   Since creating Dag Runs is a relatively time consuming process, we select only 10 dags by default (configurable via ``scheduler.max_dagruns_to_create_per_loop`` setting)
    >
    > Finds the "next n oldest" running DAG Runs to examine for scheduling (n=20 by default, configurable via ``scheduler.max_dagruns_per_loop_to_schedule`` config setting) and tries to progress state (TIs to SCHEDULED, or DagRuns to SUCCESS/FAILURE etc)
    > By "next oldest", we mean hasn't been examined/scheduled in the most time.
    >
    > Then, via a Critical Section (locking the rows of the Pool model) we queue tasks, and then send them to the executor.

4. [`SchedulerJobRunner::_create_dagruns_for_dags()`]  
    > Find Dag Models needing DagRuns and Create Dag Runs with retries in case of OperationalError.  

    -> [`DagModel::dags_needing_dagruns()`] ([airflow\models\dag.py][airflow\models\dag.py])  
    > Return (and lock) a list of Dag objects that are due to create a new DagRun.
    > This will return a resultset of rows that is row-level-locked with a "SELECT ... FOR UPDATE" query

    -> [`SchedulerJobRunner::_create_dag_runs_dataset_triggered()`]  
    > For DAGs that are triggered by datasets, create dag runs.
    > Once the DAG Run is started, all records for the triggered DAG is being removed from table dataset_dag_run_queue

    -> [`Dag::create_dagrun()`] ([airflow\models\dag.py][airflow\models\dag.py])  
    > Create a dag run from this dag including the tasks associated with this dag.  

    -> [`DagRun`] ([airflow\models\dagrun.py][airflow\models\dagrun.py])

5. [`SchedulerJobRunner::_start_queued_dagruns()`]  
    > Find DagRuns in queued state and decide moving them to running state.
  
The DAG IDs in step **4.**, *where all datasets are updated which the DAG depends on*, are being retrieved by this query from the backend database [`DagModel::dags_needing_dagruns()`] ([airflow\models\dag.py][airflow\models\dag.py]):
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

Records for the triggered DAG is being removed from table `dataset_dag_run_queue` with the below SQL [`SchedulerJobRunner::_create_dag_runs_dataset_triggered()`] ([airflow\jobs\scheduler_job_runner.py][airflow\jobs\scheduler_job_runner.py]):
```sql
delete from dataset_dag_run_queue where target_dag_id = <dag_id>
```




[database_backend]: https://airflow.apache.org/docs/apache-airflow/stable/database-erd-ref.html
[airflow\dag_processing\processor.py]: https://github.com/apache/airflow/blob/main/airflow/dag_processing/processor.py
[airflow\models\dagbag.py]: https://github.com/apache/airflow/blob/main/airflow/models/dagbag.py
[airflow\models\dag.py]: https://github.com/apache/airflow/blob/main/airflow/models/dag.py
[airflow\models\dagrun.py]: https://github.com/apache/airflow/blob/main/airflow/models/dagrun.py
[airflow\models\dataset.py]: https://github.com/apache/airflow/blob/main/airflow/models/dataset.py
[airflow\models\manager.py]: https://github.com/apache/airflow/blob/main/airflow/datasets/manager.py
[airflow\jobs\scheduler_job_runner.py]: https://github.com/apache/airflow/blob/main/airflow/jobs/scheduler_job_runner.py

[link_to_other_post]: /data-aware-scheduling-with-dataset-in-apache-airflow

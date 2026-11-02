---
title: "Automatic execution of Dags after unpausing in Apache Airflow"
layout: post
date: 2025-05-06 00:00
image: /assets/images/001/office.jpg
illustration: /assets/images/articles/scheduled-runs.svg
headerImage: true
tag:
- catchup
- orchestration
- apache
- airflow
category: blog
author: gabor
description: First execution of Dags with a schedule are automatic but the way it happens might not be straightforward.
excerpt_separator: <!--more-->
---
## Unpausing a Dag

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.10.4!
    </p>
</aside>

There is an Airflow configuration, that you can set in `airflow.cfg` file or using environment variables, which describes if a Dag gets unpaused right after creating it or if that could be done separately (e.g. manually or through APIs)

This configuration is managed by `dags_are_paused_at_creation` in the file or through the `AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION` environment variable and the default value is `True`.  
More on the Airflow configuration options you can find [here][dags_are_paused_at_creation].

<!--more-->

## DagRuns created

Unpausing a DAG allows the scheduler to create eligible runs. It does not guarantee an immediate run: the timetable, start/end dates and concurrency limits still apply. The examples below use an hourly data-interval schedule with completed intervals available.
However that is not the same how Airflow forms DagRuns for each Dag.

The difference comes from the `catchup` and `depends_on_past` definitions of Dags.  

### `catchup`

If this value is not set at Dag level, then the default Airflow configuration value comes in. This value can be set in the above mentioned configuration file (`catchup_by_default`) or through the environment variable `AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT`. In Airflow 2.10.4, the default is **`True`**. A DAG can override it with `catchup=False`. Further details [here][catchup_by_default].

**False**  
An Airflow DAG defined with a `start_date`, possibly an `end_date`, and a non-asset `schedule`, defines a series of intervals which the scheduler turns into individual DAG runs and executes.  
When catchup is disabled, either on the DAG or through `scheduler.catchup_by_default=False`, the scheduler does not create runs for every missed historical interval.
The scheduler creates a DAG run **only for the latest interval**.

**True**  
With `catchup=True`, the scheduler creates runs for eligible completed intervals that are missing, subject to the DAG’s date bounds and scheduling limits. Clearing tasks in an existing run makes those task instances eligible to run again; it does not create another DAG run for that interval.
This concept is called `Catchup`.

### `depends_on_past`

You can require a task to wait for its previous instance to succeed or be skipped.
To use this, you just need to set the `depends_on_past` argument on your Task to True.

Set `depends_on_past` on a task or through the DAG’s `default_args`. It constrains successive instances of that task; a previous instance in a successful or skipped state satisfies this dependency. It does **not** serialize whole DAG runs: a task in the next run can proceed while a different task in the previous run is still executing. To limit a DAG to one active run, set `max_active_runs=1`. See [task dependencies][baseoperator] and [DAG concurrency][dag_api].

Note that if you are running the DAG at the very start of its life—specifically, its first ever automated run—then the Task will still run, as there is no previous run to depend on.

## Sample
The `catchup=False` example has one task. The two `catchup=True` examples each have a `sleep` task followed by a `print_task`, allowing task-level dependencies across runs to be observed.

### `dag_example_catchup_false`

This Dag has only one task to demonstrate how DagRuns are generated once the newly created Dag gets unpaused.  
As the `dag.catchup` value is **False**, the scheduler would create a single DagRun for the last completed data interval (based on `schedule`, *in this case this is the last completed hour*) and the scheduler will execute it.

Executed only once for the last completed data interval:  
{% include article-image.html src="/assets/images/001/dag_example_catchup_false.jpg" alt="DagRuns created after unpausing the Dag" %}

### `dag_example_catchup_true_simultaneous`
This example has two tasks, `sleep` followed by `print_task`.
As the `dag.catchup` value is **True**, the scheduler would create a DAG Run for each completed interval between the `start_date` and the last completed data interval (based on `schedule`, *in this case this is the last completed hour*) and their tasks may execute concurrently because `depends_on_past=False`. Actual concurrency still depends on active-run limits, task limits, pools and executor capacity.

Executed for all the completed data intervals as soon as a free slot got available:  
{% include article-image.html src="/assets/images/001/dag_example_catchup_true_simultaneous.jpg" alt="DagRuns created after unpausing the Dag" %}

### `dag_example_catchup_true_depends_on_past`

This example also has two tasks, `sleep` followed by `print_task`.
As the `dag.catchup` value is **True**, the scheduler would create a Dag Run for each completed interval between the `start_date` and the last completed data interval (based on `schedule`, *in this case this is the last completed hour*) and each task waits for its own previous instance because `depends_on_past=True`. DAG runs can still overlap; this is task-level ordering, not whole-run serialization.

Executed for all the completed data intervals and while multiple DagRuns got started at almost the same time, their tasks waited for the most recent previous DagRun's same tasks to complete before got started (very close `Start Date` with an increased `Duration` as data intervals increase for DagRuns):  
{% include article-image.html src="/assets/images/001/dag_example_catchup_true_depends_on_past.jpg" alt="DagRuns created after unpausing the Dag" %}

### Source code for all Dags

{% include gist.html id="f-f-9-9-0-0/fd08d111db57ec86e2af058c2c5ac142" %}

[dags_are_paused_at_creation]: https://airflow.apache.org/docs/apache-airflow/2.10.4/configurations-ref.html#dags-are-paused-at-creation
[catchup_by_default]: https://airflow.apache.org/docs/apache-airflow/2.10.4/configurations-ref.html#catchup-by-default

[baseoperator]: https://airflow.apache.org/docs/apache-airflow/2.10.4/_api/airflow/models/baseoperator/index.html
[dag_api]: https://airflow.apache.org/docs/apache-airflow/2.10.4/_api/airflow/models/dag/index.html

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

If the Dag gets created with a valid schedule then it gets executed when unpaused, which means DagRuns get created.  
However that is not the same how Airflow forms DagRuns for each Dag.

The difference comes from the `catchup` and `depends_on_past` definitions of Dags.  

### `catchup`

If this value is not set at Dag level, then the default Airflow configuration value comes in. This value can be set in the above mentioned configuration file (`catchup_by_default`) or through the environment variable `AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT`. Further details [here][catchup_by_default].

**False**  
An Airflow DAG defined with a `start_date`, possibly an `end_date`, and a non-asset `schedule`, defines a series of intervals which the scheduler turns into individual DAG runs and executes.  
By default, DAG runs **that have not been run** since the last data interval are not created by the scheduler upon activation of a DAG (Airflow config `scheduler.catchup_by_default=False`).  
The scheduler creates a DAG run **only for the latest interval**.

**True**  
If you set `catchup=True` in the DAG, the scheduler will kick off a DAG Run for **any data interval** that has not been run since the last data interval (or has been cleared).  
This concept is called `Catchup`.

### `depends_on_past`

You can also say a task can only run if the previous run of the **task** in the previous DAG Run succeeded.  
To use this, you just need to set the `depends_on_past` argument on your Task to True.

Set at the *task level* or as a `default_arg` for all tasks at the *Dag level*. When set to **True**, the task instance must wait for the **same task** in the **most recent DAG run** to be **successful**. This ensures sequential data loads and allows only one Dag run to be executed at a time *in most cases*.

Note that if you are running the DAG at the very start of its life—specifically, its first ever automated run—then the Task will still run, as there is no previous run to depend on.

## Sample
Below Dags have only one task to demonstrate how DagRuns are generated once the newly created Dags get unpaused.

### `dag_example_catchup_false`

This Dag has only one task to demonstrate how DagRuns are generated once the newly created Dag gets unpaused.  
As the `dag.catchup` value is **False**, the scheduler would create a single DagRun for the last completed data interval (based on `schedule`, *in this case this is the last completed hour*) and the scheduler will execute it.

Executed only once for the last completed data interval:  
{% include article-image.html src="/assets/images/001/dag_example_catchup_false.jpg" alt="DagRuns created after unpausing the Dag" %}

### `dag_example_catchup_true_simultaneous`
This Dag has only one task to demonstrate how DAG Runs are generated once the newly created DAG gets unpaused.  
As the `dag.catchup` value is **True**, the scheduler would create a DAG Run for each completed interval between the `start_date` and the last completed data interval (based on `schedule`, *in this case this is the last completed hour*) and the scheduler will execute them **simultaneously** as `dag.default_args.depends_on_past` is set to **False**.  

Executed for all the completed data intervals as soon as a free slot got available:  
{% include article-image.html src="/assets/images/001/dag_example_catchup_true_simultaneous.jpg" alt="DagRuns created after unpausing the Dag" %}

### `dag_example_catchup_true_depends_on_past`

This Dag has only one task to demonstrate how Dag Runs are generated once the newly created Dag gets unpaused.  
As the `dag.catchup` value is **True**, the scheduler would create a Dag Run for each completed interval between the `start_date` and the last completed data interval (based on `schedule`, *in this case this is the last completed hour*) and the scheduler will execute them **sequentially** as `dag.default_args.depends_on_past` is set to **True**.

Executed for all the completed data intervals and while multiple DagRuns got started at almost the same time, their tasks waited for the most recent previous DagRun's same tasks to complete before got started (very close `Start Date` with an increased `Duration` as data intervals increase for DagRuns):  
{% include article-image.html src="/assets/images/001/dag_example_catchup_true_depends_on_past.jpg" alt="DagRuns created after unpausing the Dag" %}

### Source code for all Dags

{% include gist.html id="f-f-9-9-0-0/fd08d111db57ec86e2af058c2c5ac142" %}

[dags_are_paused_at_creation]: https://airflow.apache.org/docs/apache-airflow/2.10.4/configurations-ref.html#dags-are-paused-at-creation
[catchup_by_default]: https://airflow.apache.org/docs/apache-airflow/2.10.4/configurations-ref.html#catchup-by-default

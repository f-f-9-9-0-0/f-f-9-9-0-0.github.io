---
title: "Downside of Using Datasets in Apache Airflow"
layout: post
date: 2024-03-14 00:00
image: /assets/images/001/gallery.jpg
illustration: /assets/images/articles/dataset-boundaries.svg
headerImage: true
tag:
- data-aware scheduling
- orchestration
- apache
- airflow
category: blog
author: gabor
description: The good and what else?
excerpt_separator: <!--more-->
---
## Datasets in Apache Airflow

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.8.2!
    </p>
</aside>

You can find a general introduction to `datasets` in [my other post][link_to_other_post], while I go into details on the downsides of using datasets in this one.
<!--more-->

---

## Dataset updates do not align business dates

Airflow 2.8.2 stores individual dataset events and pending updates for consuming DAGs. A DAG scheduled on multiple datasets becomes eligible once each has a pending update; it does not require those updates to represent the same business date. See the [scheduling documentation][dataset_scheduling] and [internal implementation walkthrough][link_under_the_hoods].

Imagine that you have 2 DAGs (`dagA` and `dagB`), updating 1 dataset each (**dagA** updates `dsA` and **dagB** updates `dsB`). And there is a third DAG (`dagC`) which depends on both datasets.  
The concept is to run both **dagA** and **dagB** once and then trigger **dagC**, all these on a daily basis.  
Huhh, **dagA** is a really heavy boy, running for an hour at least before updting dataset **dsA**. **dagB** is the tiny one, completing in seconds!

But what happens if **dagB** fails once?  

---

**dagA** updated its dataset already on day 1 (when **dagB** failed), and here comes day 2. Ok, so both **dagA** and **dagB** starts again, and **dagB** completes fast as it always does. Resulting in an updated **dsB**.  
The pending update for **dsA** from day 1 has not yet been consumed. When **dsB** updates on day 2, both dependencies have pending updates, making **dagC** eligible to run even though **dagA** is still processing day 2. The issue is the absence of business-date matching, not a lack of event history.

So in this weird case, **dagA** and **dagC** are running in parallel, which might not be the proper way of execution. Depends on your use case, of course though, for example loading a table and its source at the same time sounds like a bad idea.

[link_to_other_post]: /data-aware-scheduling-with-dataset-in-apache-airflow
[link_under_the_hoods]: /apache-airflow-datasets-under-the-hoods

[dataset_scheduling]: https://airflow.apache.org/docs/apache-airflow/2.8.2/authoring-and-scheduling/datasets.html#multiple-datasets

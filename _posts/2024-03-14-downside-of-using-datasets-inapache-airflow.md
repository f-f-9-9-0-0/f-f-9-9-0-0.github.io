---
title: "Downside of Using Datasets in Apache Airflow"
layout: post
date: 2024-03-14 00:00
image: /assets/images/001/gallery.jpg
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
# Datasets in Apache Airflow
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.8.2!
    </p>
</div>

You can find a general introduction to `datasets` in [my other post][link_to_other_post], while I go into details on the downsides of using datasets in this one.
<!--more-->
<br>
<br>

---

# Multiple events with one timestamp, ouch!

All datasets have only 1 `updated_at` timestamp stored in Airflow's supporting database. Further details I went through in [a previous post][link_under_the_hoods].

Imagine that you have 2 DAGs (`dagA` and `dagB`), updating 1 dataset each (**dagA** updates `dsA` and **dagB** updates `dsB`). And there is a third DAG (`dagC`) which depends on both datasets.  
The concept is to run both **dagA** and **dagB** once and then trigger **dagC**, all these on a daily basis.  
Huhh, **dagA** is a really heavy boy, running for an hour at least before updting dataset **dsA**. **dagB** is the tiny one, completing in seconds!
<br>

But what happens if **dagB** fails once?  

---

**dagA** updated its dataset already on day 1 (when **dagB** failed), and here comes day 2. Ok, so both **dagA** and **dagB** starts again, and **dagB** completes fast as it always does. Resulting in an updated **dsB**.  
But wait **dsA** is updated on day 1 already and that update is not 'used' yet (*remember we have only one timestamp dor each dataset..*), so when **dsB** gets updted, the *Scheduler* sees all conditions are met to trigger **dagC**. But wait, **dagA** is still running on day 2!
<br>

So in this weird case, **dagA** and **dagC** are running in parallel, which might not be the proper way of execution. Depends on your use case, of course though, for example loading a table and its source at the same time sounds like a bad idea.


[link_to_other_post]: /data-aware-scheduling-with-dataset-in-apache-airflow
[link_under_the_hoods]: /apache-airflow-datasets-under-the-hoods

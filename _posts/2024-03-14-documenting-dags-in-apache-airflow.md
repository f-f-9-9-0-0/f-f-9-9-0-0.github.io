---
title: "Documenting DAGs in Apache Airflow"
layout: post
date: 2024-03-14 02:00
image: /assets/images/001/reading.jpg
illustration: /assets/images/articles/documented-workflow.svg
headerImage: true
tag:
- docs
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Add it, use it, documentation!
excerpt_separator: <!--more-->
---
## Documenting DAGs

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.8.2!
    </p>
</aside>

One of the most important tasks a developer can do is documenting, at least, the non-straightforward parts of the logic behing the code.  
Airflow provides a wide range of options for this effort which are ready to use and help out.  
<!--more-->

## At which level shall I add docs?

Documentation can be added at different levels in Airflow:
- at the DAG's level
- at the tasks' level

## Which form of docs?

At the **task level**, Airflow supports `doc` for monospace text and the following rich-content attributes: `doc_md`, `doc_yaml`, `doc_rst` and `doc_json`. At the **DAG level**, only `doc_md` is interpreted. See the [Airflow 2.8.2 documentation][airflow_docs].
- markdown ([->][markdown])
- YAML ([->][yaml])
- reStructuredText ([->][reStructuredText])
- JSON ([->][json])

## Where is docs in the UI?

DAG level docs can be found in a dropdown box below the top menu.  
Task level docs can be reached through the *More details* link.
{% include article-image.html src="/assets/images/001/dag_docs.png" alt="DAG level docs" %}
{% include article-image.html src="/assets/images/001/task_docs.png" alt="DAG level docs" %}

## Samples

Find a basic sample of code how it looks like in Python:
{% include gist.html id="f-f-9-9-0-0/a469906e5ea70883258ee81c7f96c405" %}

[markdown]: https://www.markdownguide.org/
[yaml]: https://yaml.org/
[reStructuredText]: https://docutils.sourceforge.io/rst.html
[json]: https://www.json.org/json-en.html

[airflow_docs]: https://airflow.apache.org/docs/apache-airflow/2.8.2/core-concepts/dags.html#dag-task-documentation

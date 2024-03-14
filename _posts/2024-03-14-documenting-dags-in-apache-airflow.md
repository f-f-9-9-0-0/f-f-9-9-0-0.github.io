---
title: "Documenting DAGs in Apache Airflow"
layout: post
date: 2024-03-14 02:00
image: /assets/images/001/airflow.png
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
# Documenting DAGs
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.8.2!
    </p>
</div>

One of the most important tasks a developer can do is documenting, at least, the non-straightforward parts of the logic behing the code.  
Airflow provides a wide range of options for this effort which are ready to use and help out.  
<br>
<!--more-->
<br>
<br>

# At which level shall I add docs?
<br>

Documentation can be added at different levels in Airflow:
- at the DAG's level
- at the tasks' level
<br>
<br>

# Which form of docs?
<br>

Documentation can be created in various forms, which all has their benefit:
- markdown ([->][markdown])
- YAML ([->][yaml])
- reStructuredText ([->][reStructuredText])
- JSON ([->][json])
<br>
<br>

# Where is docs in the UI?
<br>

DAG level docs can be found in a dropdown box below the top menu.  
Task level docs can be reached through the *More details* link.
![DAG level docs](/assets/images/001/dag_docs.png)
<br>
![DAG level docs](/assets/images/001/task_docs.png)
<br>
<br>

# Samples
<br>

Find a basic sample of code how it looks like in Python:
<script src="https://gist.github.com/f-f-9-9-0-0/a469906e5ea70883258ee81c7f96c405.js"></script>


[markdown]: https://www.markdownguide.org/
[yaml]: https://yaml.org/
[reStructuredText]: https://docutils.sourceforge.io/rst.html
[json]: https://www.json.org/json-en.html

---
title: "XCom values and how to make it work in Apache Airflow"
layout: post
date: 2025-05-05 00:00
image: /assets/images/001/xcom.jpg
headerImage: true
tag:
- xcom
- jinja
- templating
- orchestration
- apache
- airflow
category: blog
author: gabor
description: XCom is the standard way for tasks to comunicate with each other though there are certain limitations.
excerpt_separator: <!--more-->
---
# XCom _(short for “cross-communications”)_
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.10.4!
    </p>
</div>

While this the standard mechanism to transfer data among tasks, there are certain limitations where XComs can be used.  
One of these is to use XCom values only for fields included in the operators' `template_fields` private attribute.
<br>

<!--more-->
<br>
<br>

# `template_fields` and how to hack it

Reason is, when processing the Python code, Airflow translates an XCom output from the form of TaskFlow API to a string template, including a `task_instance.xcom_pull` function call for the Jinja engine to render.
<br>

As I mentioned earlier in [this post][link_to_other_post], Jinja templating is a very powerful way of interacting with Airflow in runtime.
<br>

If the field is not up to be rendered (not in the `template_fields` list) then the string will not be touched and the raw value the downstream task gets, not the XCom value set be the upstream task.
<br>

The sample Dag `dag_example_xcom` below have 2 upstream tasks, which sets XCom values and 3 downstream tasks which pulls those values.  
The transfer of data also works from within a task group and data can be pulled by tasks in task groups.
<br>

![XCom tasks](/assets/images/001/xcom_tasks.jpg)
<br>

<script src="https://gist.github.com/f-f-9-9-0-0/8c82f1495e8d42e59a67637975bc25d1.js"></script>
<br>

The output of the task `xcom_target` clearly shows the difference, as only template fields are getting the XCom values form the Jinja engine, other fields remain as raw strings:
```
      template0: this is output0
      template1: this is output0
      template2: this is output0
      template3: this is output0
      other0   : \{\{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
      other1   : \{\{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
      other2   : \{\{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
      other3   : \{\{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
```
<br>

**NOTE:** Fields `other0`and `other1` have exactly the same string being set, demonstrating how Airflow translates the TaskFlow API Python code into a Jinja template _(same applies to fields `other2` and `other3`)_  
The source code for this task:
<br>

![Source code for target task](/assets/images/001/xcom_target_code.jpg)
<br>

---
<br>

To overcome this sort of limitation, for example if you have a built in operator which comes with Airflow, and you have a field which is not in the list of `template_fields`, but you would still need to have an XCom value there, well in this case you can create a custom class inherited from the actual operator and include the fields you need in the list.  
An example for this you can see in the code, using the class `AnotherCustomOperator`.  
Field `other0` is added to the list and therefore the value for this field also gets rendered and the XCom value can be used _(output is from task `another_xcom_target`)_:
```
      template0: this is output0
      template1: this is output0
      template2: this is output0
      template3: this is output0
      other0   : this is output0 <<----------- This is the rendered value
      other1   : \{\{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
      other2   : \{\{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
      other3   : \{\{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') \}\}
```
<br>

[link_to_other_post]: /jinja-templating-in-use-for-apache-airflow

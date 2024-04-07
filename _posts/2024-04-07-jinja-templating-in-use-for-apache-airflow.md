---
title: "Jinja Templating in Use for Apache Airflow"
layout: post
date: 2024-04-07 00:00
image: /assets/images/001/disguise.jpg
headerImage: true
tag:
- jinja
- templating
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Jinja and the templates
excerpt_separator: <!--more-->
---
# Jinja templating
<br>

<div style="margin:10px;padding:5px;background-color:#7569cc;color:white">
    <p style="color:white">
        <b style="font-weight: bold">&nbsp;IMPORTANT</b><br>
        &nbsp;This post is created based on the Airflow version 2.8.4!
    </p>
</div>

Templating is a powerful way of passing data to the processing part of task instances. Providing a simple mechanism, it is easy to manage, without the need of using XCom or any custom code for implementing it.
<br>

[Jinja][jinja_docs] is a templating engine, which uses placeholders in the template allow writing code similar to Python syntax. The template is passed data to render the final document.
<br>
<!--more-->
<br>
<br>

# Variables, Python instances?

There are numerous variables you can include in your templates. These variables are being replaces with instances of Python classes during rendering the template.  
A complete list of variables available can be found [here][templates_reference].
<br>

When you include a variable in the template (e.g. {% raw %}`{{ run_id }}`{% endraw %}) then the engine replaces it with the corresponding Python class (`str` in case of `run_id`).  
Then you can use all the attributes and functions available for the actual class.  
This can be even more exciting if we have a more complex class.
<br>
<br>

# Samples, samples

## DAG details
<br>
For example, if you use a variable representing an instance of the class `DAG`, then you can use all the class's attributes in your templates.  
A string is passed  as an argument to a Python operator which the templates variables are being replaced into.  
Print current DAG's details (class `DAG`, specified in [airflow\models\dag.py][dag.py]):
<script src="https://gist.github.com/f-f-9-9-0-0/16dd8ff2d8c61cd8774cc4003fdc0ba8.js"></script>
<br>
The output looks like this:
```
    Current DAG details:
      dag_id                          : dag_example_jinja_objects_dag
      description                     : None
      schedule_interval               : None
      timetable                       : <***.timetables.simple.NullTimetable object at 0x7fa7e2fb6e80>
      start_date                      : 2021-01-01 00:00:00+00:00
      end_date                        : None
      full_filepath                   : /opt/***/dags/dag_example_jinja_objects_dag.py
      template_searchpath             : None
      template_undefined              : <class 'jinja2.runtime.StrictUndefined'>
      user_defined_macros             : None
      user_defined_filters            : None
      default_args                    : {}
      concurrency                     : 16
      max_active_tasks                : 16
      max_active_runs                 : 16
      dagrun_timeout                  : None
      sla_miss_callback               : None
      default_view                    : grid
      orientation                     : LR
      catchup                         : False
      on_success_callback             : None
      on_failure_callback             : None
      doc_md                          : 
    This DAG has only one task to demonstrate the
    capabilities of Jinja templating.
  
      params                          : {}
      access_control                  : None
      is_paused_upon_creation         : None
      jinja_environment_kwargs        : None
      render_template_as_native_obj   : False
      tags                            : []
      owner_links                     : {}
      auto_register                   : True
      fail_stop                       : False
```

<br>

---

<br>

## DAG Run details
<br>
Or another example of printing the current and the previous DAG Run's details (note that you can use functions, even static or class level functions of instances replaced, class `DagRun`, specified in [airflow\models\dagrun.py][dagrun.py]):  
<script src="https://gist.github.com/f-f-9-9-0-0/c7b887852e33bbb9385686a255eca7cc.js"></script>
<br>
The output looks like this:
```
    Current DAG Run details:
      id                        : 4370
      dag_id                    : dag_example_jinja_objects_dag_run
      queued_at                 : 2024-04-07 20:18:11.513862+00:00
      execution_date            : 2024-04-07 20:18:11.481910+00:00
      start_date                : 2024-04-07 20:18:12.299231+00:00
      end_date                  : None
      _state                    : running
      run_id                    : manual__2024-04-07T20:18:11.481910+00:00
      creating_job_id           : None
      external_trigger          : True
      run_type                  : manual
      conf                      : {}
      data_interval_start       : 2024-04-07 20:18:11.481910+00:00
      data_interval_end         : 2024-04-07 20:18:11.481910+00:00
      last_scheduling_decision  : 2024-04-07 20:18:13.676411+00:00
      dag_hash                  : 17e32a0a219858e03ef180893ed1d1a8
      log_template_id           : 2
      updated_at                : 2024-04-07 20:18:13.680604+00:00

    Previous DAG Run details:
      id                        : 4368
      dag_id                    : dag_example_jinja_objects_dag_run
      queued_at                 : 2024-04-07 20:17:35.537650+00:00
      execution_date            : 2024-04-07 20:17:35.514557+00:00
      start_date                : 2024-04-07 20:17:36.468197+00:00
      end_date                  : 2024-04-07 20:17:38.835246+00:00
      _state                    : failed
      run_id                    : manual__2024-04-07T20:17:35.514557+00:00
      creating_job_id           : None
      external_trigger          : True
      run_type                  : manual
      conf                      : {}
      data_interval_start       : 2024-04-07 20:17:35.514557+00:00
      data_interval_end         : 2024-04-07 20:17:35.514557+00:00
      last_scheduling_decision  : 2024-04-07 20:17:38.831393+00:00
      dag_hash                  : 97a538401f97b0a6cef06fd8f5cebd74
      log_template_id           : 2
      updated_at                : 2024-04-07 20:17:38.836489+00:00
```

<br>

---

<br>

## Task instances' details
<br>
Another example to print all the task instances' details of the current DAG Run (note that you can use *Jinja control elements*, like loops in the templates, class `TaskInstance` is specified in [airflow\models\taskinstance.py][taskinstance.py]):  
<script src="https://gist.github.com/f-f-9-9-0-0/f249b12543a72749d66b814cee2bd698.js"></script>
<br>
The output looks like this:
```
    All task instances' details of the current DAG Run:
      
        task_id                     : print_task
        dag_id                      : dag_example_jinja_objects_ti
        run_id                      : manual__2024-04-07T20:28:22.436164+00:00
        map_index                   : -1
        start_date                  : 2024-04-07 20:28:27.385585+00:00
        end_date                    : None
        duration                    : None
        state                       : running
        _try_number                 : 1
        max_tries                   : 0
        hostname                    : ************
        unixname                    : ***
        job_id                      : 10011
        pool                        : default_pool
        pool_slots                  : 1
        queue                       : default
        priority_weight             : 1
        operator                    : _PythonDecoratedOperator
        custom_operator_name        : @task
        queued_dttm                 : 2024-04-07 20:28:22.827421+00:00
        queued_by_job_id            : 9808
        pid                         : 1705
        executor_config             : {}
        updated_at                  : 2024-04-07 20:28:27.561034+00:00
        external_executor_id        : 237d6c7b-7f71-4320-97bc-ea74f84eecc2
        trigger_id                  : None
        trigger_timeout             : None
        next_method                 : None
        next_kwargs                 : None
```

<br>

---

<br>

## Task instances' details through class `BaseOperator`
<br>
This example uses the class `BaseOperator` to print details of the current task instance (class `BaseOperator` is specified in [airflow\models\baseoperator.py][baseoperator.py]):  
<script src="https://gist.github.com/f-f-9-9-0-0/c111be4437080501ee4af066d7cf6587.js"></script>
<br>
The output looks like this:
```
    Current task instance's details for the current DAG Run:
      task_id                               : print_task  -  (a unique, meaningful id for the task)
      owner                                 : ***  -  (the owner of the task. Using a meaningful description)
      email                                 : None  -  (the 'to' email address(es) used in email alerts. This can be a)
      email_on_retry                        : True  -  (Indicates whether email alerts should be sent when a)
      email_on_failure                      : True  -  (Indicates whether email alerts should be sent when)
      retries                               : 0  -  (the number of retries that should be performed before)
      retry_delay                           : 0:05:00  -  (delay between retries, can be set as ``timedelta`` or)
      retry_exponential_backoff             : False  -  (allow progressively longer waits between)
      max_retry_delay                       : None  -  (maximum delay interval between retries, can be set as)
      start_date                            : 2021-01-01 00:00:00+00:00  -  (The ``start_date`` for the task, determines)
      end_date                              : None  -  (if specified, the scheduler won't go beyond this date)
      depends_on_past                       : False  -  (when set to true, task instances will run)
      wait_for_past_depends_before_skipping : False  -  (when set to true, if the task instance)
      wait_for_downstream                   : False  -  (when set to true, an instance of task)
      dag                                   : <DAG: dag_example_jinja_objects_base_operator>  -  (a reference to the dag the task is attached to (if any))
      priority_weight                       : 1  -  (priority weight of this task against other task.)
      weight_rule                           : downstream  -  (weighting method used for the effective total)
      queue                                 : default  -  (which queue to target when running this job. Not)
      pool                                  : default_pool  -  (the slot pool this task should run in, slot pools are a)
      pool_slots                            : 1  -  (the number of pool slots this task should use (>= 1))
      sla                                   : None  -  (time by which the job is expected to succeed. Note that)
      execution_timeout                     : None  -  (max time allowed for the execution of)
      on_failure_callback                   : None  -  (a function or list of functions to be called when a task instance)
      on_execute_callback                   : None  -  (much like the ``on_failure_callback`` except)
      on_retry_callback                     : None  -  (much like the ``on_failure_callback`` except)
      on_success_callback                   : None  -  (much like the ``on_failure_callback`` except)
      pre_execute                           : <bound method BaseOperator.pre_execute of <Task(_PythonDecoratedOperator): print_task>>  -  (a function to be called immediately before task)
      post_execute                          : <bound method BaseOperator.post_execute of <Task(_PythonDecoratedOperator): print_task>>  -  (a function to be called immediately after task)
      trigger_rule                          : all_success  -  (defines the rule by which dependencies are applied)
      resources                             : None  -  (A map of resource parameter names (the argument names of the)
      run_as_user                           : None  -  (unix username to impersonate while running the task)
      max_active_tis_per_dag                : None  -  (When set, a task will be able to limit the concurrent)
      max_active_tis_per_dagrun             : None  -  (When set, a task will be able to limit the concurrent)
      executor_config                       : {}  -  (Additional task-level configuration parameters that are)
      do_xcom_push                          : True  -  (if True, an XCom is pushed containing the Operator's)
      multiple_outputs                      : False  -  (if True and do_xcom_push is True, pushes multiple XComs, one for each)
      task_group                            : <***.utils.task_group.TaskGroup object at 0x7fa7e2faa970>  -  (The TaskGroup to which the task should belong. This is typically provided when not)
      doc                                   : None  -  (Add documentation or notes to your Task objects that is visible in)
      doc_md                                : None  -  (Add documentation (in Markdown format) or notes to your Task objects)
      doc_rst                               : None  -  (Add documentation (in RST format) or notes to your Task objects)
      doc_json                              : None  -  (Add documentation (in JSON format) or notes to your Task objects)
      doc_yaml                              : None  -  (Add documentation (in YAML format) or notes to your Task objects)
```


[jinja_docs]: https://jinja.palletsprojects.com/en/3.1.x/
[templates_reference]: https://airflow.apache.org/docs/apache-airflow/2.7.3/templates-ref.html
[dag.py]: https://github.com/apache/airflow/blob/main/airflow/models/dag.py
[dagrun.py]: https://github.com/apache/airflow/blob/main/airflow/models/dagrun.py
[taskinstance.py]: https://github.com/apache/airflow/blob/main/airflow/models/taskinstance.py
[baseoperator.py]: https://github.com/apache/airflow/blob/main/airflow/models/baseoperator.py

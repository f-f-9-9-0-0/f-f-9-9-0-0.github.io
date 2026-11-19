---
title: "Jinja Templating in Use for Apache Airflow"
layout: post
date: 2024-04-07 00:00
image: /assets/images/001/disguise.jpg
illustration: /assets/images/articles/template-rendering.svg
headerImage: true
tag:
- jinja
- templating
- orchestration
- apache
- airflow
category: blog
author: gabor
description: Use Airflow context variables and Jinja templates to inspect DAGs, DAG runs and task instances.
excerpt_separator: <!--more-->
---
## Jinja templating

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.8.4!
    </p>
</aside>

Templating is a powerful way of passing data to the processing part of task instances. Templates expose runtime context and configured values. They do not replace XCom for exchanging computed results between tasks, although a template can call `xcom_pull()` to access those results.

[Jinja][jinja_docs] is a templating engine, which uses placeholders in the template allow writing code similar to Python syntax. The template is passed data to render the final document.
<!--more-->

## Variables, Python instances?

There are numerous variables you can include in your templates. These names refer to values and objects in the rendering context.
A complete list of variables available can be found [here][templates_reference].

For example, {% raw %}`{{ run_id }}`{% endraw %} evaluates the `run_id` value from the context, which is a string. Expressions can access permitted attributes and methods of context objects; Jinja does not replace a variable with its Python class. By default the rendered result is a string. Airflow can instead use native-object rendering when `render_template_as_native_obj=True`.
This can be even more exciting if we have a more complex class.

## Samples, samples

### DAG details
For example, if you use a variable representing an instance of the class `DAG`, then you can use all the class's attributes in your templates.  
A string is passed  as an argument to a Python operator which the templates variables are being replaced into.  
Print current DAG's details (class `DAG`, specified in [airflow\models\dag.py][dag.py]):

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_jinja_objects_dag.py</span> <span>Python</span></figcaption>

{% raw %}
```python
import pendulum
from airflow.decorators import dag, task

@task
def print_task(print_me):
    print(print_me)

@dag(
  start_date = pendulum.datetime(2021, 1, 1, tz="UTC"),
  schedule   = None,
  catchup    = False
)
def dag_example_jinja_objects_dag():
  """
    This DAG has only one task to demonstrate the
    capabilities of Jinja templating.
  """

  what_to_print = '''
    Current DAG details:
      dag_id                          : {{ dag.dag_id }}
      description                     : {{ dag.description }}
      schedule_interval               : {{ dag.schedule_interval }}
      timetable                       : {{ dag.timetable }}
      start_date                      : {{ dag.start_date }}
      end_date                        : {{ dag.end_date }}
      full_filepath                   : {{ dag.full_filepath }}
      template_searchpath             : {{ dag.template_searchpath }}
      template_undefined              : {{ dag.template_undefined }}
      user_defined_macros             : {{ dag.user_defined_macros }}
      user_defined_filters            : {{ dag.user_defined_filters }}
      default_args                    : {{ dag.default_args }}
      concurrency                     : {{ dag.concurrency }}
      max_active_tasks                : {{ dag.max_active_tasks }}
      max_active_runs                 : {{ dag.max_active_runs }}
      dagrun_timeout                  : {{ dag.dagrun_timeout }}
      sla_miss_callback               : {{ dag.sla_miss_callback }}
      default_view                    : {{ dag.default_view }}
      orientation                     : {{ dag.orientation }}
      catchup                         : {{ dag.catchup }}
      on_success_callback             : {{ dag.on_success_callback }}
      on_failure_callback             : {{ dag.on_failure_callback }}
      doc_md                          : {{ dag.doc_md }}
      params                          : {{ dag.params }}
      access_control                  : {{ dag.access_control }}
      is_paused_upon_creation         : {{ dag.is_paused_upon_creation }}
      jinja_environment_kwargs        : {{ dag.jinja_environment_kwargs }}
      render_template_as_native_obj   : {{ dag.render_template_as_native_obj }}
      tags                            : {{ dag.tags }}
      owner_links                     : {{ dag.owner_links }}
      auto_register                   : {{ dag.auto_register }}
      fail_stop                       : {{ dag.fail_stop }}
  '''

  print_task(what_to_print)

dag_example_jinja_objects_dag()
```
{% endraw %}

</figure>

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

---

### DAG Run details
Or another example of printing the current and the previous DAG Run's details (note that you can use functions, even static or class level functions of instances replaced, class `DagRun`, specified in [airflow\models\dagrun.py][dagrun.py]):  

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_jinja_objects_dag_run.py</span> <span>Python</span></figcaption>

{% raw %}
```python
import pendulum
from airflow.decorators import dag, task

@task
def print_task(print_me):
    print(print_me)

@dag(
  start_date = pendulum.datetime(2021, 1, 1, tz="UTC"),
  schedule   = None,
  catchup    = False
)
def dag_example_jinja_objects_dag_run():
  """
    This DAG has only one task to demonstrate the
    capabilities of Jinja templating.
  """

  what_to_print = '''
    Current DAG Run details:
      id                        : {{ dag_run.id }}
      dag_id                    : {{ dag_run.dag_id }}
      queued_at                 : {{ dag_run.queued_at }}
      execution_date            : {{ dag_run.execution_date }}
      start_date                : {{ dag_run.start_date }}
      end_date                  : {{ dag_run.end_date }}
      _state                    : {{ dag_run._state }}
      run_id                    : {{ dag_run.run_id }}
      creating_job_id           : {{ dag_run.creating_job_id }}
      external_trigger          : {{ dag_run.external_trigger }}
      run_type                  : {{ dag_run.run_type }}
      conf                      : {{ dag_run.conf }}
      data_interval_start       : {{ dag_run.data_interval_start }}
      data_interval_end         : {{ dag_run.data_interval_end }}
      last_scheduling_decision  : {{ dag_run.last_scheduling_decision }}
      dag_hash                  : {{ dag_run.dag_hash }}
      log_template_id           : {{ dag_run.log_template_id }}
      updated_at                : {{ dag_run.updated_at }}

    Previous DAG Run details:
      id                        : {{ dag_run.get_previous_dagrun(dag_run).id }}
      dag_id                    : {{ dag_run.get_previous_dagrun(dag_run).dag_id }}
      queued_at                 : {{ dag_run.get_previous_dagrun(dag_run).queued_at }}
      execution_date            : {{ dag_run.get_previous_dagrun(dag_run).execution_date }}
      start_date                : {{ dag_run.get_previous_dagrun(dag_run).start_date }}
      end_date                  : {{ dag_run.get_previous_dagrun(dag_run).end_date }}
      _state                    : {{ dag_run.get_previous_dagrun(dag_run)._state }}
      run_id                    : {{ dag_run.get_previous_dagrun(dag_run).run_id }}
      creating_job_id           : {{ dag_run.get_previous_dagrun(dag_run).creating_job_id }}
      external_trigger          : {{ dag_run.get_previous_dagrun(dag_run).external_trigger }}
      run_type                  : {{ dag_run.get_previous_dagrun(dag_run).run_type }}
      conf                      : {{ dag_run.get_previous_dagrun(dag_run).conf }}
      data_interval_start       : {{ dag_run.get_previous_dagrun(dag_run).data_interval_start }}
      data_interval_end         : {{ dag_run.get_previous_dagrun(dag_run).data_interval_end }}
      last_scheduling_decision  : {{ dag_run.get_previous_dagrun(dag_run).last_scheduling_decision }}
      dag_hash                  : {{ dag_run.get_previous_dagrun(dag_run).dag_hash }}
      log_template_id           : {{ dag_run.get_previous_dagrun(dag_run).log_template_id }}
      updated_at                : {{ dag_run.get_previous_dagrun(dag_run).updated_at }}

  '''

  print_task(what_to_print)

dag_example_jinja_objects_dag_run()
```
{% endraw %}

</figure>

The example above assumes a previous run exists. On the first run, `get_previous_dagrun()` returns `None`, so guard attribute access. For example:

{% raw %}
```jinja
{% set previous_run = dag_run.get_previous_dagrun(dag_run) %}
{% if previous_run is not none %}
Previous run ID: {{ previous_run.run_id }}
{% else %}
No previous run.
{% endif %}
```
{% endraw %}

Apply this guard around the previous-run section when using the DAG run example above. The output shown here is from a later run:
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

---

### Task instances' details
Another example to print all the task instances' details of the current DAG Run (note that you can use *Jinja control elements*, like loops in the templates, class `TaskInstance` is specified in [airflow\models\taskinstance.py][taskinstance.py]):  

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_jinja_objects_ti.py</span> <span>Python</span></figcaption>

{% raw %}
```python
import pendulum
from airflow.decorators import dag, task

@task
def print_task(print_me):
    print(print_me)

@dag(
  start_date = pendulum.datetime(2021, 1, 1, tz="UTC"),
  schedule   = None,
  catchup    = False
)
def dag_example_jinja_objects_ti():
  """
    This DAG has only one task to demonstrate the
    capabilities of Jinja templating.
  """

  what_to_print = '''
    All task instances' details of the current DAG Run:
      {% for tInstances in dag_run.get_task_instances() %}
        task_id                     : {{ tInstances.task_id }}
        dag_id                      : {{ tInstances.dag_id }}
        run_id                      : {{ tInstances.run_id }}
        map_index                   : {{ tInstances.map_index }}
        start_date                  : {{ tInstances.start_date }}
        end_date                    : {{ tInstances.end_date }}
        duration                    : {{ tInstances.duration }}
        state                       : {{ tInstances.state }}
        _try_number                 : {{ tInstances._try_number }}
        max_tries                   : {{ tInstances.max_tries }}
        hostname                    : {{ tInstances.hostname }}
        unixname                    : {{ tInstances.unixname }}
        job_id                      : {{ tInstances.job_id }}
        pool                        : {{ tInstances.pool }}
        pool_slots                  : {{ tInstances.pool_slots }}
        queue                       : {{ tInstances.queue }}
        priority_weight             : {{ tInstances.priority_weight }}
        operator                    : {{ tInstances.operator }}
        custom_operator_name        : {{ tInstances.custom_operator_name }}
        queued_dttm                 : {{ tInstances.queued_dttm }}
        queued_by_job_id            : {{ tInstances.queued_by_job_id }}
        pid                         : {{ tInstances.pid }}
        executor_config             : {{ tInstances.executor_config }}
        updated_at                  : {{ tInstances.updated_at }}
        external_executor_id        : {{ tInstances.external_executor_id }}
        trigger_id                  : {{ tInstances.trigger_id }}
        trigger_timeout             : {{ tInstances.trigger_timeout }}
        next_method                 : {{ tInstances.next_method }}
        next_kwargs                 : {{ tInstances.next_kwargs }}
      {% endfor %}
  '''

  print_task(what_to_print)

dag_example_jinja_objects_ti()
```
{% endraw %}

</figure>

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

---

### Task instances' details through class `BaseOperator`
This example uses the task’s `BaseOperator` object to print its operator configuration, rather than the per-run state held by `TaskInstance` (class `BaseOperator` is specified in [airflow\models\baseoperator.py][baseoperator.py]):

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_jinja_objects_base_operator.py</span> <span>Python</span></figcaption>

{% raw %}
```python
import pendulum
from airflow.decorators import dag, task

@task
def print_task(print_me):
    print(print_me)

@dag(
  start_date = pendulum.datetime(2021, 1, 1, tz="UTC"),
  schedule   = None,
  catchup    = False
)
def dag_example_jinja_objects_base_operator():
  """
    This DAG has only one task to demonstrate the
    capabilities of Jinja templating.
  """

  what_to_print = '''
    Current task instance's details for the current DAG Run:
      task_id                               : {{ task.task_id }}  -  (a unique, meaningful id for the task)
      owner                                 : {{ task.owner }}  -  (the owner of the task. Using a meaningful description)
      email                                 : {{ task.email }}  -  (the 'to' email address(es) used in email alerts. This can be a)
      email_on_retry                        : {{ task.email_on_retry }}  -  (Indicates whether email alerts should be sent when a)
      email_on_failure                      : {{ task.email_on_failure }}  -  (Indicates whether email alerts should be sent when)
      retries                               : {{ task.retries }}  -  (the number of retries that should be performed before)
      retry_delay                           : {{ task.retry_delay }}  -  (delay between retries, can be set as ``timedelta`` or)
      retry_exponential_backoff             : {{ task.retry_exponential_backoff }}  -  (allow progressively longer waits between)
      max_retry_delay                       : {{ task.max_retry_delay }}  -  (maximum delay interval between retries, can be set as)
      start_date                            : {{ task.start_date }}  -  (The ``start_date`` for the task, determines)
      end_date                              : {{ task.end_date }}  -  (if specified, the scheduler won't go beyond this date)
      depends_on_past                       : {{ task.depends_on_past }}  -  (when set to true, task instances will run)
      wait_for_past_depends_before_skipping : {{ task.wait_for_past_depends_before_skipping }}  -  (when set to true, if the task instance)
      wait_for_downstream                   : {{ task.wait_for_downstream }}  -  (when set to true, an instance of task)
      dag                                   : {{ task.dag }}  -  (a reference to the dag the task is attached to (if any))
      priority_weight                       : {{ task.priority_weight }}  -  (priority weight of this task against other task.)
      weight_rule                           : {{ task.weight_rule }}  -  (weighting method used for the effective total)
      queue                                 : {{ task.queue }}  -  (which queue to target when running this job. Not)
      pool                                  : {{ task.pool }}  -  (the slot pool this task should run in, slot pools are a)
      pool_slots                            : {{ task.pool_slots }}  -  (the number of pool slots this task should use (>= 1))
      sla                                   : {{ task.sla }}  -  (time by which the job is expected to succeed. Note that)
      execution_timeout                     : {{ task.execution_timeout }}  -  (max time allowed for the execution of)
      on_failure_callback                   : {{ task.on_failure_callback }}  -  (a function or list of functions to be called when a task instance)
      on_execute_callback                   : {{ task.on_execute_callback }}  -  (much like the ``on_failure_callback`` except)
      on_retry_callback                     : {{ task.on_retry_callback }}  -  (much like the ``on_failure_callback`` except)
      on_success_callback                   : {{ task.on_success_callback }}  -  (much like the ``on_failure_callback`` except)
      pre_execute                           : {{ task.pre_execute }}  -  (a function to be called immediately before task)
      post_execute                          : {{ task.post_execute }}  -  (a function to be called immediately after task)
      trigger_rule                          : {{ task.trigger_rule }}  -  (defines the rule by which dependencies are applied)
      resources                             : {{ task.resources }}  -  (A map of resource parameter names (the argument names of the)
      run_as_user                           : {{ task.run_as_user }}  -  (unix username to impersonate while running the task)
      max_active_tis_per_dag                : {{ task.max_active_tis_per_dag }}  -  (When set, a task will be able to limit the concurrent)
      max_active_tis_per_dagrun             : {{ task.max_active_tis_per_dagrun }}  -  (When set, a task will be able to limit the concurrent)
      executor_config                       : {{ task.executor_config }}  -  (Additional task-level configuration parameters that are)
      do_xcom_push                          : {{ task.do_xcom_push }}  -  (if True, an XCom is pushed containing the Operator's)
      multiple_outputs                      : {{ task.multiple_outputs }}  -  (if True and do_xcom_push is True, pushes multiple XComs, one for each)
      task_group                            : {{ task.task_group }}  -  (The TaskGroup to which the task should belong. This is typically provided when not)
      doc                                   : {{ task.doc }}  -  (Add documentation or notes to your Task objects that is visible in)
      doc_md                                : {{ task.doc_md }}  -  (Add documentation (in Markdown format) or notes to your Task objects)
      doc_rst                               : {{ task.doc_rst }}  -  (Add documentation (in RST format) or notes to your Task objects)
      doc_json                              : {{ task.doc_json }}  -  (Add documentation (in JSON format) or notes to your Task objects)
      doc_yaml                              : {{ task.doc_yaml }}  -  (Add documentation (in YAML format) or notes to your Task objects)
  '''

  print_task(what_to_print)

dag_example_jinja_objects_base_operator()
```
{% endraw %}

</figure>

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
[templates_reference]: https://airflow.apache.org/docs/apache-airflow/2.8.4/templates-ref.html
[dag.py]: https://github.com/apache/airflow/blob/2.8.4/airflow/models/dag.py
[dagrun.py]: https://github.com/apache/airflow/blob/2.8.4/airflow/models/dagrun.py
[taskinstance.py]: https://github.com/apache/airflow/blob/2.8.4/airflow/models/taskinstance.py
[baseoperator.py]: https://github.com/apache/airflow/blob/2.8.4/airflow/models/baseoperator.py

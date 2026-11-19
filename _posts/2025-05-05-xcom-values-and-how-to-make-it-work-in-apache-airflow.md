---
title: "XCom values and how to make it work in Apache Airflow"
layout: post
date: 2025-05-05 00:00
image: /assets/images/001/xcom.jpg
illustration: /assets/images/articles/task-messages.svg
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
description: XCom is the standard way for tasks to communicate with each other though there are certain limitations.
excerpt_separator: <!--more-->
---
## XCom _(short for “cross-communications”)_

<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.10.4!
    </p>
</aside>

XComs let tasks exchange small serializable values. Tasks can pull values directly with `task_instance.xcom_pull()`, and TaskFlow supports passing task outputs as arguments. This article focuses on a narrower rule: automatic resolution of values passed to classic operator fields uses the operator’s `template_fields` attribute. That attribute is part of the operator authoring interface, not a private attribute. See the [XCom documentation][xcom_docs].

<!--more-->

## `template_fields` and automatic resolution

A TaskFlow output is represented by an `XComArg`. When passed directly to a templated operator field, it can be resolved to the stored value at runtime. It does not have to become a Jinja string. Converting a plain `XComArg` to a string produces a Jinja `xcom_pull` expression for compatibility; that is why unresolved objects printed by the example look like templates. See the [implementation][xcom_arg].

As I mentioned earlier in [this post][link_to_other_post], Jinja templating is a very powerful way of interacting with Airflow in runtime.

A field outside `template_fields` is not automatically resolved. An `XComArg` remains an object and an explicitly supplied template remains a string, unless the operator implements its own runtime handling.

The sample Dag `dag_example_xcom` below have 2 upstream tasks, which sets XCom values and 3 downstream tasks which pulls those values.  
The transfer of data also works from within a task group and data can be pulled by tasks in task groups.

{% include article-image.html src="/assets/images/001/xcom_tasks.jpg" alt="XCom tasks" %}

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_xcom.py</span> <span>Python</span></figcaption>

{% raw %}
~~~~python
from airflow.decorators import dag, task, task_group
from airflow.models.baseoperator import BaseOperator
from datetime import datetime
from typing import Sequence

class CustomOperator(BaseOperator):
  '''
    ----------------------------------  
    # Purpose of this class
    ```
    |-------------------------------------------------------------------|
    | To demonstrate functionalities of XCom on `template_fields` and   |
    | all others fields.                                                |
    |                                                                   |
    |       |\      _,,,---,,_                                          |
    | ZZZzz /,`.-'`'    -.  ;-;;,_                                      |
    |     |,4-  ) )-,_. ,\ (  `'-'                                      |
    |     '---''(_/--'  `-'\_)                                          |
    |-------------------------------------------------------------------|
    ```
    ----------------------------------  
  '''
  template_fields: Sequence[str] = { 'template0', 'template1', 'template2', 'template3', }

  def __init__(
    self,
    template0, template1, template2, template3,
    other0, other1, other2, other3,
    **kwargs
  ) -> None:
    super().__init__(**kwargs)
    self.template0 = template0
    self.template1 = template1
    self.template2 = template2
    self.template3 = template3
    self.other0 = other0
    self.other1 = other1
    self.other2 = other2
    self.other3 = other3

  def execute(self, context):
    print(f'''
      template0: { self.template0 }
      template1: { self.template1 }
      template2: { self.template2 }
      template3: { self.template3 }
      other0   : { self.other0 }
      other1   : { self.other1 }
      other2   : { self.other2 }
      other3   : { self.other3 }
    ''')

class AnotherCustomOperator(CustomOperator):
  '''
    ----------------------------------  
    # Purpose of this class
    ```
    |-------------------------------------------------------------------|
    | To demonstrate how easy this is to extend the list of fields in   |
    | `template_fields` and enable wider use of XCom values in others   |
    | fields.                                                           |
    |                                                                   |
    |       |\      _,,,---,,_                                          |
    | ZZZzz /,`.-'`'    -.  ;-;;,_                                      |
    |     |,4-  ) )-,_. ,\ (  `'-'                                      |
    |     '---''(_/--'  `-'\_)                                          |
    |-------------------------------------------------------------------|
    ```
    ----------------------------------  
  '''
  template_fields: Sequence[str] = { 'template0', 'template1', 'template2', 'template3', 'other0' }


@task(
  multiple_outputs = True
)
def xcom_source():
  '''
    ----------------------------------  
    # Purpose of this task
    ```
    |-------------------------------------------------------------------|
    | Generate an XCom value.                                           |
    | Because of the option `multiple_outputs = True` all keys in the   |
    | returned value can be accessed separately by other tasks through  |
    | XCom.                                                             |
    | Without this option the only value `return_value` could be        |
    | accessed.                                                         |
    |                                                                   |
    |       |\      _,,,---,,_                                          |
    | ZZZzz /,`.-'`'    -.  ;-;;,_                                      |
    |     |,4-  ) )-,_. ,\ (  `'-'                                      |
    |     '---''(_/--'  `-'\_)                                          |
    |-------------------------------------------------------------------|
    ```
    ----------------------------------  
  '''
  return {
    'output0': 'this is output0'
  }

@task_group
def wrapper_source():
  '''
    ----------------------------------  
    # Purpose of this task group
    ```
    |-------------------------------------------------------------------|
    | To include a task that sets XCom values.                          |
    |                                                                   |
    |       |\      _,,,---,,_                                          |
    | ZZZzz /,`.-'`'    -.  ;-;;,_                                      |
    |     |,4-  ) )-,_. ,\ (  `'-'                                      |
    |     '---''(_/--'  `-'\_)                                          |
    |-------------------------------------------------------------------|
    ```
    ----------------------------------  
  '''
  return xcom_source()

@task_group
def wrapper_target(
  input1,
  input2
):
  '''
    ----------------------------------  
    # Purpose of this task group
    ```
    |-------------------------------------------------------------------|
    | To include a task that reads XCom values.                         |
    | Inputs are the outputs (XCom) of other tasks using TaskFlow API.  |
    |                                                                   |
    |       |\      _,,,---,,_                                          |
    | ZZZzz /,`.-'`'    -.  ;-;;,_                                      |
    |     |,4-  ) )-,_. ,\ (  `'-'                                      |
    |     '---''(_/--'  `-'\_)                                          |
    |-------------------------------------------------------------------|
    ```
    ----------------------------------  
  '''
  CustomOperator(
    task_id    = 'xcom_target',
    # 
    template0  = input1,
    template1  = "{{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    other0     = input1,
    other1     = "{{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    # 
    template2  = input2,
    template3  = "{{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    other2     = input2,
    other3     = "{{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}"
  )

@dag(
  dag_id          = 'dag_example_xcom',
  start_date      = datetime(2024, 12, 2),
  schedule        = None,
  tags            = [ 'example' ]
)
def dag_example_xcom():
  '''
    # Purpose of this dag
    ```
    |-------------------------------------------------------------------|
    | This DAG has two source tasks and another two target tasks        |
    | to demonstrate how XCom values could be used to transfer data     |
    | among tasks.                                                      |
    |                                                                   |
    | The two target tasks reveals the internal behavior of XComs       |
    | if used with TaskFlow API and how those are being interpreted     |
    | internally by Airflow.                                            |
    |                                                                   |
    | With TaskFlow API only operators' `template_fields` can accept    |
    | XCom values directly.                                             |
    | Airflow first generates a template string for the Jinja engine    |
    | including a `task_instance.xcom_pull` funcion call to get the     |
    | XCom value.                                                       |
    | As this is a string typed field, without rendering it provides no |
    | XCom data, therefore only those fields can get the value which    |
    | are in the `template_fields` list of the operator (means those    |
    | are getting rendered by the Jinja engine).                        |
    |                                                                   |
    |       |\      _,,,---,,_                                          |
    | ZZZzz /,`.-'`'    -.  ;-;;,_                                      |
    |     |,4-  ) )-,_. ,\ (  `'-'                                      |
    |     '---''(_/--'  `-'\_)                                          |
    |-------------------------------------------------------------------|
    ```
  '''

  xcom_source_task = xcom_source()

  wrapper_source_task_group = wrapper_source()

  xcom_target_task = CustomOperator(
    task_id    = 'xcom_target',
    # 
    template0  = xcom_source_task['output0'],
    template1  = "{{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    other0     = xcom_source_task['output0'],
    other1     = "{{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    # 
    template2  = wrapper_source_task_group['output0'],
    template3  = "{{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    other2     = wrapper_source_task_group['output0'],
    other3     = "{{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}"
  )

  wrapper_target(
    input1 = xcom_source_task['output0'],
    input2 = wrapper_source_task_group['output0']
  )

  xcom_target_task = AnotherCustomOperator(
    task_id    = 'another_xcom_target',
    # 
    template0  = xcom_source_task['output0'],
    template1  = "{{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    other0     = xcom_source_task['output0'],
    other1     = "{{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    # 
    template2  = wrapper_source_task_group['output0'],
    template3  = "{{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}",
    other2     = wrapper_source_task_group['output0'],
    other3     = "{{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}"
  )

dag_example_xcom()
~~~~
{% endraw %}

</figure>

The output of `xcom_target` shows resolved values for templated fields. For the other fields, the f-string used to print the values makes an unresolved `XComArg` look like an explicitly supplied Jinja string:
{% raw %}
```
      template0: this is output0
      template1: this is output0
      template2: this is output0
      template3: this is output0
      other0   : {{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}
      other1   : {{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}
      other2   : {{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}
      other3   : {{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}
```
{% endraw %}

**NOTE:** `other0` receives an `XComArg`, while `other1` receives a string. Their printed representations match because printing invokes string conversion; their stored Python values are not the same type. The same distinction applies to `other2` and `other3`.
The source code for this task:

{% include article-image.html src="/assets/images/001/xcom_target_code.jpg" alt="Source code for target task" %}

---

To overcome this sort of limitation, for example if you have a built in operator which comes with Airflow, and you have a field which is not in the list of `template_fields`, but you would still need to have an XCom value there, well in this case you can create a custom class inherited from the actual operator and include the fields you need in the list.  
An example for this you can see in the code, using the class `AnotherCustomOperator`.  
Field `other0` is added to the list and therefore the value for this field also gets rendered and the XCom value can be used _(output is from task `another_xcom_target`)_:
{% raw %}
```
      template0: this is output0
      template1: this is output0
      template2: this is output0
      template3: this is output0
      other0   : this is output0 <<----------- This is the rendered value
      other1   : {{ task_instance.xcom_pull(task_ids='xcom_source', dag_id='dag_example_xcom', key='output0') }}
      other2   : {{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}
      other3   : {{ task_instance.xcom_pull(task_ids='wrapper_source.xcom_source', dag_id='dag_example_xcom', key='output0') }}
```
{% endraw %}

[link_to_other_post]: /jinja-templating-in-use-for-apache-airflow/

[xcom_docs]: https://airflow.apache.org/docs/apache-airflow/2.10.4/core-concepts/xcoms.html
[xcom_arg]: https://github.com/apache/airflow/blob/2.10.4/airflow/models/xcom_arg.py

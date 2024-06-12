---
title: "Going deep into Jinja Templating of Apache Airflow"
layout: post
date: 2024-04-14 00:00
image: /assets/images/001/gallery2.jpg
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

# What to render?
<br>

Each operator has to have the fields specified which Jinja Template Rendering should be applied onto.  
That is being specified in the specific class' attribute `template_fields`.  
Another option is to specify an extension of files where rendering needs to be in place for their content: `template_ext`.  
For some operators, file paths can be passed a value in `template_fields`. When the specified extension in `template_ext` is at the end of the value passed, then the file content will be rendered (not the file path itself).
<br>

Above behavious on file content rendering is being implemented in class `Templater` as below (specified in [airflow\template\templater.py][templater.py]):
```python
if isinstance(value, str):
    if value.endswith(tuple(self.template_ext)):  # A filepath.
        template = jinja_env.get_template(value)
    else:
        template = jinja_env.from_string(value)
    return self._render(template, context)
```

That means only those fields will be rendered which are listed here, or those files, where applicable.  
Let's see some examples. For a decorated *Python operator* of **TaskFlow API** (class `_PythonDecoratedOperator`) the field `template_fields` is being set to `("templates_dict", "op_args", "op_kwargs")` (specified in [airflow\decorators\python.py][python.py]). That means all the values provided as arguments are being rendered.  

---

Another example for a **Bash Operator** (class `BashOperator`) is: `("bash_command", "env")` (specified in [airflow\operators\bash.py][bash.py]). So if a string is passed to the argument `bash_command` then it gets rendered.  For this operator the field `template_ext` is also being set to `(".sh", ".bash")`

---

How aboout a `BigQueryInsertJobOperator`? The fields rendered (specified in [airflow\providers\google\cloud\operators\bigquery.py][bigquery.py]):  
```python
template_fields: Sequence[str] = (
    "configuration",
    "job_id",
    "impersonation_chain",
    "project_id",
)
```
File content is being rendered for files with extensions:
```python
template_ext: Sequence[str] = (
    ".json",
    ".sql",
)
```
<br>
<br>

# Rendering nested fields
<br>

For common built-in collections rendeiring is implemented on each element separately as shown below (function `render_template()` in class `Templater`):
```python
# Fast path for common built-in collections.
if value.__class__ is tuple:
    return tuple(self.render_template(element, context, jinja_env, oids) for element in value)
elif isinstance(value, tuple):  # Special case for named tuples.
    return value.__class__(*(self.render_template(el, context, jinja_env, oids) for el in value))
elif isinstance(value, list):
    return [self.render_template(element, context, jinja_env, oids) for element in value]
elif isinstance(value, dict):
    return {k: self.render_template(v, context, jinja_env, oids) for k, v in value.items()}
elif isinstance(value, set):
    return {self.render_template(element, context, jinja_env, oids) for element in value}
```
<br>

More complex collection can also be rendered, where `template_fields` from each element of the wrapper collection is being rendered individually.  
<br>
<br>

# What is field `template_fields_renderers` used for?
<br>

You can see something like this being set in this field:
```python
    template_fields_renderers = {
      "configuration": "json",
      "configuration.query.query": "sql"
    }
```
<br>

That field is there to render Airflow UI HTML pages highlighting template fields as the languages specified.  
This functionality is processed in function `rendered_templates()` of class `Airflow` (specified in [airflow\www\views.py][views.py]).  
<br>

1. `pygments` provides HTML code for highlighting the content of template fields of Airflow, implemented in function `get_attr_renderer()` ([airflow\www\utils.py][utils.py])
```python
"""Return Dictionary containing different Pygments Lexers for Rendering & Highlighting."""
return {
    "bash": lambda x: render(x, lexers.BashLexer),
    "bash_command": lambda x: render(x, lexers.BashLexer),
    "doc": lambda x: render(x, lexers.TextLexer),
    "doc_json": lambda x: render(x, lexers.JsonLexer),
    "doc_md": wrapped_markdown,
    "doc_rst": lambda x: render(x, lexers.RstLexer),
    "doc_yaml": lambda x: render(x, lexers.YamlLexer),
    "hql": lambda x: render(x, lexers.SqlLexer),
    "html": lambda x: render(x, lexers.HtmlLexer),
    "jinja": lambda x: render(x, lexers.DjangoLexer),
    "json": lambda x: json_render(x, lexers.JsonLexer),
    "md": wrapped_markdown,
    "mysql": lambda x: render(x, lexers.MySqlLexer),
    "postgresql": lambda x: render(x, lexers.PostgresLexer),
    "powershell": lambda x: render(x, lexers.PowerShellLexer),
    "py": lambda x: render(x, lexers.PythonLexer, get_python_source),
    "python_callable": lambda x: render(x, lexers.PythonLexer, get_python_source),
    "rst": lambda x: render(x, lexers.RstLexer),
    "sql": lambda x: render(x, lexers.SqlLexer),
    "tsql": lambda x: render(x, lexers.TransactSqlLexer),
    "yaml": lambda x: render(x, lexers.YamlLexer),
}
```
<br>

2. The HTML code returned by `pygments` [Lexers][pygments] is being passed over to [Flask App builder][flask] function `render_template()` of class `flask_appbuilder.BaseView` to render HTML page [airflow\www\templates\airflow\ti_code.html][ti_code.html] (which is actually another Jinja template itself!). HTML code of `pygments` is passed as `html_dict`.

{% raw %}
```go
{% extends "airflow/task_instance.html" %}
{% block title %}DAGs - {{ appbuilder.app_name }}{% endblock %}

{% block content %}
  {{ super() }}
  <h4>{{ title }}</h4>
  {% for k, v in html_dict.items() %}
    <h5>{{ k }}</h5>
    {{ v }}
  {% endfor %}
{% endblock %}
```
{% endraw %}
<br>

So on the UI in the above example, you will see values of field `configuration` highlighted as json, while values for `configuration.query.query` are being highlighted as SQL.
<br>

<br>
<br>

[jinja_docs]: https://jinja.palletsprojects.com/en/3.1.x/
[templater.py]: https://github.com/apache/airflow/blob/main/airflow/template/templater.py
[python.py]: https://github.com/apache/airflow/blob/main/airflow/decorators/python.py
[bash.py]: https://github.com/apache/airflow/blob/main/airflow/operators/bash.py
[bigquery.py]: https://github.com/apache/airflow/blob/main/airflow/providers/google/cloud/operators/bigquery.py
[views.py]: https://github.com/apache/airflow/blob/main/airflow/www/views.py
[utils.py]: https://github.com/apache/airflow/blob/main/airflow/www/utils.py
[pygments]: https://pygments.org/
[flask]: https://flask.palletsprojects.com/
[ti_code.html]: https://github.com/apache/airflow/blob/main/airflow/www/templates/airflow/ti_code.html

---
title: "DataStax Studio"
layout: post
date: 2024-10-31 00:00
image: /assets/images/001/robot.jpg
headerImage: true
tag:
- data management
- database
- nosql
- astradb
- datastax
- cassandra
- apache
category: blog
author: gabor
description: DataStax Studio, the best developer tool to visualize, profile, and manipulate data stored in DataStax databases.
excerpt_separator: <!--more-->
---
# DataStax Studio

In my [other post][link_to_other_post] I shared some techniques how to manage data in e.g. Datastax AstraDB.  
The best developer tool to visualize, profile, and manipulate data stored in DataStax databases, however is DataStax Studio.  
> Designed to facilitate Cassandra Query Language (CQL), Graph/Gremlin, and 
> Spark SQL language development, DataStax Studio has all the tools needed 
> for ad hoc queries,  visualizing and exploring data sets, profiling performance 
> and comes with a notebook interface that fuels collaboration.
<br>

<!--more-->
<br>
<br>

# Sample code

#### This is a simple Dockerfile to prepare an environment for DataStax Studio.
<script src="https://gist.github.com/f-f-9-9-0-0/77df05c6a05ab185e35af6386051036e.js"></script>
<br>

Once in use, **remove the suffix** and keep the file name as `Dockerfile` only.
<br>

`DataStax Studio` gets installed with all its dependencies on the image's OS.
<br>

:warning: **NOTE:** Take care of the future version changes over time, both OS and application level.
<br>

---
<br>

Build the image using the bellow command, from the same folder where the `Dockerfile` is located (*PowerShell*)  
```bash
docker build -t test/dsstudio .
```

Once completed, you can start the container on top of the image in detached mode, with the local folder attached as a volume (*PowerShell*)  
```bash
docker run -d -p :9091 -v "$(pwd):/work_dir" --name dsstudio test/dsstudio
```
<br>

You would need a `secure connect bundle` to be able to connect to e.g. AstraDB from the Studio, so keep that in the folder which you attached to the container.  
Then you can specify the **full PATH** in a DataStax Studio connection as `/work_dir/secure-connect.zip`
<br>

If started you get the URL printed on the console where DataStax Studio is available.  
Copy that link and paste into the browser (or you can click directly on Docker Desktop's link next to the container)
<br>

[link_to_other_post]: /how-to-manage-data-in-datastax-astradb-effectively

---
title: "DataStax Studio"
layout: post
date: 2024-10-31 00:00
image: /assets/images/001/robot.jpg
illustration: /assets/images/articles/database-workbench.svg
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
## DataStax Studio

In my [other post][link_to_other_post] I shared some techniques how to manage data in e.g. DataStax AstraDB.  
The best developer tool to visualize, profile, and manipulate data stored in DataStax databases, however is DataStax Studio.  
> Designed to facilitate Cassandra Query Language (CQL), Graph/Gremlin, and 
> Spark SQL language development, DataStax Studio has all the tools needed 
> for ad hoc queries,  visualizing and exploring data sets, profiling performance 
> and comes with a notebook interface that fuels collaboration.

<!--more-->

## Sample code

This is a simple Dockerfile to prepare an environment for DataStax Studio.

<figure class="code-example" markdown="1">
<figcaption><span class="code-file">Dockerfile</span> <span>Docker</span></figcaption>

```dockerfile
ARG  CODE_VERSION=latest
FROM alpine:${CODE_VERSION}

ENV  WORKDIR=/app
WORKDIR ${WORKDIR}

LABEL version="1.0"
LABEL description="DataStax Studio"

RUN apk add --upgrade apk-tools && \
apk upgrade --available && \
# Need Bash as that is being used in the
# Datastax Studio scripts
apk add --no-cache bash && \
apk add --no-cache openjdk8-jre && \
wget https://downloads.datastax.com/datastax-studio/datastax-studio-6.8.tar.gz && \
tar -xvzf datastax-studio-6.8.tar.gz && \
rm datastax-studio-6.8.tar.gz && \
# This is required if you run this from
# your local computer on top of Docker
# Desktop
sed -i -e 's/httpBindAddress: localhost/httpBindAddress: 0.0.0.0/' ./datastax-studio-6.8.*/conf/configuration.yaml

ENTRYPOINT ./datastax-studio-6.8.*/bin/server.sh
```

</figure>

`DataStax Studio` gets installed with all its dependencies on the image's OS.

<aside class="callout" aria-label="Note">
    <p>
        <strong class="callout-title">Note</strong>
        Take care of the future version changes over time, both OS and application level.
    </p>
</aside>

---

Build the image using the below command, from the same folder where the `Dockerfile` is located (*PowerShell*)  
```bash
docker build -t test/dsstudio .
```

Once completed, you can start the container on top of the image in detached mode, with the local folder attached as a volume (*PowerShell*)  
```bash
docker run -d -p :9091 -v "$(pwd):/work_dir" --name dsstudio test/dsstudio
```

You would need a `secure connect bundle` to be able to connect to e.g. AstraDB from the Studio, so keep that in the folder which you attached to the container.  
Then you can specify the **full PATH** in a DataStax Studio connection as `/work_dir/secure-connect.zip`

Detached mode prints the container ID, not the application’s startup output. Inspect the logs and the assigned host port with:

```bash
docker logs dsstudio
docker port dsstudio 9091
```

Because `-p :9091` assigns an available host port, use the reported port to open `http://localhost:<HOST_PORT>` when Docker runs locally. The application logs show startup details but may show the container’s internal port. See the [Docker run reference][docker_run].

[link_to_other_post]: /how-to-manage-data-in-datastax-astradb-effectively/

[docker_run]: https://docs.docker.com/reference/cli/docker/container/run/

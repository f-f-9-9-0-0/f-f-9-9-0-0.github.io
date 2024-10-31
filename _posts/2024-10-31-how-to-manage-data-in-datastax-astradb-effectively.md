---
title: "How to manage data in DataStax AstraDB effectively"
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
description: There are couple of tools built for facilitating data management in the Apache Cassandra based AstraDB.
excerpt_separator: <!--more-->
---
# Apache Cassandra

> [Apache Cassandra][cassandra] is a free and open-source, distributed, wide-column store, NoSQL, database management system intended to handle large amounts of data across multiple commodity servers, providing availability with no single point of failure. - [wikipedia][wiki_cassandra]
<br>

It all started with Avinash Lakshman and Prashant Malik once they were building the blue book of many faces. And you are right, the similarities between Cassandra and Amazon's DynamoDB is not something comes without a reason. As Lakshman also worked on that project before started at Facebook.  
So az usual (?) Cassandra got open-sourced and became a top-level project at Apache. And this is how Matthieu Riou, one of the Cassandra Committee members, celebrated it on [18th February 2010][top_level]:  
> Good news! Yesterday (for those who aren't on private), the board
> approved the resolution to adopt Cassandra as a top level project,
> you've graduated!
<br>

<!--more-->
So what is Cassandra good for? It can handle really huge volume of data. Also it is lightning fast if it comes to writing and reading data.  
Sounds great, but wait.. is this magic? No, it is not. So there are limitations.  
As this post is not about to go into the details of how Cassandra works, let me shorten this into a couple of examples, where Cassandra is struggling. Updates and deletes are not tolerated, or at least affects performance. Another similar kind of a data engineer use case is to get that data out, I mean all of it! Yeah, this is not something you should do with Cassandra, though if you want one single record out of the billion only, then.. yes you rockin' it.
<br>
<br>

# AstraDB, another level?

Okay, but What does AstraDB add to Cassandra then? Straight from Santa Clara, California, DataStax came to the rescue, namely Jonathan Ellis and Matt Pfeil.  
This is how Pfeil commented on their early days in 2018:  
> Q: Did you ever get worried about the Cassandra project being viable?  
> A: Definitely. During the 2009 to 2011 timeframe it felt like a new NoSQL project was  
> launching weekly. It's sort of like how Crypto is today.  
> ...  
> Q: What advice would you give to someone working on an early stage  
> technology with breakout potential  
> A: Get users. Do whatever you can to make them successful in production  
> and get them talking about it to the world. Repeat.  
<br>

AstraDB is a cloud [database-as-a-service][daas] based on Apache Cassandra. You get rid of the administration overhead and managing the software, which is usual for any such solution and also you can get professional support.  
Okay, so our expectation is that everything works which is there in Cassandra and even more functionalities included into the cloud based product, which is not open-sourced of course.  
<br>
<br>

# How to manage your data?

There are many ways to manage data in an AstraDB database, starting from the AstraDB web console, using another one, DataStax Studio or go with APIs.  
<br>

And there are tools ready for use which can help you to achieve your goals when it comes to reading and writing records of your tables.  
<br>

## CQLSH Standalone Tool

`cqlsh` is a command-line interface for interacting with Cassandra using CQL (the Cassandra Query Language). It is shipped with every Cassandra package, and can be found in the `bin/` directory alongside the `cassandra` executable.  
<br>

As you plan to go with a cloud database, you do not have the Cassandra package at hand. You need to download it separately.  
<br>

## DataStax Bulk Loader

The DataStax Bulk Loader tool (DSBulk) is a unified tool for loading into and unloading from Cassandra-compatible storage engines, such as Apache Cassandra, DataStax AstraDB and DataStax Enterprise (DSE).  
Three subcommands, `load`, `unload`, and `count` are straightforward. The subcommands require the options `keyspace` and `table`, or a `schema.query`. The load and unload commands also require a designated data source (`CSV` or `JSON`).  
<br>
<br>

# Sample code

#### This is a simple Dockerfile to prepare an environment to manage AstraDB data.
<script src="https://gist.github.com/f-f-9-9-0-0/f6634e9cc2cd9b987df9ad5952ce773a.js"></script>
<br>

Once in use, **remove the suffix** and keep the file name as `Dockerfile` only.
<br>

Tools `CQLSH standalone tool` and `DataStax Bulk Loader` get installed with all their dependencies on the image's OS.
<br>

:warning: **NOTE:** Take care of the future version changes over time, both OS and application level.
<br>

---
<br>

Build the image using the bellow command, from the same folder where the `Dockerfile` is located (*PowerShell*)  
```bash
docker build -t test/astradb_data_manager .
```

Once completed, you can start the container on top of the image in interactive mode, with the local folder attached as a volume (*PowerShell*)  
```bash
docker run -it -v "$(pwd):/work_dir" --name astradb_data_manager test/astradb_data_manager
```
<br>

If started you get the prompt from the container.
<br>

Set the below variables properly (*credentials to your AstraDB databases*):
```bash
client_id=***
client_secret=***
secure_connect_bundle=<PATH_TO_THE_SECURE_CONNECT_BUNDLE>
```

Now you can start using the tools installed.
<br>

### CQLSH Standalone Tool

Sample code to print current timestamp in format of `timeUUID`
```bash
cqlsh \
  -u $client_id \
  -p $client_secret \
  -b $secure_connect_bundle \
  --execute="select now() from system.local;"
```
<br>

### Datastax Bulk Loader

Sample code to get one record from a table in form of a `CSV`
```bash
dsbulk \
  unload \
  -u $client_id \
  -p $client_secret \
  -b $secure_connect_bundle \
  -url <PATH_OF_THE_OUTPUT_FOLDER> \
  -c csv \
  -query "select * from <KEYSPACE_NAME>.<TABLE_NAME> limit 1"
```
<br>
<br>

[cassandra]: https://cassandra.apache.org/
[wiki_cassandra]: https://en.wikipedia.org/wiki/Apache_Cassandra
[top_level]: https://www.mail-archive.com/cassandra-dev@incubator.apache.org/msg01518.html
[daas]: https://en.wikipedia.org/wiki/Cloud_database

---
title: "Keep documents' change history in Elasticsearch"
layout: post
date: 2024-10-07 00:00
image: /assets/images/001/gallery2.jpg
headerImage: true
tag:
- change history
- versioning
- indexing
- elasticsearch
- elk
- elastic
category: blog
author: gabor
description: There's no built-in support for this. Which means that you need to manage this by yourself.
excerpt_separator: <!--more-->
---
# Documents' change history
<br>

As expressed by David Pilato, one of Elastic's most experienced developer and evangelist, there's no built-in support for keeping documents' change history in an index of Elasticsearch.
<br>

It is interesting to see that there is nothing implemented for this common problem, which is a demanding need across the developers' community using Elasticsearch.  
Here are some questions where the community make their voice heard:
- [How to store document history (versioning, revisions)?][discuss1]
- [How to model a document’s state history?][discuss2]
- [Is it possible to store document versions in Elastic Search][discuss3]
<br>

<!--more-->
<br>
<br>

# `_version` metadata field in Elasticsearch

Every document in Elasticsearch has a version number. Every time a change is made to a document (including deleting it), the _version number is incremented.  
Elasticsearch uses this _version number to ensure that changes are applied in the correct order. If an older version of a document arrives after a new version, it can simply be ignored.  
<br>

`_version`: the source document’s version. The field is of the type long.
<br>

---
<br>

`_version` number can be used to ensure that conflicting changes made by applications do not result in data loss, as described in the [Elasticsearch Definitive Guide][guide]  
But that is not exactly what we want, so let's get through another solution described below..
<br>

# The solution

As I described in my previous post [Painless scripting in Elasticsearch][link_painless], we have Painless scripting which can come in handy now, and always.  
<br>

So what we need to do, step by step:
1. Store existing document values for the selected fields in a specific extra field, associated with the change history (e.g. `history` in the below example)
2. Set the technical fields providing details on the change (e.g. fields `change_timestamp`, `change_description` and `last_change_timestamp`)
3. Change the source documents' fields to the new values
4. Extend the change history of the document
<br>
<br>

# Sample code
<br>

#### A simple script to demonstrate how to keep change history of an Elasticsearch document inside the document itself
<script src="https://gist.github.com/f-f-9-9-0-0/e4e7fd4ab27e488a66386116aeb85790.js"></script>

[discuss1]: https://discuss.elastic.co/t/how-to-store-document-history-versioning-revisions/32651
[discuss2]: https://discuss.elastic.co/t/how-to-model-a-documents-state-history/144684
[discuss3]: https://discuss.elastic.co/t/is-it-possible-to-store-document-versions-in-elastic-search/337496
[guide]: https://github.com/elastic/elasticsearch-definitive-guide/blob/master/030_Data/40_Version_control.asciidoc
[link_painless]: /painless-scripting-in-elasticsearch

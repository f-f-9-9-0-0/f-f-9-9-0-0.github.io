---
title: "Keep documents' change history in Elasticsearch"
layout: post
date: 2024-10-07 00:00
image: /assets/images/001/robot.jpg
illustration: /assets/images/articles/document-history.svg
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
## Documents' change history

As expressed by [David Pilato][pilato], one of Elastic's most experienced developer and evangelist, there's no built-in support for keeping documents' change history in an index of Elasticsearch.

It is interesting to see that there is nothing implemented for this common problem, which is a demanding need across the developers' community using Elasticsearch.  
Here are some questions where the community make their voice heard:
- [How to store document history (versioning, revisions)?][discuss1]
- [How to model a document’s state history?][discuss2]
- [Is it possible to store document versions in Elastic Search][discuss3]

<!--more-->

## `_version` metadata field in Elasticsearch

In Elasticsearch 8.15, `_version` tracks a document’s internal version, but it does not retain previous document contents. Replication ordering uses sequence numbers assigned by the primary shard. To protect application read-modify-write operations, send the last observed `if_seq_no` and `if_primary_term`; conflicting writes are rejected rather than silently applied. External versioning is a separate, explicitly selected mechanism. See [optimistic concurrency control][concurrency] and [index versioning][versioning].

---

Concurrency control prevents certain conflicting writes; it is not a revision archive. The example below explicitly stores selected previous values inside the document.

## The solution

As I described in my previous post [Painless scripting in Elasticsearch][link_painless], we have Painless scripting which can come in handy now, and always.  

So what we need to do, step by step:
1. Store existing document values for the selected fields in a specific extra field, associated with the change history (e.g. `history` in the below example)
2. Set the technical fields providing details on the change (e.g. fields `change_timestamp`, `change_description` and `last_change_timestamp`)
3. Change the source documents' fields to the new values
4. Extend the change history of the document

## Sample code

### A simple script to demonstrate how to keep change history of an Elasticsearch document inside the document itself
{% include gist.html id="f-f-9-9-0-0/e4e7fd4ab27e488a66386116aeb85790" %}

### The output

The ouput shows exactly what we wanted to achieve, having the documents change history being kept within the field `history` of the document, consisting the technical fields which desribe the details on each change.  
```json
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [
      {
        "_index": "test_history_management",
        "_id": "93229420-028b-11ed-b440-0358b6de8001",
        "_score": 1,
        "_source": {
          "creation_timestamp": "2024-09-15T00:00:00.000000000",
          "last_change_timestamp": "2024-09-15T02:00:00.000000000",
          "field_excluded_from_in_history": "excluded_001",
          "another_excluded_field": "another_excluded_001",
          "field_included_in_history": "included_002",
          "another_included_field": "another_included_001",
          "history": [
            {
              "change_description": "keep history of field 'field_included_in_history' of the document",
              "field_included_in_history": "included_001",
              "old": {
                "field_included_in_history": "included_000"
              },
              "change_timestamp": "2024-09-15T01:00:00.000000000"
            },
            {
              "change_description": "keep history of both fields 'field_included_in_history' and 'another_included_field' of the document",
              "field_included_in_history": "included_002",
              "old": {
                "field_included_in_history": "included_001",
                "another_included_field": "another_included_000"
              },
              "change_timestamp": "2024-09-15T02:00:00.000000000",
              "another_included_field": "another_included_001"
            }
          ]
        }
      }
    ]
  }
}
```

[pilato]: https://david.pilato.fr/
[discuss1]: https://discuss.elastic.co/t/how-to-store-document-history-versioning-revisions/32651
[discuss2]: https://discuss.elastic.co/t/how-to-model-a-documents-state-history/144684
[discuss3]: https://discuss.elastic.co/t/is-it-possible-to-store-document-versions-in-elastic-search/337496
[concurrency]: https://www.elastic.co/guide/en/elasticsearch/reference/8.15/optimistic-concurrency-control.html
[versioning]: https://www.elastic.co/guide/en/elasticsearch/reference/8.15/docs-index_.html#versioning
[link_painless]: /painless-scripting-in-elasticsearch

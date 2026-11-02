---
title: "Painless scripting in Elasticsearch"
layout: post
date: 2024-09-09 00:00
image: /assets/images/001/engine.jpg
illustration: /assets/images/articles/search-transform.svg
headerImage: true
tag:
- painless
- scripting
- elasticsearch
- elk
- elastic
category: blog
author: gabor
description: Painless is a scripting language designed for security and performance
excerpt_separator: <!--more-->
---
## Painless

Painless is a scripting language designed for security and performance. Painless syntax is similar to Java syntax along with some additional features such as dynamic typing, Map and List accessor shortcuts, and array initializers.

Scripts are compiled directly into Java Virtual Machine (JVM) byte code and executed against a standard JVM.

<!--more-->

## A brief history of search engines

It all started with Vannevar Bush's essay back in 1945..
> 'Consider a future device …  in which an individual stores all his books, records, and communications, and which is mechanized so that it may be consulted with exceeding speed and flexibility. It is an enlarged intimate supplement to his memory.'

Then shortly after, the SMART (System for the Mechanical Analysis and Retrieval of Text) Information Retrieval System was the beginning of developing many important concepts in information retrieval at [Cornell University][cornell] in the 1960s.

Some big names worked on the project that time back, including Michael E. Lesk and the leader of the group working on the development, Gerard A. "Gerry" Salton.

---

And [here][lesk] is a short summary of himself by Lesk:
> In the 1960's I worked for the SMART project, wrote much of their retrieval code and did many of the retrieval experiments, as well as obtaining a PhD in Chemical Physics.  
> In the 1970's I worked in the group that built Unix and I wrote Unix tools for word processing (tbl, refer), compiling (lex), and networking (uucp).  
> ...

Quite impressive, huhh..

Salton's professional career and [legacy][salton] is also significant, but no surprise as he was one of the fifteen PhD students of Howard Hathaway Aiken, who was '*Truly a giant in early development of automatic computation*'.

---

But back to SMART, those important concepts were including:
- the vector space model,
- relevance feedback, and
- Rocchio classification

All these are being used ever since then..

## Elasticsearch

Elasticsearch is a search engine, a software program designed to help users find information stored on a specific database, based on the [Lucene library][lucene].  
In addition to this open source library Elasticsearch provides:
- distributed, multitenant-capable full-text search engine with an
- HTTP web interface and
- JSON documents with explicit or automatically inferred [field mappings][mapping]

Elasticsearch is developed in Java. And the main reason for this is because Apache Lucene, its high-performance, full-featured search engine library, is also written entirely in Java.  
Historically, several ports and related projects have targeted other languages. The following list includes legacy and discontinued projects and should not be read as a list of currently maintained alternatives:
- CLucene - Lucene implementation in C++
- Lucene.Net - Lucene implementation in .NET
- Lucene4c - Lucene implementation in C
- LuceneKit - Lucene implementation in Objective-C (Cocoa/GNUstep support)
- Lupy - Lucene implementation in Python (RETIRED)
- NLucene - another Lucene implementation in .NET (out of date)
- Zend Search - Lucene implementation in the Zend Framework for PHP 5
- Plucene - Lucene implementation in Perl
- KinoSearch - a new Lucene implementation in Perl
- PyLucene - a Python interface to Java Lucene, built with JCC and JNI (see the [project documentation][pylucene])
- MUTIS - Lucene implementation in Delphi
- Ferret - Lucene implementation in Ruby
- Montezuma - Lucene implementation in Common Lisp

## Painless, designed specifically for use with Elasticsearch

You can use Painless anywhere scripts are used in Elasticsearch.  
Painless is a simple, secure scripting language designed specifically for use with Elasticsearch.

Painless shipped with the [Elasticsearch 5.0 GA release][release_5] on October 26, 2016 (*at the time of writing we are at version 8.15.1*).
Jack Conradson put the code together, and reasons of '*Why build a brand new language when there are already so many to choose from?*' you can found [here][painless_jack].

---

And here we are, ever since then we can use Painless scripts anywhere in Elasticsearch where the is space for a script. For example in **runtime fields**, fields that are evaluated at query time.  
One important thing to note:
> When defining a Painless script to use with runtime fields, you must include **emit** to return calculated values.

There are two ways of defining a runtime field:  
1. Adding a runtime section under the mapping definition for exploring data without indexing fields.
2. Using runtime fields in a search request for creating a field that exists only as part of the query.

---

The full language specification can be found here: [Painless Language Specification][painless_spec]  

## Sample code

### Parsing a date field
{% include gist.html id="f-f-9-9-0-0/4f372cbce47b63a319eb87f08f42b8e0" %}

### Mapping a value to another
Multi-line script
{% include gist.html id="f-f-9-9-0-0/f62804cd61c6fd216e3cb69a9e702f97" %}

### Classification
Multi-line script
{% include gist.html id="f-f-9-9-0-0/56e81a16d0164900b78a8d217cd1ddf8" %}

[cornell]: https://cornell.edu/
[lesk]: https://www.lesk.com/mlesk/
[salton]: https://history.computer.org/pioneers/salton.html
[lucene]: https://lucene.apache.org/core/
[release_5]: https://www.elastic.co/blog/elasticsearch-5-0-0-released
[painless_jack]: https://www.elastic.co/blog/painless-a-new-scripting-language
[painless_spec]: https://www.elastic.co/guide/en/elasticsearch/painless/8.15/painless-lang-spec.html

[mapping]: https://www.elastic.co/guide/en/elasticsearch/reference/8.15/mapping.html
[pylucene]: https://lucene.apache.org/pylucene/

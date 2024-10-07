---
title: "The source or dot operator in Bash"
layout: post
date: 2024-06-12 00:00
image: /assets/images/001/circuit.jpg
headerImage: true
tag:
- bash
- shell
- linux
category: blog
author: gabor
description: Demistify the source or dot operator in Bash
excerpt_separator: <!--more-->
---
# Bash shell
<br>

Bash, short for Bourne-Again SHell, is a shell program and command language supported by the Free Software Foundation, first developed by Brian Fox.
<br>

Brian Fox began coding Bash on January 10, 1988 and released Bash as a beta, version .99, on June 8, 1989.
<br>
<!--more-->
<br>
<br>

# . (source or dot operator)
<br>

First of all, let's clarify what it means to execute a shell script file in Bash.  
If you type simply the script name (e.g. `script0.sh`) into Bash then it looks for the file in the `PATH` environment variable and if it is not there then it fails with `command not found`.  
If the script's path is there in the `PATH` environment variable then it can get executed. Same applies if you specify the full path to the script (e.g. `./script0.sh`, this case '.' represents the current directory, not the dot operator!)  
<br>

In both cases the script needs to be made executable (e.g. `chmod 744 script0.sh`)  
<br>

When a script gets executed like this then a subshell is created for its execution with separate variables which are removed after the script completes.  
<br>

---
<br>

This behavior is different it the script gets executed with the source or dot operator (e.g. `. script0.sh` or `source script0.sh`)  
<br>

This case the script does not need to be made executable.  
<br>

Also the script's content gets executed in the existing shell invoking it, which means all variables are shared and changes preserved after the script completes. The same as we would type each statement from the script into the console itself.  
<br>

`source` is a synonym for dot/period '.' in bash, but not in POSIX sh, so for maximum compatibility use the period.  
<br>

# Sample code
<br>

<script src="https://gist.github.com/f-f-9-9-0-0/362970e3c1f6b0afddd218eefe1f6c97.js"></script>

---
title: "The source or dot operator in Bash"
layout: post
date: 2024-06-12 00:00
image: /assets/images/001/circuit.jpg
illustration: /assets/images/articles/shell-environment.svg
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
## Bash shell

Bash, short for Bourne-Again SHell, is a shell program and command language supported by the Free Software Foundation, first developed by Brian Fox.

Brian Fox began coding Bash on January 10, 1988 and released Bash as a beta, version .99, on June 8, 1989.
<!--more-->

## . (source or dot operator)

First of all, let's clarify what it means to execute a shell script file in Bash.  
If you type simply the script name (e.g. `script0.sh`) into Bash then it looks for the file in the `PATH` environment variable and if it is not there then it fails with `command not found`.  
If the script's path is there in the `PATH` environment variable then it can get executed. Same applies if you specify a path to the script (e.g. `./script0.sh`, this case '.' represents the current directory, not the dot operator!)

In both cases the script needs to be made executable (e.g. `chmod 744 script0.sh`)  

When a script gets executed like this then a subshell is created for its execution with separate variables which are removed after the script completes.  

---

This behavior is different it the script gets executed with the source or dot operator (e.g. `. script0.sh` or `source script0.sh`)  

This case the script does not need to be made executable.  

Also the script's content gets executed in the existing shell invoking it, which means all variables are shared and changes preserved after the script completes. The same as we would type each statement from the script into the console itself.  

`source` is a synonym for dot/period '.' in bash, but not in POSIX sh, so for maximum compatibility use the period.  

## Sample code

To source the file from the current directory explicitly, use `. ./script0.sh`.

<aside class="callout" aria-label="Note">
    <p>
        <strong class="callout-title">Note</strong>
        Run the example with care. It creates a <code>bash_test</code> folder in the current directory, works inside it and deletes it at the end. Read it first, save it as a file and run it with <code>bash</code> from an empty directory, rather than pasting it into a terminal.
    </p>
</aside>


<figure class="code-example" markdown="1">
<figcaption><span class="code-file">the_source_or_dot_operator_in_bash.sh</span> <span>Bash</span></figcaption>

```bash
#!/bin/bash

# create a new folder for the tests,
# and stop if it already exists
mkdir bash_test && cd bash_test || exit 1

# create a new script with some content
# set the variable 'some_variable' in the script
echo "some_variable=0" >script0.sh
printf '%s\n' 'echo "$0"' >>script0.sh

# check the new folder is not in
# the PATH environment variable
echo $PATH

# try to execute the script
# you get an error as not found
# in the PATH:
#   command not found
script0.sh

# try to execute the script
# you get an error as the script
# is not executable (since path
# is specified not checked in PATH):
#   Permission denied
./script0.sh

# another try, but this time add
# the current folder to the PATH
export PATH=$PATH:$(pwd)
# check it is being added
echo $PATH
# execute the script, as found in
# the PATH,
# now you get the same error
#   Permission denied
script0.sh

# okay, remove the current folder
# from PATH
export PATH=${PATH%:/*}
# check again
echo $PATH

# add permission necessary to
# execute within a subshell
chmod 744 script0.sh
# check
ls -l script0.sh

# set variable empty
some_variable=
# check variable is not set
echo $some_variable
# execute the script, the variable
# is set in a subshell
./script0.sh
# check variable is still not
# set in the current shell
echo $some_variable

# remove permission added earlier
chmod 644 script0.sh
# check
ls -l script0.sh
# now execute with the
# source or dot operator
. script0.sh
# check variable again
# which is now being
# set in the current shell
echo $some_variable

# cleanup
some_variable=
cd ..
rm -R bash_test
```

</figure>

[![image.png](https://i.postimg.cc/zDsb0YJW/image.png)](https://postimg.cc/jChSS9nd)

![PyPI - Version](https://img.shields.io/pypi/v/todo-or-not)
[![Coverage Status](https://coveralls.io/repos/github/Start-Out/todo-or-not/badge.svg?branch=dev/staging&kill_cache=1)](https://coveralls.io/github/Start-Out/todo-or-not?branch=dev/staging&kill_cache=1)
![PyPI - Downloads](https://img.shields.io/pypi/dm/todo-or-not)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/todo-or-not)
![PyPI - License](https://img.shields.io/pypi/l/todo-or-not?color=purple)

## Overview

> TODO or not to do, that is the question

TODO Or Not (todoon) is, in essence, a simple tool that checks your project for TODO's and FIXME's. You can also
integrate this tool into your GitHub workflow via actions, and automate generating issues from the discovered TODO's and
FIXME's.

[Try it out! (see on PyPi)](https://pypi.org/project/todo-or-not/)

```bash
pip install --upgrade todo-or-not
todoignore-util -pc .gitignore 
todoignore-util -ut .git
todoon
```

## Example

Check out [this example code](blob/dev/staging/example.py) and
the [issues that it yielded](https://github.com/Start-Out/todo-or-not/issues?q=is%3Aissue+author%3Aapp%2Ftodo-or-not+label%3Aexample+)!

```py
###########################
# Example usage of # todoon
###########################

def an_unfinished_function():
    # TODO Finish documenting todo-or-not
    print("Hello, I'm not quite done, there's more to do!")
    print("Look at all these things I have to do!")
    a = 1 + 1
    b = a * 2
    print("Okay I'm done!")


def a_broken_function():
    # This line might not show up in the generated issue because it's too far away
    #  from the line that triggered the issue.
    # The search for pertinent lines will stop when it hits a line break or the
    #  maximum number of lines, set by PERTINENT_LINE_LIMIT
    a = [
        1, 1, 2, 3
    ]
    b = sum(a)
    c = b * len(a)
    return c / 0  # FIXME I just don't know why this doesn't work!
    # Notice that this line will be collected

    # But this one won't, because there's some whitespace between it and the trigger!


def a_skipping_example():
    # Since the line below has `# todoon` in it, the checker will give it a pass even though it has the magic words!
    print("Sometimes you really have to write TODO or FIXME, like this!")  # todoon


def a_very_pretty_example():
    # TODO Titled Issue! | In this format, you can define a title and a body! Also labels like #example or #enhancement
    print("Check this out!")

```

## Contributing

Please target `dev/contribute` with your fork, and please use the appropriate PR template! 

## Help

[See the wiki!](wiki)

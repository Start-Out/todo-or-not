##########################
# Example usage of # todoon
##########################

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


def a_closed_example():
    # TODO Closed Issues are helpful! | This issue is closed, but the TODO string is still in the codebase!
    print("This should be a red flag, because if the issue is still in the code then something isn't done yet")
    print("(Though it may simply be that the comment hasn't been removed)")


def another_closed_example():
    # TODO Closed Issues are STILL helpful! | This issue is also closed, but the TODO string is still in the codebase!
    print("Sometimes you need to do things twice.")

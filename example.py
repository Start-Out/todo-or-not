##########################
# Example usage of @todoon
##########################

def an_unfinished_function():
    # TODO Finish documenting todo-or-not
    print("Hello, I'm not quite done, there's more to do!")


def a_broken_function():
    return 42 / 0  # FIXME I don't know why this doesn't work!


def a_skipping_example():
    # Since the line below has @todoon in it, the checker will give it a pass even though it has the magic words!
    print("Sometimes you really have to write TODO or FIXME, like this!")  # #todoon

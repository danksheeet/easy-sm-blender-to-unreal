def is_descendant(child, parent):
    """Recursively checks if the child object is a descendant of the parent object."""
    p = child.parent
    while p:
        if p == parent: 
            return True
        p = p.parent
    return False

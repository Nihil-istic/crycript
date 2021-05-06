def kill(message: str, end: bool = True):
    """Print given message and then raise SystemExit.

    message: str -> message to print
    end: bool -> raise SystemExit if set to True"""
    # Print message
    print('\n', message, '\n', sep='')

    # Raise SystemExit (exit program)
    if end:
        raise SystemExit



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Splits up 'items' into size 'size' chunks.
INPUT: items - List of values.
       size - Chunk size we are splitting up 'items' into.
OUTPUT: Tuple of lists with given 'size'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def chunks(items: list, size: int) -> list:
    # validate_inputs([items, size], [list, int])
    size = max(1, size)
    return [items[i:i + size] for i in range(0, len(items), size)]

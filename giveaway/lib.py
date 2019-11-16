def starfilter(pred, it):
    for i in it:
        if pred(*i):
            yield i

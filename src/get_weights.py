def get_weights(vs):
    # :brief Get the weights for some set of update vectorsself.
    # :param vs [array<array<float>>] some update vectors
    # :return a [array<float>] a list of weights in the same order
    ls = []
    for v in vs:
        l = 0.0
        for e in v:
            l += e**2
        l = l**0.5
        ls.append(l)
    s = 0.0
    ret = []
    for l in ls:
        x = 1.0 / l
        s += x
        ret.append(x)
    for k in range(len(ls)):
        ret[k] /= s
    return ret

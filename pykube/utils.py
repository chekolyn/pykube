from six.moves import zip_longest
import posixpath


empty = object()


def obj_merge(a, b):
    c = {}
    for k, v in a.items():
        if k not in b:
            c[k] = v
        else:
            c[k] = obj_check(v, b[k])
    for k, v in b.items():
        if k not in a:
            c[k] = v
    return c


def obj_check(a, b):
    c = None
    if not isinstance(a, type(b)):
        c = a
    else:
        if isinstance(a, dict):
            c = obj_merge(a, b)
        elif isinstance(a, list):
            z = []
            for x, y in zip_longest(a, b, fillvalue=empty):
                if x is empty:
                    z.append(y)
                elif y is empty:
                    z.append(x)
                else:
                    z.append(obj_check(x, y))
            c = z
        else:
            c = a
    return c

def get_kwargs(self, **kwargs):
    """
    Creates a full URL to request based on arguments.

    :Parametes:
       - `kwargs`: All keyword arguments to build a kubernetes API endpoint
    """
    url = ""
    version = kwargs.pop("version", "v1")
    if version == "v1":
        base = kwargs.pop("base", "/api")
    elif "/" in version:
        base = kwargs.pop("base", "/apis")
    else:
        if "base" not in kwargs:
            raise TypeError("unknown API version; base kwarg must be specified.")
        base = kwargs.pop("base")
    bits = [base, version]
    # Overwrite (default) namespace from context if it was set
    if "namespace" in kwargs:
        n = kwargs.pop("namespace")
        if n is not None:
            if n:
                namespace = n
            else:
                namespace = self.config.namespace
            if namespace:
                bits.extend([
                    "namespaces",
                    namespace,
                ])
    url = kwargs.get("url", "")
    if url.startswith("/"):
        url = url[1:]
    bits.append(url)
    kwargs["url"] = self.url + posixpath.join(*bits)
    return kwargs

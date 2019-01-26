# 根据
_REGISTRY = {}


def get_provider(name):
    return _REGISTRY.get(name)


def _set_provider(name, provider):
    _original_provider = _REGISTRY.get(name, None)
    _REGISTRY[name] = provider


def _process_dependencies(obj):
    def process(obj, attr_name):
        for dependency in getattr(obj, attr_name, []):
            if dependency not in _REGISTRY:
                raise Exception("do not know dependency.")
            setattr(obj, dependency, get_provider(dependency))

    process(obj, "_dependencies")


def provider(name):
    """A class decorator used to register providers.

    When ``@provider()`` is used to decorate a class, members of that class
    will register themselves as providers for the named dependency. As an
    example, In the code fragment::

        @dependency.provider('foo_api')
        class Foo:
            def __init__(self):
                ...

            ...

        foo = Foo()

    The object ``foo`` will be registered as a provider for ``foo_api``. No
    more than one such instance should be created; additional instances will
    replace the previous ones, possibly resulting in different instances being
    used by different consumers.

    """
    def wrapper(cls):
        def wrapped(init):
            def __wrapped_init__(self, *args, **kwargs):
                init(self, *args, **kwargs)
                _set_provider(name, self)
            return __wrapped_init__
        cls.__init__ = wrapped(cls.__init__)
        return cls
    return wrapper


def requires(*dependecies):
    """A class decorator used to inject providers into consumers.

    The required providers will be made available to instances of the decorated
    class via an attribute with the same name as the provider. For example, in
    the code fragment::

        @dependency.requires('foo_api', 'bar_api')
        class FooBarClient:
            def __init__(self):
                ...

            ...

        client = FooBarClient()

    The object ``client`` will have attributes named ``foo_api`` and
    ``bar_api``, which are instances of the named providers.

    Objects must not rely on the existence of these attributes until after
    ``resolve_future_dependencies()`` has been called; they may not exist
    beforehand.

    Dependencies registered via ``@required()`` must have providers; if not,
    an ``UnresolvableDependencyException`` will be raised when
    ``resolve_future_dependencies()`` is called.

    """
    def wrapper(self, *args, **kwargs):
        self.__wrapped_init__(*args, **kwargs)
        _process_dependencies(self)

    def wrapped(cls):
        existing_dependencies = getattr(cls, "_dependencies", set())
        cls._dependencies = existing_dependencies.union(dependecies)
        if not hasattr(cls, '__wrapped_init__'):
            cls.__wrapped_init__ = cls.__init__
            cls.__init__ = wrapper
        return cls
    return wrapped

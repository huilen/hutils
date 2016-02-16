import threading
import logging
import re

from copy import copy
from contextlib import contextmanager
from collections import defaultdict


logger = logging.getLogger(__name__)

registry = None


class InjectException(Exception):
    pass


class Dependency(object):

    def __init__(self, dependency, name=None):
        self._dependency = dependency
        if not name:
            try:
                name = dependency.__name__
            except AttributeError:
                name = dependency.__class__.__name__
            name = self._camel_to_lower(name)
        self.name = name

    def get(self, target):
        return self._dependency

    def _camel_to_lower(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return name


class DynamicDependency(Dependency):

    def get(self, target):
        return self._dependency()


class LazyDependency(Dependency):

    def __init__(self, dependency, name=None,
                 perthread=False, pertarget=False):
        super(LazyDependency, self).__init__(dependency, name)
        self._perthread = perthread
        self._pertarget = pertarget

    def get(self, target):
        key = threading.current_thread().name if self._perthread else None
        obj = target if self._pertarget else self
        if not hasattr(obj, '_dependencies_'):
            obj._dependencies_ = defaultdict(
                lambda: defaultdict(dict))
        if not obj._dependencies_[key][self.name]:
            obj._dependencies_[key][self.name] = self._dependency()
        return obj._dependencies_[key][self.name]


class Registry(object):

    def __init__(self, *dependencies):
        self._registry = {}
        self.register(*dependencies)

    def install(self, merge=False):
        global registry
        if merge and registry:
            merged = registry._registry.copy()
            merged.update(self._registry)
            self._registry = merged
        registry = self
        logger.info("Registry installed")

    @staticmethod
    def current():
        return registry

    def get(self, dependency_name):
        try:
            return self._registry[dependency_name]
        except KeyError:
            raise InjectException(
                "Dependency not found in registry: {}", dependency_name)

    def register(self, *dependencies):
        for dependency in dependencies:
            self._registry[dependency.name] = dependency
            logger.info("{} registered".format(dependency.name))


def require(*dependency_names):

    def get_resolver(name):
        def get_dependency(target):
            logger.debug("Injecting {dep} on {cls}".format(
                dep=name, cls=target.__class__))
            try:
                if not registry:
                    raise InjectException("Registry not found")
                return registry.get(name).get(target)
            except InjectException as e:
                if hasattr(target, '__' + name):
                    logger.info("{dep} dependency was injected "
                                "manually on {cls}".format(
                                    dep=name, cls=target.__class__.__name__))
                    return getattr(target, '__' + name)
                else:
                    raise e

        def set_dependency(target, dependency):
            setattr(target, '__' + name, dependency)

        return property(get_dependency, set_dependency)

    def wrap_init(cls):
        orig_init = cls.__init__
        def init_wrapper(cls, *args, **kwargs):
            for name, dependency in kwargs.items():
                if name in dependency_names:
                    logger.info("{cls} manual injected through" \
                                "constructor {dep}".format(
                                    dep=name, cls=cls.__class__.__name__))
                    setattr(cls, name, dependency)
            orig_init(cls)
        setattr(cls, '__init__', init_wrapper)

    def build_cls(cls):
        for name in dependency_names:
            logger.info("{cls} requires {dep}".format(
                dep=name, cls=cls.__name__))
            setattr(cls, name, get_resolver(name))
        wrap_init(cls)
        return cls

    return build_cls

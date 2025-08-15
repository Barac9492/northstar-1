"""
Dependency Injection Container
Enterprise-grade IoC container for managing dependencies
"""
from typing import TypeVar, Type, Dict, Any, Callable, Optional
from abc import ABC, abstractmethod
import inspect
from functools import wraps

T = TypeVar('T')


class Container:
    """Lightweight dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._transients: Dict[str, Callable] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        key = self._get_key(interface)
        self._singletons[key] = implementation
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a transient service (new instance each time)"""
        key = self._get_key(interface)
        self._transients[key] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function"""
        key = self._get_key(interface)
        self._factories[key] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance"""
        key = self._get_key(interface)
        self._services[key] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service by its interface"""
        key = self._get_key(interface)
        
        # Check for registered instance
        if key in self._services:
            return self._services[key]
        
        # Check for singleton
        if key in self._singletons:
            if key not in self._services:
                self._services[key] = self._create_instance(self._singletons[key])
            return self._services[key]
        
        # Check for factory
        if key in self._factories:
            return self._factories[key]()
        
        # Check for transient
        if key in self._transients:
            return self._create_instance(self._transients[key])
        
        # Try to create instance directly
        return self._create_instance(interface)
    
    def _create_instance(self, cls: Type[T]) -> T:
        """Create an instance with dependency injection"""
        # Get constructor signature
        signature = inspect.signature(cls.__init__)
        parameters = signature.parameters
        
        # Skip 'self' parameter
        param_names = [name for name in parameters.keys() if name != 'self']
        
        # Resolve dependencies
        dependencies = {}
        for param_name in param_names:
            param = parameters[param_name]
            if param.annotation != inspect.Parameter.empty:
                dependencies[param_name] = self.resolve(param.annotation)
        
        return cls(**dependencies)
    
    def _get_key(self, interface: Type) -> str:
        """Get string key for interface"""
        return f"{interface.__module__}.{interface.__qualname__}"


# Global container instance
container = Container()


def inject(interface: Type[T]) -> T:
    """Decorator for dependency injection"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Inject dependency
            dependency = container.resolve(interface)
            return func(dependency, *args, **kwargs)
        return wrapper
    return decorator


class ServiceRegistry:
    """Service registry for automatic dependency discovery"""
    
    def __init__(self, container: Container):
        self.container = container
    
    def auto_register_services(self, module_paths: list) -> None:
        """Automatically register services from modules"""
        import importlib
        
        for module_path in module_paths:
            try:
                module = importlib.import_module(module_path)
                self._scan_module(module)
            except ImportError as e:
                print(f"Warning: Could not import {module_path}: {e}")
    
    def _scan_module(self, module) -> None:
        """Scan module for services to register"""
        for name in dir(module):
            obj = getattr(module, name)
            if (inspect.isclass(obj) and 
                hasattr(obj, '__annotations__') and 
                getattr(obj, '_service_type', None)):
                
                service_type = obj._service_type
                interface = obj._interface
                
                if service_type == 'singleton':
                    self.container.register_singleton(interface, obj)
                elif service_type == 'transient':
                    self.container.register_transient(interface, obj)


def service(interface: Type = None, lifetime: str = 'singleton'):
    """Decorator to mark classes as services"""
    def decorator(cls):
        cls._service_type = lifetime
        cls._interface = interface or cls
        return cls
    return decorator
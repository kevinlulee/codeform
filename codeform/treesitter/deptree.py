import functools
from typing import Callable, Dict, List, Set, Any

class DependencyTree:
    def __init__(self, library: Dict, getter: Callable):
        """
        Initialize the dependency tree with a library and a getter function.
        
        Args:
            library: Dictionary containing dependency information
            getter: Function to extract dependencies for a given key
        """
        self.getter = functools.cache(lambda key: getter(library.get(key)))
    
    def recursively_get_dependencies(self, target: str) -> Dict:
        """
        Generate a tree of dependencies for the given target.
        
        Args:
            target: The key to find dependencies for
            
        Returns:
            Dict representing the dependency tree
        """
        seen = set()
        
        def runner(key):
            seen.add(key)
            
            raw = self.getter(key)
            
            # Filter dependencies directly in this method
            dependencies = [] if not raw else [item for item in raw if item not in seen]
            
            children = [runner(dep) for dep in dependencies]
            payload = {"name": key}
            
            if children:
                payload["children"] = children
                
            return payload
        
        return runner(target)


def flatten(tree: Dict) -> List:
    """
    Flatten a dependency tree into a simple list of dependencies.
    
    Args:
        tree: Dependency tree
        
    Returns:
        Flat list of dependencies
    """
    def runner(node):
        name = node.get("name")
        children = node.get("children", [])
        
        # Directly flatten the nested results here
        result = [name]
        for child in children:
            result.extend(runner(child))
        return result
    
    return runner(tree)


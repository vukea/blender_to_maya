from abc import ABC, abstractmethod

class BaseNode(ABC):
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.node = None

    @abstractmethod
    def create(self):
        """Create the node in Maya"""
        pass

    @abstractmethod
    def connect(self, target_attr):
        """Connect this node to a target attribute"""
        pass

"""
Workflows package containing all AI workflows.
"""

from .srs_workflow import srs_graph
from .class_diagram_workflow import class_diagram_graph
from .usecase_diagram_workflow import usecase_diagram_graph
from .activity_diagram_workflow import activity_diagram_graph
from .wireframe_workflow import wireframe_graph

__all__ = ["srs_graph", "class_diagram_graph", "usecase_diagram_graph", "activity_diagram_graph", "wireframe_graph"]

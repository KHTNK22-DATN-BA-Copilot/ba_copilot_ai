"""
Workflows package containing all AI workflows.
"""

from .srs_workflow import srs_graph
from .class_diagram_workflow import class_diagram_graph
from .usecase_diagram_workflow import usecase_diagram_graph
from .activity_diagram_workflow import activity_diagram_graph
from .wireframe_workflow import wireframe_graph
from .stakeholder_register_workflow import stakeholder_register_graph
from .high_level_requirements_workflow import high_level_requirements_graph
from .requirements_management_plan_workflow import requirements_management_plan_graph
from .business_case_workflow import business_case_graph
from .scope_statement_workflow import scope_statement_graph
from .product_roadmap_workflow import product_roadmap_graph

__all__ = [
    "srs_graph",
    "class_diagram_graph",
    "usecase_diagram_graph",
    "activity_diagram_graph",
    "wireframe_graph",
    "stakeholder_register_graph",
    "high_level_requirements_graph",
    "requirements_management_plan_graph",
    "business_case_graph",
    "scope_statement_graph",
    "product_roadmap_graph"
]

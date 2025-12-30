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
from .feasibility_study_workflow import feasibility_study_graph
from .cost_benefit_analysis_workflow import cost_benefit_analysis_graph
from .risk_register_workflow import risk_register_graph
from .compliance_workflow import compliance_graph
from .hld_arch_workflow import hld_arch_graph
from .hld_cloud_workflow import hld_cloud_graph
from .hld_tech_workflow import hld_tech_graph
from .lld_arch_workflow import lld_arch_graph
from .lld_db_workflow import lld_db_graph
from .lld_api_workflow import lld_api_graph
from .lld_pseudo_workflow import lld_pseudo_graph
from .uiux_wireframe_workflow import uiux_wireframe_graph
from .uiux_mockup_workflow import uiux_mockup_graph
from .uiux_prototype_workflow import uiux_prototype_graph
from .rtm_workflow import rtm_graph
from .metadata_extraction_workflow import metadata_extraction_graph

__all__ = [
    "srs_graph",
    "class_diagram_graph",
    "usecase_diagram_graph",
    "activity_diagram_graph",
    "wireframe_graph",
    "stakeholder_register_graph",
    "high_level_requirements_graph",
    "requirements_management_plan_workflow",
    "business_case_graph",
    "scope_statement_graph",
    "product_roadmap_graph",
    "feasibility_study_graph",
    "cost_benefit_analysis_graph",
    "risk_register_graph",
    "compliance_graph",
    "hld_arch_graph",
    "hld_cloud_graph",
    "hld_tech_graph",
    "lld_arch_graph",
    "lld_db_graph",
    "lld_api_graph",
    "lld_pseudo_graph",
    "uiux_wireframe_graph",
    "uiux_mockup_graph",
    "uiux_prototype_graph",
    "rtm_graph",
    "metadata_extraction_graph"
]

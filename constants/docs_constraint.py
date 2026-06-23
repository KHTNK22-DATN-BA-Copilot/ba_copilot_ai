# Define the dependencies between various project documents.
DOCUMENT_DEPENDENCIES = {
    "stakeholder-register": {
        "required": [],
        "recommended": [],
    },
    "high-level-requirements": {
        "required": [],
        "recommended": ["stakeholder-register"],
    },
    "requirements-management-plan": {
        "required": [],
        "recommended": ["stakeholder-register", "high-level-requirements"],
    },
    "business-case": {
        "required": [],
        "recommended": ["stakeholder-register", "high-level-requirements"],
    },
    "scope-statement": {
        "required": ["business-case", "high-level-requirements"],
        "recommended": ["stakeholder-register"],
    },
    "product-roadmap": {
        "required": ["scope-statement", "high-level-requirements"],
        "recommended": ["business-case"],
    },
    "feasibility-study": {
        "required": ["business-case", "scope-statement", "high-level-requirements"],
        "recommended": ["product-roadmap"],
    },
    "cost-benefit-analysis": {
        "required": ["business-case", "feasibility-study", "scope-statement"],
        "recommended": ["product-roadmap"],
    },
    "risk-register": {
        "required": ["feasibility-study", "scope-statement"],
        "recommended": ["cost-benefit-analysis", "stakeholder-register"],
    },
    "compliance": {
        "required": ["scope-statement", "high-level-requirements"],
        "recommended": ["risk-register"],
    },
    "srs": {
        "required": ["high-level-requirements", "scope-statement", "feasibility-study"],
        "recommended": ["compliance", "stakeholder-register"],
    },
    "hld-arch": {
        "required": ["srs", "feasibility-study", "high-level-requirements"],
        "recommended": [],
    },
    "hld-cloud": {
        "required": ["hld-arch", "srs"],
        "recommended": ["cost-benefit-analysis"],
    },
    "hld-tech": {"required": ["hld-arch", "srs"], "recommended": ["feasibility-study"]},
    "lld-arch": {"required": ["hld-arch", "srs", "hld-tech"], "recommended": []},
    "lld-db": {"required": ["srs", "lld-arch"], "recommended": ["hld-tech"]},
    "lld-api": {"required": ["srs", "lld-arch", "lld-db"], "recommended": ["hld-tech"]},
    "lld-pseudo": {"required": ["srs"], "recommended": ["lld-api", "lld-db"]},
    "uiux-wireframe": {
        "required": ["srs", "high-level-requirements"],
        "recommended": ["stakeholder-register"],
    },
    "uiux-mockup": {"required": ["uiux-wireframe", "srs"], "recommended": []},
    "uiux-prototype": {
        "required": ["uiux-mockup", "uiux-wireframe"],
        "recommended": ["lld-api"],
    },
    "rtm": {
        "required": ["srs", "high-level-requirements"],
        "recommended": ["lld-arch", "lld-db", "lld-api", "uiux-wireframe"],
    },
}


def resolve_document_constraint(workflow_name: str) -> list[str]:
    """Return the document types that should be used as RAG filters for a workflow."""
    dependency = DOCUMENT_DEPENDENCIES.get(workflow_name, {})
    resolved: list[str] = []

    for document_type in dependency.get("required", []):
        if document_type not in resolved:
            resolved.append(document_type)

    for document_type in dependency.get("recommended", []):
        if document_type not in resolved:
            resolved.append(document_type)
    resolved.append("other")
    return resolved
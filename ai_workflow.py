# ai_service/ai_workflow.py
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from figma_mcp import generate_figma_wireframe, generate_figma_diagram
from models.srs import SRSOutput, SRSResponse
from models.wireframe import WireframeOutput, WireframeResponse
from models.diagram import DiagramOutput, DiagramResponse
import json
import os
from typing import TypedDict

# Load API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

class GraphState(TypedDict):
    user_message: str
    intent: str
    type: str
    response: dict

def extract_json(text: str) -> dict:
    """Extract JSON from text response"""
    try:
        # Find JSON block
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return {"intent": "unknown"}
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {"intent": "unknown"}

# 1️⃣ Node phân loại intent
def classify_intent(state: GraphState) -> GraphState:
    """Classify user intent into: srs, wireframe, or diagram"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.1
    )

    prompt = f"""
    Phân loại yêu cầu của người dùng thành một trong các loại sau:
    - "srs": Khi người dùng yêu cầu tạo tài liệu đặc tả yêu cầu phần mềm (Software Requirements Specification)
    - "wireframe": Khi người dùng yêu cầu tạo wireframe/giao diện UI/mockup
    - "diagram": Khi người dùng yêu cầu tạo sơ đồ (ERD, flowchart, architecture diagram, etc.)

    Yêu cầu: "{state['user_message']}"

    Chỉ trả về JSON với format: {{"intent": "<loại>"}}
    """

    res = model.invoke(prompt)
    intent_data = extract_json(res.content)
    intent = intent_data.get("intent", "srs")  # Default to srs

    return {"intent": intent, "user_message": state["user_message"]}

# 2️⃣ Node SRS - Generate Software Requirements Specification
def srs_node(state: GraphState) -> GraphState:
    """Generate SRS document using Gemini"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    prompt = f"""
    Bạn là một Business Analyst chuyên nghiệp. Hãy tạo tài liệu Software Requirements Specification (SRS)
    chi tiết cho yêu cầu sau: {state['user_message']}

    Trả về theo format JSON sau:
    {{
        "title": "Tên dự án/tính năng",
        "functional_requirements": "Mô tả các yêu cầu chức năng (các tính năng chính, use cases)",
        "non_functional_requirements": "Mô tả các yêu cầu phi chức năng (performance, security, scalability, etc.)",
        "detail": "Nội dung chi tiết đầy đủ của tài liệu SRS ở định dạng Markdown với các sections:
                   1. Introduction
                   2. Overall Description
                   3. Functional Requirements (chi tiết)
                   4. Non-Functional Requirements (chi tiết)
                   5. System Features
                   6. External Interface Requirements
                   7. Other Requirements"
    }}

    Chỉ trả về JSON, không thêm text nào khác.
    """

    result = model.invoke(prompt)

    # Extract and parse JSON response
    try:
        srs_data = extract_json(result.content)

        srs_response = SRSResponse(
            title=srs_data.get("title", "Software Requirements Specification"),
            functional_requirements=srs_data.get("functional_requirements", ""),
            non_functional_requirements=srs_data.get("non_functional_requirements", ""),
            detail=srs_data.get("detail", "")
        )

        output = SRSOutput(type="srs", response=srs_response)
        return {"type": "srs", "response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error parsing SRS response: {e}")
        # Fallback response
        return {
            "type": "srs",
            "response": {
                "title": "Software Requirements Specification",
                "functional_requirements": "Error generating requirements",
                "non_functional_requirements": "Error generating requirements",
                "detail": result.content
            }
        }

# 3️⃣ Node Wireframe - Generate Figma wireframe
def wireframe_node(state: GraphState) -> GraphState:
    """Generate wireframe using Figma MCP"""
    result = generate_figma_wireframe(state["user_message"])

    wireframe_response = WireframeResponse(**result)
    output = WireframeOutput(type="wireframe", response=wireframe_response)

    return {"type": "wireframe", "response": output.model_dump()["response"]}

# 4️⃣ Node Diagram - Generate Figma diagram
def diagram_node(state: GraphState) -> GraphState:
    """Generate diagram using Gemini + Figma MCP"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    prompt = f"""
    Tạo mô tả chi tiết cho sơ đồ (diagram) dựa trên yêu cầu: {state['user_message']}

    Mô tả nên bao gồm:
    - Loại sơ đồ (ERD, Flowchart, Architecture, etc.)
    - Các entities/components chính
    - Relationships/connections giữa các thành phần
    - Attributes/properties quan trọng

    Trả về mô tả chi tiết để có thể dùng để vẽ sơ đồ.
    """

    desc = model.invoke(prompt).content
    result = generate_figma_diagram(desc)

    diagram_response = DiagramResponse(**result)
    output = DiagramOutput(type="diagram", response=diagram_response)

    return {"type": "diagram", "response": output.model_dump()["response"]}

# 5️⃣ Routing function
def route_intent(state: GraphState) -> str:
    """Route to appropriate node based on intent"""
    intent = state.get("intent", "srs")

    if intent == "wireframe":
        return "wireframe_node"
    elif intent == "diagram":
        return "diagram_node"
    else:
        return "srs_node"

# 6️⃣ Build LangGraph pipeline
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("intent_classifier", classify_intent)
workflow.add_node("srs_node", srs_node)
workflow.add_node("wireframe_node", wireframe_node)
workflow.add_node("diagram_node", diagram_node)

# Set entry point
workflow.set_entry_point("intent_classifier")

# Add conditional edges from classifier
workflow.add_conditional_edges(
    "intent_classifier",
    route_intent,
    {
        "srs_node": "srs_node",
        "wireframe_node": "wireframe_node",
        "diagram_node": "diagram_node"
    }
)

# Add finish edges
workflow.add_edge("srs_node", END)
workflow.add_edge("wireframe_node", END)
workflow.add_edge("diagram_node", END)

# Compile graph
ai_graph = workflow.compile()

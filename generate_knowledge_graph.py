import os
import asyncio
import warnings
import webbrowser
from collections import Counter
from dotenv import load_dotenv
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pyvis.network import Network

warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

# 1. Setup specialized Bio-Transformer
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
nodes = ["Gene", "Protein", "Disease", "BiologicalProcess", "Complex"]
rels = ["PRODUCES", "INTERACTS_WITH", "ASSOCIATED_WITH", "INHIBITS", "CLEAVES"]

graph_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=nodes,
    allowed_relationships=rels,
    strict_mode=True,
    additional_instructions="""
    - Focus on molecular biology: extract genes and proteins as distinct nodes.
    - If a gene and its protein have the same name, create a Gene node and a Protein node.
    - Identify clinical associations like 'risk of disease' as 'ASSOCIATED_WITH' relationships.
    - Treat complexes (e.g., BRCA1-BARD1 complex) as a result of an INTERACTS_WITH relationship.
    """
    
)

async def extract_graph_data(text):
    documents = [Document(page_content=text)]
    return await graph_transformer.aconvert_to_graph_documents(documents)

def visualize_graph(graph_documents):
    net = Network(height="900px", width="100%", directed=True, bgcolor="#222222", font_color="white")
    
    color_map = {"Gene": "#3498db", "Protein": "#2ecc71", "Disease": "#e74c3c", "BiologicalProcess": "#9b59b6"}

    # Add Legend
    for i, (label, color) in enumerate(color_map.items()):
        net.add_node(f"legend_{label}", label=label, color=color, fixed=True, x=-1000, y=-500+(i*60), physics=False, shape="box")

    # Calculate Node Scaling
    relationships = graph_documents[0].relationships
    nodes = graph_documents[0].nodes
    edge_counts = Counter([r.source.id for r in relationships] + [r.target.id for r in relationships])

    # Add Data Nodes
    for node in nodes:
        net.add_node(node.id, label=node.id, size=20+(edge_counts[node.id]*10), color=color_map.get(node.type, "#95a5a6"), title=node.type)

    # Add Data Edges
    for rel in relationships:
        net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower(), color="#aaaaaa", width=2)

    net.set_options('{"physics": {"forceAtlas2Based": {"springLength": 200}, "solver": "forceAtlas2Based"}}')
    net.save_graph("bio_knowledge_graph.html")

import wikipediaapi
import networkx as nx

def get_prerequisites(concept):
    # This function returns prerequisite concepts (behind concepts) for the given concept
    wiki_wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': 'MyWikipediaBot/1.0'})
    page = wiki_wiki.page(concept)
    prerequisites = []
    
    if page.exists():
        intro_text = page.text[:500]  # Limit to the first 500 characters
        links = page.links.keys()
        
        # Filter prerequisite links found in the intro
        for link in links:
            if link in intro_text:
                prerequisites.append(link)
                
    return prerequisites

def get_advanced_topics(concept):
    # This function returns advanced topics (beyond concepts) for the given concept
    wiki_wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': 'MyWikipediaBot/1.0'})
    page = wiki_wiki.page(concept)
    advanced_topics = []

    if page.exists():
        for section in page.sections:
            if "Advanced" in section.title or "Applications" in section.title:
                for link in section.text.split():
                    if link in page.links.keys():
                        advanced_topics.append(link)

    return advanced_topics

def build_concept_graph(concept):
    G = nx.DiGraph()  # Directed graph to enforce the concept order

    # Add the initial concept
    G.add_node(concept)

    # Get prerequisites (behind concepts)
    prerequisites = get_prerequisites(concept)
    for prereq in prerequisites:
        G.add_edge(prereq, concept)  # Prerequisite -> Concept

    # Get advanced topics (beyond concepts)
    advanced_topics = get_advanced_topics(concept)
    for advanced in advanced_topics:
        G.add_edge(concept, advanced)  # Concept -> Advanced Topic

    return G

def generate_learning_path(concept):
    # Build the graph and get a topologically sorted learning path
    concept_graph = build_concept_graph(concept)
    
    try:
        # Perform topological sorting to ensure the right order
        path = list(nx.topological_sort(concept_graph))
        return path
    except nx.NetworkXUnfeasible:
        # This exception occurs if there are cycles in the graph (which shouldn't happen if data is correct)
        return "Error: Cyclic dependency detected. Unable to generate a learning path."

# Example usage
concept = "Machine Learning"
learning_path = generate_learning_path(concept)
print("Learning Path:", learning_path)


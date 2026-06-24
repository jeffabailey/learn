"""A tiny knowledge graph in pure Python.

A knowledge graph stores facts as triples: (subject, relationship, object).
This file builds one as a plain list of triples, then queries and traverses it
with a few small functions. No database, no libraries, no setup.

Run it:
    python knowledge_graph.py
"""

# A triple is one fact: who, how, what.
# ("Marie Curie", "won", "Nobel Prize in Physics") reads like a short sentence.

graph = [
    ("Marie Curie", "won", "Nobel Prize in Physics"),
    ("Marie Curie", "studied", "Radioactivity"),
    ("Marie Curie", "born in", "Poland"),
    ("Radioactivity", "is a", "Physics concept"),
    ("Pierre Curie", "won", "Nobel Prize in Physics"),
]


def add(graph, subject, relationship, obj):
    """Add one fact to the graph."""
    graph.append((subject, relationship, obj))


def facts_about(graph, subject):
    """Return every fact that starts at this subject."""
    return [triple for triple in graph if triple[0] == subject]


def follow(graph, subject, relationship):
    """Follow one relationship from a subject to the objects it points to."""
    return [obj for (s, r, obj) in graph if s == subject and r == relationship]


def who(graph, relationship, obj):
    """Find every subject connected to an object by a relationship."""
    return [s for (s, r, o) in graph if r == relationship and o == obj]


if __name__ == "__main__":
    # 1. What do we know about Marie Curie?
    print("Facts about Marie Curie:")
    for s, r, o in facts_about(graph, "Marie Curie"):
        print(f"  {s} {r} {o}")

    # 2. Traverse: Marie Curie -> studied -> Radioactivity -> is a -> ?
    print("\nTraversal:")
    for topic in follow(graph, "Marie Curie", "studied"):
        for field in follow(graph, topic, "is a"):
            print(f"  Marie Curie studied {topic}, which is a {field}.")

    # 3. Shared node: who else won the same prize?
    print("\nWho won the Nobel Prize in Physics:")
    for person in who(graph, "won", "Nobel Prize in Physics"):
        print(f"  {person}")

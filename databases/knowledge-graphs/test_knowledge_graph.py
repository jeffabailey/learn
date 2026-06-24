"""Unit tests for knowledge_graph.py.

Run them:
    python -m pytest test_knowledge_graph.py
"""

import pytest

from knowledge_graph import add, facts_about, follow, who


@pytest.fixture
def sample_graph():
    """A small graph rebuilt fresh for each test."""
    return [
        ("Marie Curie", "won", "Nobel Prize in Physics"),
        ("Marie Curie", "studied", "Radioactivity"),
        ("Marie Curie", "born in", "Poland"),
        ("Radioactivity", "is a", "Physics concept"),
        ("Pierre Curie", "won", "Nobel Prize in Physics"),
    ]


class TestAdd:
    def test_appends_one_triple(self, sample_graph):
        before = len(sample_graph)
        add(sample_graph, "Pierre Curie", "studied", "Radioactivity")
        assert len(sample_graph) == before + 1
        assert ("Pierre Curie", "studied", "Radioactivity") in sample_graph

    def test_mutates_in_place_and_returns_none(self, sample_graph):
        result = add(sample_graph, "Henri Becquerel", "won", "Nobel Prize in Physics")
        assert result is None
        assert sample_graph[-1] == ("Henri Becquerel", "won", "Nobel Prize in Physics")

    def test_allows_duplicate_facts(self, sample_graph):
        triple = ("Marie Curie", "born in", "Poland")
        add(sample_graph, *triple)
        assert sample_graph.count(triple) == 2

    def test_starts_from_empty_graph(self):
        graph = []
        add(graph, "A", "rel", "B")
        assert graph == [("A", "rel", "B")]


class TestFactsAbout:
    def test_returns_every_fact_for_subject(self, sample_graph):
        facts = facts_about(sample_graph, "Marie Curie")
        assert facts == [
            ("Marie Curie", "won", "Nobel Prize in Physics"),
            ("Marie Curie", "studied", "Radioactivity"),
            ("Marie Curie", "born in", "Poland"),
        ]

    def test_matches_only_the_subject_position(self, sample_graph):
        # "Radioactivity" appears as an object for Marie Curie, but only its
        # own subject facts should come back.
        facts = facts_about(sample_graph, "Radioactivity")
        assert facts == [("Radioactivity", "is a", "Physics concept")]

    def test_unknown_subject_returns_empty(self, sample_graph):
        assert facts_about(sample_graph, "Albert Einstein") == []

    def test_is_case_sensitive(self, sample_graph):
        assert facts_about(sample_graph, "marie curie") == []

    def test_empty_graph_returns_empty(self):
        assert facts_about([], "Marie Curie") == []


class TestFollow:
    def test_returns_objects_for_subject_and_relationship(self, sample_graph):
        assert follow(sample_graph, "Marie Curie", "studied") == ["Radioactivity"]

    def test_collects_multiple_objects(self, sample_graph):
        add(sample_graph, "Marie Curie", "studied", "Magnetism")
        assert follow(sample_graph, "Marie Curie", "studied") == [
            "Radioactivity",
            "Magnetism",
        ]

    def test_supports_chained_traversal(self, sample_graph):
        # Marie Curie -> studied -> Radioactivity -> is a -> Physics concept
        topics = follow(sample_graph, "Marie Curie", "studied")
        fields = [f for t in topics for f in follow(sample_graph, t, "is a")]
        assert fields == ["Physics concept"]

    def test_wrong_relationship_returns_empty(self, sample_graph):
        assert follow(sample_graph, "Marie Curie", "discovered") == []

    def test_unknown_subject_returns_empty(self, sample_graph):
        assert follow(sample_graph, "Nobody", "won") == []


class TestWho:
    def test_finds_every_subject_for_object(self, sample_graph):
        assert who(sample_graph, "won", "Nobel Prize in Physics") == [
            "Marie Curie",
            "Pierre Curie",
        ]

    def test_single_match(self, sample_graph):
        assert who(sample_graph, "born in", "Poland") == ["Marie Curie"]

    def test_relationship_must_also_match(self, sample_graph):
        # "Radioactivity" is an object via "studied", not "won".
        assert who(sample_graph, "won", "Radioactivity") == []

    def test_no_match_returns_empty(self, sample_graph):
        assert who(sample_graph, "won", "Nobel Prize in Chemistry") == []

    def test_reflects_newly_added_facts(self, sample_graph):
        add(sample_graph, "Henri Becquerel", "won", "Nobel Prize in Physics")
        assert who(sample_graph, "won", "Nobel Prize in Physics") == [
            "Marie Curie",
            "Pierre Curie",
            "Henri Becquerel",
        ]


class TestQueriesDoNotMutate:
    def test_read_functions_leave_graph_unchanged(self, sample_graph):
        snapshot = list(sample_graph)
        facts_about(sample_graph, "Marie Curie")
        follow(sample_graph, "Marie Curie", "studied")
        who(sample_graph, "won", "Nobel Prize in Physics")
        assert sample_graph == snapshot

# Software Ontology: a worked example

This folder is a companion to the blog post [How Do I Create a Software Ontology?](https://jeffbailey.us/blog/2026/05/28/how-do-i-create-a-software-ontology).

It is a complete, documented software ontology for one bounded context, **Subscription Billing**, built by following the seven steps in that post. The blog post explains *how* to build an ontology. This folder is the *artifact* a team would actually keep next to its code.

## What is in here

- [`ontology.md`](ontology.md): the ontology written for humans. Ubiquitous language glossary, concept classification, aggregates and their invariants, and two Mermaid diagrams (the aggregate relationship model and the context map).
- [`ontology.yaml`](ontology.yaml): the same ontology written for machines. A structured form you can load, validate, diff in pull requests, or feed into a graph store. This is what "make it queryable" (Step 7) looks like in practice.

Read `ontology.md` first. Open `ontology.yaml` when you want to see the queryable shape.

## What this ontology covers

Subscription Billing owns the recurring-payment slice of a SaaS business: turning a customer's chosen plan into a stream of invoices, collecting payment, and retrying when a charge fails. It deliberately does **not** own the product catalog or customer support; those are neighboring contexts, mapped at the seams in the context map.

The model names every concept once, classifies each as an entity, a value object, or a domain event, and groups the entities into three aggregates (`Subscription`, `Invoice`, `Plan`), each guarding a single invariant. Concepts that belong to neighbors (`Product`, `Customer`) are referenced by identity across an anti-corruption layer rather than copied in.

## How to keep it honest

An ontology rots the moment it stops matching the code. Treat both files as source, not documentation:

- Keep them in version control next to the code they describe.
- Review changes to them in the same pull request that changes the model.
- Run the verification checklist from the blog post before merging: every code name should appear in the glossary, spelled the same way, and every aggregate should name the invariant it protects in one sentence.

## Tools that help

You can build this with a Markdown file and a Mermaid diagram, which is what this folder uses. When the model grows, these tools help define and visualize it:

- [Context Mapper](https://contextmapper.org/): an open-source domain-specific language for Domain-Driven Design context maps and bounded contexts. It generates diagrams and service contracts from text, which keeps the map in version control.
- [Archi](https://www.archimatetool.com/): a free, open-source modeling tool for the [ArchiMate](https://pubs.opengroup.org/architecture/archimate3-doc/) enterprise-architecture language, useful when the ontology has to line up with a wider architecture view.
- [Protege](https://protege.stanford.edu/): the long-standing editor for formal OWL/RDF ontologies, for when a glossary is not enough and you need machine reasoning over the model.

## Using AI to draft the first pass

Large language models are starting to do real work in ontology engineering, mostly as a fast, fallible first-drafter. A 2025 survey, [LLM-empowered knowledge graph construction](https://arxiv.org/abs/2510.20345), maps where they fit: extracting candidate concepts and relationships from documents, suggesting a taxonomy, and aligning terms across sources. The model proposes; the domain expert disposes.

A workable loop:

1. Paste real domain text (support tickets, a spec, a transcript) and ask the model to list the nouns and verbs it sees, with one-line definitions. This jump-starts Step 2.
2. Ask it to classify each as entity, value object, or event, and to flag any term used two ways. Treat every answer as a hypothesis to check, not a decision.
3. Ask it to draft the Mermaid relationship diagram, then correct the relationships by hand. Models invent plausible-but-wrong edges.

The failure mode is confident nonsense: invented relationships, missed ambiguity, and a tidy taxonomy that does not match how the business actually talks. The expert review in Step 2 and the verification checklist are what catch it. For a curated, current reading list, see [KG-LLM-Papers](https://github.com/zjukg/KG-LLM-Papers).

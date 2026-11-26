---
title: "Namespace and Identity Policy"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Namespace and Identity Policy

Preserve exact existing entity IRIs, including legacy Persona namespaces inside consolidated DAMA. Ontology identity is distinct from entity identity. Prefix changes do not change IRIs. Retain legacy ontology import resolution via a governed compatibility mechanism if required; do not assert owl:sameAs between ontology documents merely because one supersedes another. Use approved persistent namespaces for new entities and separate version IRIs for releases. Do not fabricate canonical namespace choices. Resolve and pin version IRIs where available, otherwise immutable revision and checksum. No owl:sameAs, owl:equivalentClass or equivalentProperty based only on lexical matches. Review domain/range and disjointness impacts. Breaking IRI changes require a separate ADR and migration report. Use stable mapping assertion IRIs with explicit provenance; source graph identifiers are not entity aliases.

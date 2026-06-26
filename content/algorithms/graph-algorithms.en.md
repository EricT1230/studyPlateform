# Graph Algorithms

Use this subject to train efficient problem solving: model the input, justify correctness, and estimate cost before coding.

This chapter maps to `algorithms/graph-algorithms` and should be studied together with the matching practice questions. The current bank includes 20 questions for this topic. Difficulty coverage: advanced, basic, intermediate, master.

## Core Concepts

The core of this chapter is graph representations, BFS, DFS, topological order, shortest paths, minimum spanning trees, and graph properties. Do not study these terms as isolated vocabulary. Connect each concept to the operation, invariant, cost model, or failure mode that makes it useful in an exam or engineering discussion.

A good mental model for this topic is to ask: what is the input, what structure is hidden in the input, what operation must be repeated, and what invariant must stay true after each step? If you can answer those questions, most multiple-choice distractors become easier to eliminate.

## Problem-Solving Focus

Focus on selecting algorithms from directedness, weights, negative edges, and acyclicity. Before looking at the answer choices, write down the relevant constraints, expected output, and one reason why an alternative approach may fail.

Useful tags for this chapter: graph, bfs, dfs, adjacency-list, complexity, topological-sort, cycle-detection, scc. When practicing, group wrong answers by cause: definition gap, missing condition, incorrect cost estimate, implementation detail, or English misread.

## Common Pitfalls

The most common mistake is using Dijkstra with negative edges or applying BFS distance logic to weighted graphs. Another recurring issue is answering from memory before checking the exact condition in the question. Many exam options are almost correct but fail because one assumption is missing.

When two options look similar, compare their preconditions. For example, ask whether the data is ordered, weighted, unique, independent, normalized, cached, synchronized, or evaluated on held-out data.

## Pre-Practice Checklist

- [ ] I can define the main objects in this chapter without looking at notes.
- [ ] I can explain the key invariant or rule in one sentence.
- [ ] I can identify at least one situation where the standard approach does not apply.
- [ ] I can estimate the relevant time, space, probability, or consistency cost.
- [ ] I can explain one wrong option from the practice set in my own words.

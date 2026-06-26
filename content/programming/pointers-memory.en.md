# Pointers and Memory

Use this subject to strengthen low-level code reading, memory reasoning, and C execution behavior.

This chapter maps to `programming/pointers-memory` and should be studied together with the matching practice questions. The current bank includes 20 questions for this topic. Difficulty coverage: advanced, basic, intermediate, master.

## Core Concepts

The core of this chapter is addresses, pointer variables, dereferencing, pointer arithmetic, stack, heap, malloc, free, ownership, dangling pointers, and buffer overflow. Do not study these terms as isolated vocabulary. Connect each concept to the operation, invariant, cost model, or failure mode that makes it useful in an exam or engineering discussion.

A good mental model for this topic is to ask: what is the input, what structure is hidden in the input, what operation must be repeated, and what invariant must stay true after each step? If you can answer those questions, most multiple-choice distractors become easier to eliminate.

## Problem-Solving Focus

Focus on drawing memory cells and arrows before answering pointer questions. Before looking at the answer choices, write down the relevant constraints, expected output, and one reason why an alternative approach may fail.

Useful tags for this chapter: c, pointers, address-of, dereference, arrays, pointer-arithmetic, sizeof, malloc. When practicing, group wrong answers by cause: definition gap, missing condition, incorrect cost estimate, implementation detail, or English misread.

## Common Pitfalls

The most common mistake is confusing the value stored in a pointer variable with the value at the pointed address. Another recurring issue is answering from memory before checking the exact condition in the question. Many exam options are almost correct but fail because one assumption is missing.

When two options look similar, compare their preconditions. For example, ask whether the data is ordered, weighted, unique, independent, normalized, cached, synchronized, or evaluated on held-out data.

## Pre-Practice Checklist

- [ ] I can define the main objects in this chapter without looking at notes.
- [ ] I can explain the key invariant or rule in one sentence.
- [ ] I can identify at least one situation where the standard approach does not apply.
- [ ] I can estimate the relevant time, space, probability, or consistency cost.
- [ ] I can explain one wrong option from the practice set in my own words.

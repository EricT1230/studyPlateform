# Synchronization

Use this subject to understand virtualization, concurrency, and persistence in real systems.

This chapter maps to `operating-systems/synchronization` and should be studied together with the matching practice questions. The current bank includes 20 questions for this topic. Difficulty coverage: advanced, basic, intermediate, master.

## Core Concepts

The core of this chapter is race conditions, critical sections, locks, atomic operations, semaphores, condition variables, monitors, and deadlocks. Do not study these terms as isolated vocabulary. Connect each concept to the operation, invariant, cost model, or failure mode that makes it useful in an exam or engineering discussion.

A good mental model for this topic is to ask: what is the input, what structure is hidden in the input, what operation must be repeated, and what invariant must stay true after each step? If you can answer those questions, most multiple-choice distractors become easier to eliminate.

## Problem-Solving Focus

Focus on finding shared state and possible interleavings before reasoning about correctness. Before looking at the answer choices, write down the relevant constraints, expected output, and one reason why an alternative approach may fail.

Useful tags for this chapter: critical-section, mutex, semaphore, deadlock, spinlock, atomicity, coffman, producer-consumer. When practicing, group wrong answers by cause: definition gap, missing condition, incorrect cost estimate, implementation detail, or English misread.

## Common Pitfalls

The most common mistake is adding a lock without checking lock order or wakeup conditions. Another recurring issue is answering from memory before checking the exact condition in the question. Many exam options are almost correct but fail because one assumption is missing.

When two options look similar, compare their preconditions. For example, ask whether the data is ordered, weighted, unique, independent, normalized, cached, synchronized, or evaluated on held-out data.

## Pre-Practice Checklist

- [ ] I can define the main objects in this chapter without looking at notes.
- [ ] I can explain the key invariant or rule in one sentence.
- [ ] I can identify at least one situation where the standard approach does not apply.
- [ ] I can estimate the relevant time, space, probability, or consistency cost.
- [ ] I can explain one wrong option from the practice set in my own words.

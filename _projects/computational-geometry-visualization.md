---
title: Computational Geometry Visualization
desc: Tool for the visualization of algorithms in computational geometry. Topics are convex hulls, line segment intersection, triangulation, range queries, voronoi diagrams.
published: 05.11.2025
language: en
---

## About this project 
In parallel to the -- sadly only 2 ECTS  -- lecture "Grafisch-geometrsiche Algorithmen", or, in english, "computational geometry" (Lecture notes can be found [here]({% link /assets/lecture_notes_pdf/cg.pdf %})), I am working through the accompanying book [Computational Geometry](https://link.springer.com/book/10.1007/978-3-540-77974-2) .
To test my understanding I wanted to try and visualize some of the algorithms covered in the lecture and book.
This page is dedicated to said project and contains videos of those algorithms.
The source code of the project can be found on [GitHub](https://github.com/jan-keuchel/Computational-Geometry-Visualization).

## Convex Hull
### Brute Force approach
The first ovious approach is to test all possible edges between all nodes if they are part of the convex hull. 
This is really slow and takes $$\mathcal{O}(n^3)$$ time.
<video controls="" preload="none">
<source src="/assets/videos/CH_brute_force.mp4" type="video/mp4">
</video>

### Monotonous Chains
This algorithm is already way quicker -- see lecture notes or the book for a detailed explanation. It only takes $$\mathcal{O}(n \log{n})$$ time.
<video controls="" preload="none">
<source src="/assets/videos/CH_graham_scan.mp4" type="video/mp4">
</video>

### Jarvis' March
Another algorithm is the so called Jarvis' March or Gift Wrapping Algorithm which is an output sensitive algorithm.
This algorithm starts out at the left most point and then circulates around the set of points always finding the next vertex in the convex hull.
The running time is $$\mathcal{O}(n \cdot k)$$ with $$k$$ being the number of vertices in the convex hull.
<video controls="" preload="none">
<source src="/assets/videos/CH_jarvis_march.mp4" type="video/mp4">
</video>

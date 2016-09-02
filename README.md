# drawgraph

This small python program draws a given graph using an online version of the Fruchtermann-Reingold algorithm. Lets you interact with the graph using the mouse.

# Demostration

You can see the program in action in this video:

[http://www.youtube.com/watch?v=qzOLzU77Qt0](http://www.youtube.com/watch?v=qzOLzU77Qt0)

# Input

You type the graph into stdin (or using redirects). First you introduce the number of nodes, then the nodes, then the edges. The following is an example creating a graph with three nodes (A, B and C), pairwise connected:

```
3
A
B
C
A B
A C
B C
```
# Controls

Run this to learn of to use this program:

> python2 drawgraph.py -h

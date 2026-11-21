# EKD Variant 1
# AI Usage:
# Write details about how you used AI for this project.

from __future__ import annotations
import os
import json
import math
from typing import List

# Data Classes
# DO NOT MODIFY!
class Point():
    def __init__(self,
                 x : int,
                 y : int):
        self.x = x
        self.y = y
class Datum():
    def __init__(self,
                 point : Point,
                 code  : str):
        self.point = point
        self.code  = code
    def to_json(self) -> dict:
        dict_repr = {'coords':[self.point.x,self.point.y],'code':self.code}
        return(dict_repr)
class BoundingBox():
    def __init__(self,
                 xmin : int,
                 xmax : int,
                 ymin : int,
                 ymax : int):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

# Node Classes
# # DO NOT MODIFY!
class NodeInternal():
    def  __init__(self,
                  splitcoord : str,
                  splitvalue : float,
                  leftchild,
                  rightchild,
                  boundingbox : BoundingBox):
        self.splitcoord = splitcoord
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild
        self.boundingbox = boundingbox
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum],
                  boundingbox : BoundingBox):
        self.data = data
        self.boundingbox = boundingbox


class EKDtree():
    # DO NOT MODIFY.
    def  __init__(self,
                  splitmethod : str, # cycle or custom
                  m           : int,
                  root        : NodeLeaf = None):
        self.m    = m
        self.splitmethod = splitmethod
        self.root = root

    # DO NOT MODIFY!
    def customdump(self):
        def recurse(node,indent):
            if isinstance(node,NodeLeaf):
                print(f"{indent*' '} |bb:     [{node.boundingbox.xmin},{node.boundingbox.xmax}]x[{node.boundingbox.ymin},{node.boundingbox.ymax}]")
                for datum in node.data:
                    print(f"{indent*' '} |datum:  ({datum.point.x},{datum.point.y}) {datum.code}")
            else:
                print(f"{indent*' '}  split: {node.splitcoord} = {node.splitvalue}")
                print(f"{indent*' '}  bb:    [{node.boundingbox.xmin},{node.boundingbox.xmax}]x[{node.boundingbox.ymin},{node.boundingbox.ymax}]")
                print(f"{indent*' '}  leftchild:")
                recurse(node.leftchild,indent+2)
                print(f"{indent*' '}  rightchild:")
                recurse(node.rightchild,indent+2)
        if self.root is not None:
            recurse(self.root,0)
        else:
            print("No Tree!")



    @staticmethod
    def _bb_points(data):
        xs = [d.point.x for d in data]
        ys = [d.point.y for d in data]
        return BoundingBox(min(xs), max(xs), min(ys), max(ys))

    @staticmethod
    def _bb_union(a, b):
        return BoundingBox(min(a.xmin, b.xmin), max(a.xmax, b.xmax), min(a.ymin, b.ymin), max(a.ymax, b.ymax))

    def _choose_dim(self, data, parent_dim):
        if self.splitmethod == 'cycle':
            if parent_dim is None:
                return 'x'
            return 'y' if parent_dim == 'x' else 'x'
        nx = len({d.point.x for d in data})
        ny = len({d.point.y for d in data})
        return 'y' if ny > nx else 'x'

    def _split_leaf(self, leaf, parent_dim):
        dim = self._choose_dim(leaf.data, parent_dim)
        if dim == 'x':
            key = lambda d: (d.point.x, d.point.y)
            val = lambda d: d.point.x
        else:
            key = lambda d: (d.point.y, d.point.x)
            val = lambda d: d.point.y
        pts = sorted(leaf.data, key=key)
        n = len(pts)
        mid = n // 2
        left, right = pts[:mid], pts[mid:]
        if n % 2 == 1:
            value = float(val(pts[mid]))
        else:
            value = (val(pts[mid - 1]) + val(pts[mid])) / 2
        l = NodeLeaf(left, self._bb_points(left))
        r = NodeLeaf(right, self._bb_points(right))
        return NodeInternal(dim, value, l, r, self._bb_union(l.boundingbox, r.boundingbox))

    def _goes_left(self, node, datum):
        val = datum.point.x if node.splitcoord == 'x' else datum.point.y
        if val == node.splitvalue:
            return val % 2 == 0          # tie: even -> left, odd -> right
        return val < node.splitvalue

    def _redistribute(self, node, datum):
        pts = node.leftchild.data + node.rightchild.data + [datum]
        if node.splitcoord == 'x':
            key = lambda d: (d.point.x, d.point.y)
            val = lambda d: d.point.x
        else:
            key = lambda d: (d.point.y, d.point.x)
            val = lambda d: d.point.y
        pts.sort(key=key)
        mid = len(pts) // 2
        left, right = pts[:mid], pts[mid:]
        node.splitvalue = (val(left[-1]) + val(right[0])) / 2
        node.leftchild = NodeLeaf(left, self._bb_points(left))
        node.rightchild = NodeLeaf(right, self._bb_points(right))
        node.boundingbox = self._bb_union(node.leftchild.boundingbox, node.rightchild.boundingbox)

    def _insert(self, node, datum, parent_dim, nonstandard):
        if isinstance(node, NodeLeaf):
            node.data.append(datum)
            node.boundingbox = self._bb_points(node.data)
            if len(node.data) > self.m:
                return self._split_leaf(node, parent_dim)
            return node

        go_left = self._goes_left(node, datum)
        child = node.leftchild if go_left else node.rightchild
        sibling = node.rightchild if go_left else node.leftchild

        # nonstandard: if the target leaf is full and its sibling leaf has room,
        # rebalance across this node's split instead of creating a new split
        if (nonstandard and isinstance(child, NodeLeaf) and isinstance(sibling, NodeLeaf)
                and len(child.data) >= self.m and len(sibling.data) < self.m):
            self._redistribute(node, datum)
            return node

        new = self._insert(child, datum, node.splitcoord, nonstandard)
        if go_left:
            node.leftchild = new
        else:
            node.rightchild = new
        node.boundingbox = self._bb_union(node.leftchild.boundingbox,
                                          node.rightchild.boundingbox)
        return node

    def _do_insert(self, datum, nonstandard):
        if self.root is None:
            self.root = NodeLeaf([datum], self._bb_points([datum]))
        else:
            self.root = self._insert(self.root, datum, None, nonstandard)

    def insert_standard(self, datum: Datum):
        self._do_insert(datum, False)

    def insert_nonstandard(self, datum: Datum):
        self._do_insert(datum, True)

    def _delete(self, node, p):
        if isinstance(node, NodeLeaf):
            for i, d in enumerate(node.data):
                if d.point.x == p.x and d.point.y == p.y:
                    del node.data[i]
                    if not node.data:
                        return None, True
                    node.boundingbox = self._bb_points(node.data)
                    return node, True
            return node, False
        for side in ('leftchild', 'rightchild'):
            child = getattr(node, side)
            bb = child.boundingbox
            if bb.xmin <= p.x <= bb.xmax and bb.ymin <= p.y <= bb.ymax:
                new, found = self._delete(child, p)
                if found:
                    if new is None:
                        return (node.rightchild if side == 'leftchild' else node.leftchild), True
                    setattr(node, side, new)
                    node.boundingbox = self._bb_union(node.leftchild.boundingbox, node.rightchild.boundingbox)
                    return node, True
        return node, False

    def delete(self, point: Point):
        if self.root is None:
            return
        self.root, _ = self._delete(self.root, point)

    def knn_query(self, point: Point, k: int) -> str:
        best = []
        visited = [0]

        def bbdist2(bb):
            dx = max(bb.xmin - point.x, 0, point.x - bb.xmax)
            dy = max(bb.ymin - point.y, 0, point.y - bb.ymax)
            return dx * dx + dy * dy

        def recurse(node):
            if isinstance(node, NodeLeaf):
                for d in node.data:
                    dx, dy = d.point.x - point.x, d.point.y - point.y
                    best.append((dx * dx + dy * dy, d.code, d))
                best.sort(key=lambda t: (t[0], t[1]))
                del best[k:]
                return
            visited[0] += 1
            kids = sorted([node.leftchild, node.rightchild], key=lambda n: bbdist2(n.boundingbox))
            for c in kids:
                if len(best) >= k and bbdist2(c.boundingbox) > best[-1][0]:
                    continue
                recurse(c)

        if self.root is not None and k > 0:
            recurse(self.root)
        metric = visited[0]
        return json.dumps({"metric": metric, "points": [str(t[2].to_json()) for t in best]}, indent=2)

    # Draw a picture of the points and bounding boxes.
    # You will need to install matplotlib to use this.
    # Add the following line in the tracefile:
    # plot
    # Note that the autograder will never add this line.

    def plotit(self):
        if self.root == None:
            return
        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Rectangle
        except ImportError:
            return
        def _plot(node,pointlist: List[tuple],boxlist: List[tuple]):
            if isinstance(node,NodeInternal):
                _plot(node.leftchild,pointlist,boxlist)
                _plot(node.rightchild,pointlist,boxlist)
                boxlist.append([node.boundingbox.xmin,node.boundingbox.ymin,node.boundingbox.xmax,node.boundingbox.ymax])
            else:
                pointlist.extend([[datum.point.x,datum.point.y] for datum in node.data])
                boxlist.append([node.boundingbox.xmin,node.boundingbox.ymin,node.boundingbox.xmax,node.boundingbox.ymax])
        pointlist = []
        boxlist = []
        _plot(self.root,pointlist,boxlist)
        fig,ax = plt.subplots()
        x, y = zip(*pointlist)
        ax.scatter(x=x, y=y)
        for bb in boxlist:
            rect = Rectangle((bb[0],bb[1]),bb[2]-bb[0],bb[3]-bb[1],
                 linewidth=1, edgecolor='r', facecolor='red', alpha=0.2)  # facecolor='none' makes it transparent
            ax.add_patch(rect)
        plt.savefig("plot.png", dpi=200, bbox_inches="tight")
        plt.close()
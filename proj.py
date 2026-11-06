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

    def insert_standard(self,datum:Datum):
        dummy = True

    def insert_nonstandard(self,datum:Datum):
        dummy = True

    def delete(self,point:Point):
        dummy = True

    def knn_query(self,point:Point,k:int) -> str:
        metric = 0
        knnlist = []
        return(json.dumps({"metric":metric,"points":[str(datum.to_json()) for datum in knnlist]},indent=2))

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
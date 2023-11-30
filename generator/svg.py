###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
"""svg.py: Helper class to render union jack graph as svg."""

__author__ = "Ruben S. Andrist"
__email__ = "randrist@amazon.com"


from typing import Any, Dict


class Svg:
    def __init__(self, L: int) -> None:
        self.L = L
        self.nodes = []
        self.edges = []
        self.scale = 20

    Node = Dict[str, Any]

    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes += [node]

    def add_edge(self, a: Node, b: Node) -> None:
        """Create an edge between two nodes."""
        self.edges += [[a, b]]

    def viewBox(self, scale: float) -> str:
        """Compute the appropriate svg view box."""
        return "{shift} {shift} {L} {L}".format(shift=-0.5 * scale, L=self.L * scale)

    def tag(
        self,
        name: str,
        indent: int = 0,
        closed: bool = False,
        innerHtml: str = None,
        **kwargs,
    ):
        """Create an svg tag."""
        t = " " * indent
        if len(kwargs) == 0 and closed and innerHtml is None:
            return t + f"</{name}>\n"
        t += f"<{name}"
        for k, v in kwargs.items():
            t += " " + k.replace("_", "-") + f'="{v}"'
        if innerHtml is not None:
            t += f">{innerHtml}"
            if closed:
                t += f"</{name}>"
            return t + "\n"
        if closed:
            t += " /"
        return t + ">\n"

    def render_edge(self, a: Node, b: Node) -> str:
        """Create the svg tag for an edge."""
        return self.tag(
            "line",
            indent=4,
            x1=a["x"] * self.scale,
            y1=a["y"] * self.scale,
            x2=b["x"] * self.scale,
            y2=b["y"] * self.scale,
            stroke="black",
            stroke_width=0.01 * self.scale,
            closed=True,
        )

    def render_node(self, node: Node) -> str:
        """Create the svg tag for a node."""
        return self.tag(
            "circle",
            indent=4,
            cx=node["x"] * self.scale,
            cy=node["y"] * self.scale,
            r=0.1 * self.scale,
            stroke="black",
            stroke_width=0.01 * self.scale,
            fill="green",
            closed=True,
        )

    def render_label(self, x: int, y: int, text: str) -> str:
        """Create the svg tag for a node label."""
        return self.tag(
            "text",
            indent=4,
            x=x * self.scale,
            y=(y + 0.04) * self.scale,
            font_size=0.1 * self.scale,
            fill="white",
            text_anchor="middle",
            innerHtml=text,
            closed=True,
        )

    def render(self) -> str:
        """Render the graph as a svg.

        This should be called after all nodes and edges have been added.
        """
        s = self.scale
        L = self.L
        svg = self.tag(
            "svg",
            height=L * s,
            width=L * s,
            viewBox=self.viewBox(s),
            xmlns="http://www.w3.org/2000/svg",
        )

        svg += self.tag("g", indent=2, id="edges")
        for e in self.edges:
            svg += self.render_edge(*e)
        svg += self.tag("g", indent=2, closed=True)
        svg += self.tag("g", indent=2, id="nodes")
        for n in self.nodes:
            svg += self.render_node(n)
        svg += self.tag("g", indent=2, closed=True)
        svg += self.tag("g", indent=2, id="labels")
        for i, n in enumerate(self.nodes):
            svg += self.render_label(n["x"], n["y"], str(i))
        svg += self.tag("g", indent=2, closed=True)
        svg += self.tag("svg", closed=True)
        return svg

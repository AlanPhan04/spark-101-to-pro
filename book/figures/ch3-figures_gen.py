#!/usr/bin/env python3
"""Chapter 3 concept figures: writes the .drawio sources and renders them to ../images/*.pdf.

  jvm-jit-pipeline      source -> bytecode -> interpreter -> JIT -> machine code
  object-overhead       List<Integer> against int[]: where the 20.6 MB vs 4.0 MB comes from
  memory-per-task       heap -> unified pool -> share per task at 4 and 8 cores (worked for a 4 GiB heap)
  gc-generations        young / old generations and what each collection costs
  gc-collector-timelines  schematic pause shapes of Parallel, G1 and ZGC (not to scale)
  serialization-bytes   one record, Java serializer against Kryo (299 B against 42 B)
"""
import html
import os

from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, os.pardir, "images")

ROLES = {
    "blue": "fillColor=#cfe0f4;strokeColor=#3b6ea5;fontColor=#1f3d5c;",
    "green": "fillColor=#d8ebcf;strokeColor=#4f8a3d;fontColor=#2f5320;",
    "rose": "fillColor=#f7dde0;strokeColor=#b5545e;fontColor=#7d2f38;strokeWidth=2;",
    "orange": "fillColor=#fce7d2;strokeColor=#c77f3b;fontColor=#7a4a17;",
    "purple": "fillColor=#ece6f4;strokeColor=#6a5a8a;fontColor=#3f335c;",
    "gray": "fillColor=#eceef1;strokeColor=#6b7280;fontColor=#374151;",
    "amber": "fillColor=#fbeecf;strokeColor=#c9a227;fontColor=#7a5c0a;",
}
CONT = {
    "blue": "fillColor=#eaf1fb;strokeColor=#3b6ea5;fontColor=#1f3d5c;",
    "green": "fillColor=#e4f1dc;strokeColor=#4f8a3d;fontColor=#2f5320;",
    "rose": "fillColor=#fdeef0;strokeColor=#b5545e;fontColor=#7d2f38;",
    "orange": "fillColor=#fdf1e3;strokeColor=#c77f3b;fontColor=#7a4a17;",
    "purple": "fillColor=#f3effa;strokeColor=#6a5a8a;fontColor=#3f335c;",
}
EDGE = {
    "blue": "strokeColor=#3b6ea5;strokeWidth=2;",
    "green": "strokeColor=#4f8a3d;strokeWidth=2;",
    "rose": "strokeColor=#b5545e;strokeWidth=2;",
    "gray": "strokeColor=#6b7280;strokeWidth=2;",
    "orange": "strokeColor=#c77f3b;strokeWidth=2;",
    "purple": "strokeColor=#6a5a8a;strokeWidth=2;dashed=1;",
}


class Fig:
    def __init__(self, name, width, height):
        self.name, self.w, self.h = name, width, height
        self.cells = []

    def _v(self, cid, x, y, w, h, value, style):
        v = html.escape(value, quote=True)
        self.cells.append(
            f'<mxCell id="{cid}" value="{v}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>')

    def box(self, cid, x, y, w, h, text, role, dashed=False, size=14, plain=False):
        st = ("rounded=0;" if plain else "rounded=1;") + "whiteSpace=wrap;html=1;" + ROLES[role]
        if dashed:
            st += "dashed=1;"
        self._v(cid, x, y, w, h, text, st + f"fontSize={size};")

    def container(self, cid, x, y, w, h, title, role):
        st = ("rounded=1;whiteSpace=wrap;html=1;container=1;verticalAlign=top;spacingTop=8;"
              + CONT[role] + "fontSize=16;")
        self._v(cid, x, y, w, h, "<b>" + title + "</b>", st)

    def text(self, cid, x, y, w, h, text, size=14, align="center", color="#57503f"):
        st = (f"text;html=1;fillColor=none;strokeColor=none;align={align};fontColor={color};"
              f"fontSize={size};")
        self._v(cid, x, y, w, h, text, st)

    def edge(self, cid, src, dst, role="blue", label="", extra=""):
        v = html.escape(label, quote=True)
        self.cells.append(
            f'<mxCell id="{cid}" value="{v}" style="endArrow=block;html=1;{EDGE[role]}{extra}" '
            f'edge="1" parent="1" source="{src}" target="{dst}">'
            f'<mxGeometry relative="1" as="geometry" /></mxCell>')

    def save(self):
        body = "\n".join(self.cells)
        xml = (f'<mxfile host="app.diagrams.net"><diagram name="{self.name}" id="{self.name}">'
               f'<mxGraphModel dx="800" dy="400" grid="1" gridSize="20" page="1" pageScale="1" '
               f'pageWidth="{self.w}" pageHeight="{self.h}" math="0" shadow="0"><root>'
               f'<mxCell id="0" /><mxCell id="1" parent="0" />\n{body}\n</root></mxGraphModel>'
               f'</diagram></mxfile>')
        src = os.path.join(HERE, self.name + ".drawio")
        open(src, "w", encoding="utf-8").write(xml)
        render(src, os.path.join(IMG, self.name + ".pdf"))


def jvm_jit_pipeline():
    f = Fig("jvm-jit-pipeline", 640, 300)
    f.box("src", 20, 30, 110, 60, "Scala source<br>(Spark's code)", "gray")
    f.box("cmp", 160, 30, 110, 60, "Compiler<br>(build time)", "blue")
    f.box("bc", 290, 30, 150, 60, "<b>Bytecode</b><br>portable, not native", "gray")
    f.edge("e1", "src", "cmp")
    f.edge("e2", "cmp", "bc")
    f.text("t1", 450, 45, 170, 30, "done once, before the job", align="left")
    f.container("jvm", 20, 130, 600, 140, "The JVM, at run time (every executor)", "blue")
    f.box("int", 40, 185, 150, 70, "<b>Interpreter</b><br>runs bytecode<br>slowly", "orange")
    f.box("jit", 235, 185, 150, 70, "<b>JIT compiler</b><br>compiles methods<br>called often", "blue")
    f.box("mc", 430, 185, 170, 70, "<b>Machine code</b><br>runs at full speed", "green")
    f.edge("e3", "bc", "int", "gray", extra="exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
    f.edge("e4", "int", "jit", "blue")
    f.edge("e5", "jit", "mc", "green", label="")
    f.text("t2", 20, 272, 600, 26, "first runs: mostly interpreted  →  later runs: compiled", align="center")
    f.save()


def object_overhead():
    f = Fig("object-overhead", 640, 350)
    f.container("l", 20, 20, 290, 310, "List&lt;Integer&gt;: 20.6 MB", "rose")
    f.container("r", 330, 20, 290, 310, "int[]: 4.0 MB", "green")
    xs = [32, 120, 208]
    for i, x in enumerate(xs):
        f.box(f"ref{i}", x, 80, 82, 40, "ref 4 B", "gray")
        f.box(f"hd{i}", x, 170, 52, 40, "header", "rose", plain=True)
        f.box(f"va{i}", x + 52, 170, 30, 40, "int", "blue", plain=True)
        f.edge(f"a{i}", f"ref{i}", f"hd{i}", "rose")
    f.text("lt", 30, 225, 270, 60, "each integer: a 4 B reference<br>plus a 16 B object<br>to hold 4 B of data", align="center")
    f.text("lt2", 30, 295, 270, 26, "per million: 20.6 MB", align="center", color="#7d2f38")
    for i, x in enumerate([350, 432, 514]):
        f.box(f"c{i}", x, 80, 82, 40, "4 B", "green", plain=True)
    f.text("rt", 340, 140, 270, 60, "one array, no per-value header,<br>no references", align="center")
    f.text("rt2", 340, 295, 270, 26, "per million: 4.0 MB", align="center", color="#2f5320")
    f.save()


def memory_per_task():
    f = Fig("memory-per-task", 640, 340)
    # scale: 600 px = 4096 MiB heap
    k = 600 / 4096.0
    reserved, unified, user = 300 * k, 2277.6 * k, 1518.4 * k
    x0 = 20
    f.text("h0", 20, 8, 600, 26, "<b>JVM heap, 4 GiB</b>  (spark.executor.memory)", align="left", size=15, color="#2f3b52")
    f.box("res", x0, 40, round(reserved), 70, "300", "gray", plain=True)
    f.box("uni", x0 + round(reserved), 40, round(unified), 70,
          "<b>Unified pool</b><br>(4096 − 300) × 0.6 = 2278 MiB", "blue", plain=True)
    f.box("usr", x0 + round(reserved) + round(unified), 40, round(user), 70,
          "<b>User memory</b><br>40%, not tracked", "rose", plain=True)
    ux = x0 + round(reserved)
    uw = round(unified)
    f.text("l1", ux, 118, uw, 26, "shared by every task running at the same moment", size=14)
    for i in range(4):
        f.box(f"a{i}", ux + i * uw // 4, 160, uw // 4, 50, "569", "green", plain=True)
    for i in range(8):
        f.box(f"b{i}", ux + i * uw // 8, 245, uw // 8, 50, "285", "green", plain=True)
    f.text("r1", ux + uw + 14, 160, 220, 50, "<b>4 cores</b><br>569 MiB per task", align="left")
    f.text("r2", ux + uw + 14, 245, 220, 50, "<b>8 cores</b><br>285 MiB per task", align="left")
    f.text("n", 20, 305, 600, 26, "same heap, same pool: more cores, a smaller share for each task", align="center")
    f.save()


def gc_generations():
    f = Fig("gc-generations", 640, 320)
    f.box("new", 20, 130, 110, 60, "New<br>objects", "gray")
    f.container("young", 160, 40, 270, 240, "Young generation", "blue")
    f.box("eden", 180, 90, 100, 60, "<b>Eden</b><br>allocated here", "green")
    f.box("surv", 310, 90, 100, 60, "<b>Survivor</b><br>still in use", "green")
    f.text("yn", 175, 170, 245, 90, "<b>minor collection</b><br>frequent and cheap:<br>most objects are already dead", align="center")
    f.container("old", 470, 40, 150, 240, "Old generation", "rose")
    f.box("oldb", 485, 90, 120, 70, "long-lived data:<br>cached blocks,<br>big tables", "orange")
    f.text("on", 480, 175, 135, 90, "<b>full collection</b><br>rare and expensive", align="center", color="#7d2f38")
    f.edge("e1", "new", "eden", "blue")
    f.edge("e2", "eden", "surv", "green", label="")
    f.edge("e3", "surv", "oldb", "orange")
    f.text("pr", 408, 86, 80, 26, "promoted", size=14)
    f.save()


def gc_collector_timelines():
    f = Fig("gc-collector-timelines", 640, 330)
    x0, x1 = 160, 620
    f.text("th", x0, 8, x1 - x0, 24, "time →   (schematic, not to scale)", align="left", size=14, color="#555555")
    lanes = [("Parallel", 50, [(300, 90)]),
             ("G1", 130, [(200, 16), (260, 16), (320, 16), (380, 16), (440, 16), (500, 16)]),
             ("ZGC", 210, [(310, 4), (480, 4)])]
    notes = {"Parallel": "one long pause", "G1": "many short pauses", "ZGC": "almost none"}
    for name, y, pauses in lanes:
        f.text(f"n{name}", 20, y, 130, 40, f"<b>{name}</b>", align="left", size=15, color="#2f3b52")
        f.box(f"run{name}", x0, y, x1 - x0, 50, "", "green", plain=True)
        for i, (px, pw) in enumerate(pauses):
            f.box(f"p{name}{i}", px, y, pw, 50, "", "rose", plain=True)
        f.text(f"d{name}", x0, y + 52, x1 - x0, 24, notes[name], align="left", size=14)
    f.box("lg1", 160, 292, 30, 24, "", "green", plain=True)
    f.text("lt1", 196, 290, 160, 28, "application runs", align="left")
    f.box("lg2", 370, 292, 30, 24, "", "rose", plain=True)
    f.text("lt2", 406, 290, 214, 28, "stop-the-world pause", align="left")
    f.save()


def serialization_bytes():
    f = Fig("serialization-bytes", 640, 360)
    f.box("o", 20, 20, 150, 56, "<b>Objects</b><br>in the heap", "gray")
    f.box("s", 230, 20, 150, 56, "<b>Serializer</b>", "blue")
    f.box("b", 440, 20, 180, 56, "<b>Flat bytes</b><br>shuffle, spill, broadcast", "green")
    f.edge("e1", "o", "s", "blue")
    f.edge("e2", "s", "b", "blue")
    f.text("q", 20, 95, 600, 26, "<b>One record, written two ways</b> (20,000 five-field records, measured)", align="left", size=15, color="#2f3b52")
    sc = 250 / 299.0
    f.text("jl", 20, 130, 300, 24, "Java serializer: 299 bytes per record", align="left")
    f.box("jd", 20, 158, round(257 * sc), 50, "class name and field names", "rose", plain=True)
    f.box("jv", 20 + round(257 * sc), 158, round(42 * sc), 50, "data", "green", plain=True)
    f.box("jd2", 290, 158, round(257 * sc), 50, "class name and field names", "rose", plain=True)
    f.box("jv2", 290 + round(257 * sc), 158, round(42 * sc), 50, "data", "green", plain=True)
    f.text("kl", 20, 235, 300, 24, "Kryo: 42 bytes per record", align="left")
    f.box("kv", 20, 263, round(42 * sc), 50, "data", "green", plain=True)
    f.box("kv2", 20 + round(42 * sc) + 6, 263, round(42 * sc), 50, "data", "green", plain=True)
    f.box("kv3", 20 + 2 * (round(42 * sc) + 6), 263, round(42 * sc), 50, "data", "green", plain=True)
    f.text("kn", 200, 270, 420, 40, "a short class id plus the values;<br>no repeated description", align="left")
    f.text("foot", 20, 325, 600, 26, "an array of records writes the description once, so the gap shrinks to 58 vs 41 bytes", align="left")
    f.save()


if __name__ == "__main__":
    for fn in (jvm_jit_pipeline, object_overhead, memory_per_task, gc_generations,
               gc_collector_timelines, serialization_bytes):
        fn()

# Development guide

This document is intended for Yukon developers only, not users.


## Design

The high-level ideas behind Yukon are outlined in the following unorganized sources:

- Main features: https://forum.uavcan.org/t/gui-tool-next-generation/229/2?u=pavel.kirienko

- Canvas UI:
  - https://forum.uavcan.org/t/gui-tool-next-generation/229/24?u=pavel.kirienko
  - https://forum.uavcan.org/t/gui-tool-next-generation/229/53?u=pavel.kirienko

- Original design proposal by Scott Dixon:
  https://github.com/UAVCAN/yukon/blob/ee94032a8f5d5775372174808e121212c4401500/design/index.md

Also see the dedicated forum category at https://forum.uavcan.org/c/app/yukon/14.

In 2020, Amazon sponsored Nuno Marques to do some early-stage/exploratory work on this project.
This initial work was focused mostly on the front-end, tentatively ignoring the backend and the core business logic
of the application.
While this work package was not meant to produce any tangible product,
it was still useful in resurfacing important questions that require special attention at the design stage.
Specifically:

- **The application has to be usable with high-throughput networks.**
  In the Nuno's work package this category of issues was categorized under
  *[key performance indicators](https://github.com/UAVCAN/yukon/issues?q=kpi)*.

- Early exploration of the
  [monetization prospects](https://docs.google.com/presentation/d/16HzYFdCbv-Xs9wuDjYkmjcSQeCi84MNvMEfJu-5tiV8/edit)
  revealed that the application should be sufficiently extensible for packaging advanced features
  (such as postmortem log analysis) into optional, proprietary,
  [non-free components supplied by third parties](https://forum.uavcan.org/t/gui-tool-next-generation/229/57).
  To be useful, this *extension framework* should allow the extension developer to significantly alter the
  behaviors of the application.

- **The Canvas UI was identified as the core UI component of the application.**
  All of the capabilities are to be built around this component, with one notable exception of the
  [Global Register View](https://forum.uavcan.org/t/yukon-design-megathread/390/25?u=pavel.kirienko).

The current work builds upon the experience we gained from Nuno's work and
many fruitful discussions around it.
Unlike the earlier experimental efforts, this work takes a more structured approach where the
design process is primarily focused on the backend architecture and the business logic rather than the UI.

The application is built as a multi-process decentralized system where different components of the application
interact by means of a UAVCAN-based data distribution network.
That is, in the best spirit of dogfooding, ***the UAVCAN IDE is itself built on UAVCAN***.
As will be shown later, this design is expected to accommodate the core design requirements identified at
the earlier stages of the project.

The application will consist of several main processes (that is, UAVCAN nodes) on its
distributed computing (DCS) graph:

- The **Head node** that runs the user interface UI.
  This is the main point of contact with the user.
  The Head node is responsible for starting the other nodes at launch.

- The **IO worker** node (IOW) that bridges Yukon's internal data distribution system with the analyzed network.
  It is responsible for initializing and interacting with the networking hardware connected to the local computer,
  such as Ethernet NIC, CAN adapters, etc.,
  and forwarding raw data frames (such as Ethernet or CAN frames) from the adapter to the DCS and back.

  In the case of postmortem analysis, the IOW is to be replaced with a log reader node similar to *rosbag*.
  By virtue of implementing the same UAVCAN network service interface on the DCS,
  the log reader can transparently replace the IOW without other nodes having to be aware of the replacement.

- The **Avatar node** that is responsible for accurately tracking the state of each node on the analyzed network.
  This involves reassembly of all transfers emitted by each node, configuration change tracking, and so on.
  Reassembled transfers are published on a specific DCS subject (actually several, sharded by port-ID
  for purposes of load balancing).

- **Canvas UI component nodes**.
  Whenever a new item is placed on the Canvas,
  the Head node launches a new node process that connects to the DCS subjects it requires to fulfill its function.

  For example, to plot a specific field from a subject, one would drop a new component onto the canvas,
  which would launch the new plotter node, and then drag the inputs of the new item to the correct subjects
  displayed on the canvas.
  In response to that, the Head node would instruct the plotter node to start listening for a specific subject.

  UI component nodes render complex graphics internally into a texture
  (e.g, using [Kaleido](https://github.com/plotly/Kaleido)),
  which is then transferred over to the Head node for displaying.
  Common graphical primitives such as buttons and textbox fields can be transferred using dedicated DSDL messages,
  like:

      @union
      org_uavcan_yukon.ui.Button.1.0  button
      org_uavcan_yukon.ui.Spinbox.1.0 spinbox
      org_uavcan_yukon.ui.Textbox.1.0 textbox
      # etc.

  Whenever the user interacts with a UI element, the callback is delivered back to the publisher via RPC-service call
  over the DCS.

As is generally the case with data distribution systems, the IDL definitions (DSDL definitions in this case)
are the main component of the implementation,
since they effectively define behavioral and interaction contracts for all components of the application.
The DSDL definitions of Yukon's DCS are contained under `/yukon/dsdl_src` (do explore them).
Their compiled outputs are distributed together with the application;
the compilation is done by `setup.py` at build time.

The solid DSDL contracts at the foundation of the application provide a natural integration point for extensions.
The proposed strategy for the *extension framework* is to let third-party components integrate directly with the DCS
as opposed to some API as is typically the case in other projects.
While this may result in some boilerplate logic, the positive side is that extensions can be implemented
in different programming languages, be run on remote machines,
and be unaffected by refactorings of the application's core as long as the DCS's DSDL definitions remain compatible.

The heavy reliance on multi-processing is expected to be friendly to modern computers that tend
to be well-optimized for highly concurrent workloads.
This is why this design is expected to be able to interact with high-throughput UAVCAN networks in real-time,
especially if it is executed by a JIT-enabled Python runtime (like PyPy or Pyston).
Even CPython shouldn't pose a problem in many scenarios because PyUAVCAN appears to be able to handle high-throughput
data flows in real time without significant performance issues.

The original work done by Nuno builds its UI using web technologies.
This is an okay strategy but it might be sensible to consider a more modern, lower-level, GPU-based
solution that might be  a better choice for a high-performance application:
[**Dear ImGui**](https://github.com/ocornut/imgui).
There are several projects that build a node editor on top of that library which is related to what we're after here:

- https://github.com/Nelarius/imnodes
- https://github.com/thedmd/imgui-node-editor
- https://github.com/ocornut/imgui/issues/3488#issuecomment-703280919

This description is far from being exhaustive but it is not supposed to be so.
The preferred course of action is to implement the bare minimum functionality without documenting it,
and then **let Yukon describe itself**, since it is built for analyzing UAVCAN networks like its own internal one.


## Conventions

Follow PEP8 except that the maximum line length is 120 characters.
Compliance is enforced by Black and PyLint.

When re-exporting entities from a package-level ``__init__.py``,
always use the form ``import ... as ...`` even if the name is not changed
to signal static analysis tools that the name is intended to be re-exported
(unless the aliased name starts with an underscore).
Compliance is enforced by MyPy (it is set up with ``implicit_reexport=0``).


## Testing

Come back later.


## Releasing

Too soon.


## Tools

We recommend [JetBrains PyCharm](https://www.jetbrains.com/pycharm/) for development.
Configure a File Watcher to run Black on save (make sure to disable running it on external file changes though).

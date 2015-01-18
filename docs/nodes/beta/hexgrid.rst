Hexagonal grid
==============

*destination after Beta: Generators*

Functionality
-------------

This node can produce either hexagonal or triangular grid of specified size.

Inputs & Parameters
-------------------

All parameters except for **Mode** can be given by the node or an external input.
This node has the following parameters:

+----------------+---------------+-------------+----------------------------------------------------------+
| Parameter      | Type          | Default     | Description                                              |  
+================+===============+=============+==========================================================+
| **Mode**       | Hex or Trig   | Hex         | What kind of grid to generate: hexagonal or triangular.  |
+----------------+---------------+-------------+----------------------------------------------------------+
| **Step**       | Float         | 1.0         | Length of grid's edge.                                   |
+----------------+---------------+-------------+----------------------------------------------------------+
| **Size U**     | Int           | 10          | Number of grid vertices along the first dimension.       |
+----------------+---------------+-------------+----------------------------------------------------------+
| **Size V**     | Int           | 10          | Number of grid vertices along the second dimension.      |
+----------------+---------------+-------------+----------------------------------------------------------+
| **Angle**      | Float         | 60.0        | Main angle of the grid, in degrees. Default value of 60  |
|                |               |             | creates regular hexagons or triangles.                   |
+----------------+---------------+-------------+----------------------------------------------------------+

Outputs
-------

This node has the following outputs:

- **Vertices**
- **Edges**
- **Polygons**

This node does not generate anything if ``Vertices`` output slot is not connected.

Examples of usage
-----------------

Default parameters:

.. image:: https://cloud.githubusercontent.com/assets/284644/5792200/20fcbe52-9f2e-11e4-8491-fb7182a019ba.png

Default parameters for triangluar grid:

.. image:: https://cloud.githubusercontent.com/assets/284644/5792199/20fbafb2-9f2e-11e4-8275-5c60013f9b9a.png

Main angle changed:

.. image:: https://cloud.githubusercontent.com/assets/284644/5792199/20fbafb2-9f2e-11e4-8275-5c60013f9b9a.png


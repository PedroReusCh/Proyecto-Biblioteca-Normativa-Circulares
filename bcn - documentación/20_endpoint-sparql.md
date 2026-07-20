# Endpoint SPARQL

> Acceso a la herramienta que permite realizar consultas sobre los grafos de la Biblioteca e información técnica sobre su uso.

Al igual que la mayoría de las iniciativas Linked Data, la Biblioteca del Congreso Nacional cuenta con un Endpoint SPARQL, herramienta que permite realizar consultas SPARQL sobre un grafo de entrada compuesto por tripletas RDF.

A nivel técnico, un Endpoint SPARQL implementa una interfaz descrita en la especificación SPROT de W3C que define una operación, un mensaje de entrada y dos mensajes de salida. El mensaje de entrada corresponde a la consulta SPARQL que se desea ejecutar, además del grafo (que es opcional) sobre el cual se ejecuta la consulta.

La operación permite ejecutar una consulta SPARQL sobre la lógica de aplicación en que existe el Endpoint. El primer mensaje de salida corresponde a los resultados obtenidos a partir de la consulta, lo cual se da en el caso de que no existan errores. El segundo mensaje de salida corresponde a mensajes de error en el caso de falla de la consulta (que puede estar causada por errores de sintaxis, semánticos, excepciones en tiempo de ejecución, u otros).

[**Acceder al Endpoint SPARQL**](https://datos.bcn.cl/sparql)

[Consultas SPARQL de Prueba](https://datos.bcn.cl/es/documentacion/consultas-sparql)

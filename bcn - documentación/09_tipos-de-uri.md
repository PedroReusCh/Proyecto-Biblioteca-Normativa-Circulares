# Tipos de URI

La siguiente tabla muestra los tipos de URI en la implementación.

| Tipo | Descripción |
| --- | --- |
| URIs de recurso | Son  URIs HTTP que definen la ubicación de un recurso, pero no su  representación en algún formato, y  sirven para referenciar recursos  entre sí.   En la siguiente URI de ejemplo se accede al recurso LEY 300,  pero no se describe a cuál de todas las representaciones se accederá.   La definición de la representación, estará dada por el mecanismo de  negociación de contenido. `http://datos.bcn.cl/recurso/cl/ley/330` |
| URIs de documento | Son URIs HTTP que apuntan directamente a un documento que describe un  recurso. Dicho de otra forma, son URIs a las representaciones de un  recurso, y es posible obtenerlas mediante negociación de contenido o  acceso directo.  En el siguiente ejemplo se se accede al recurso LEY 300  en formato RDF/XML. `http://datos.bcn.cl/recurso/cl/ley/330/datos.rdf` |
| URIs de ontología | Son  URIs que apuntan hacia recursos RDF que contienen ontologías escritas  en RDFS + OWL. Estas ontologías siempre son obtenidas en sintaxis  RDF/XML, sin embargo a futuro se podrá acceder mediante negociación de  contenido a diferentes representaciones. La siguiente URI corresponde a  una URI de ontología: `http://datos.bcn.cl/ontologies/bcn-norms#` |

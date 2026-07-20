# Conjunto de datos publicados

> Todos los conjuntos de datos (o datasets) abiertos y enlazables que encontrará disponibles en el servidor cuentan con una descripción sobre el Modelo de URI, Modelo de datos entregados y URIs de ejemplo.

Conjuntos de datos  BCN (o datasets) abiertos enlazables

[Dataset de Normas](https://datos.bcn.cl/es/documentacion/normas)

- Todas las normas jurídicas, sus atributos y medatatos, definidas en el portal de [Leychile](http://www.leychile.cl/) y actualizadas diariamente.
- Un gran conjunto de organismos de Estado emisores de normas.
- Países con los que se han firmado tratados internacionales.
- Organizaciones internacionales con las que se han firmado tratados.
- Algunas consultas REST, como por ejemplo, las normas emitidas por una organización cualquiera en un intervalo de fechas.

[Dataset de localidades](https://datos.bcn.cl/es/endpoint-sparql/index_html)

- Divisiones político administrativas y electorales de Chile.

Para obtener las URIs y nombres de las localidades registradas ingresa en [http://datos.bcn.cl/sparql .](https://datos.bcn.cl/sparql)Luego ejecutar las siguientes instrucciones de consulta:

select ?uri ?label

where {

?uri a  dbpedia-owl:Place.

?uri rdfs:label  ?label .

}

 [Dataset de Personas](https://datos.bcn.cl/es/endpoint-sparql/index_html)

- Reseñas de parlamentarios

- Cargos públicos

Para obtener las URIs y nombres de personas ingresa en [http://datos.bcn.cl/sparql .](https://datos.bcn.cl/sparql)Luego, ejecutar las siguientes instrucciones de consulta:

select ?uri ?label

where {

?uri a foaf:Person .

?uri foaf:name  ?label .

}

## **Conjuntos de datos sobre los cuales actualmente se está trabajando**

- [Biografías](https://datos.bcn.cl/es/ontologias/modelo-de-biografias): datos de  personas naturales y jurídicas relacionadas con el parlamento.

- [Congreso](https://datos.bcn.cl/es/ontologias/modelo-de-congreso): datos sobre  personas, documentos y procesos de funcionamiento del parlamento.

- [Reportes comunales:](https://datos.bcn.cl/es/ontologias/modelo-de-reportes-comunales)datos demográficos, sociales, educacionales, económicos, municipales y de seguridad ciudadana de cada comuna de Chile.

- [Recursos legislativos](https://datos.bcn.cl/es/ontologias/modelo-de-recursos-legislativos): recursos referenciables en el Congreso Nacional (tales como documentos y relaciones con actores)

- [Sesión parlamentaria](https://datos.bcn.cl/es/ontologias/modelo-de-sesion-parlamentaria): funcionamiento de cada sesión en Senado o Cámara de Diputados,  como a sus entidades relacionadas (personas, lugares, documentos y otros).

- [Transparencia:](https://datos.bcn.cl/es/ontologias/modelo-de-transparencia)jerarquías y relaciones laborales en el ámbito de la realidad de la Biblioteca.

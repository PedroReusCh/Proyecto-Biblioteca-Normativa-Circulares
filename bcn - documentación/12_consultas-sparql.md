# Consultas SparQL

> A continuación se presentan algunas consultas SPARQL que se pueden realizar en el Endpoint SPARQL.

## Consulta 1

Encontrar el id y título de 20 normas cualquiera (super clase de la ontología).

```text
PREFIX bcnnorms: <http://datos.bcn.cl/ontologies/bcn-norms#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT DISTINCT ?id ?title ?norma 
WHERE {
    ?norma dc:identifier ?id .
    ?norma dc:title ?title .
    ?norma a bcnnorms:Norm .
} 
LIMIT 20
```

[Ejecutar SPARQL](https://datos.bcn.cl/sparql?default-graph-uri=&query=PREFIX+bcnnorms%3A+%3Chttp%3A%2F%2Fdatos.bcn.cl%2Fontologies%2Fbcn-norms%23%3E%0D%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+dc%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Felements%2F1.1%2F%3E%0D%0A%0D%0ASELECT+DISTINCT+%3Fid+%3Ftitle+%3Fnorma+%0D%0AWHERE+%7B%0D%0A%09%3Fnorma+dc%3Aidentifier+%3Fid+.%0D%0A%09%3Fnorma+dc%3Atitle+%3Ftitle+.%0D%0A%09%3Fnorma+a+bcnnorms%3ANorm+.%0D%0A%7D+%0D%0ALIMIT+20&format=text%2Fhtml&timeout=0&debug=on)

### Consulta 2

Encontrar todos los tipos de norma que ha emitido el ministerio del interior  y decir cuántas normas ha emitido de cada tipo.

```text
SELECT DISTINCT ?nombreTipo ?nombreOrganizacion count(?norma) as ?cantidad 
WHERE {
    ?norma bcnnorms:type ?tipo.
    ?tipo bcnnorms:hasName ?nombreTipo.
    ?norma bcnnorms:createdBy ?ministerio.
    ?ministerio rdfs:label ?nombreOrganizacion .
    FILTER(?ministerio = )
} 
group by ?nombreTipo ?nombreOrganizacion 
ORDER BY ?cantidad
```

[Ejecutar SPARQL](https://datos.bcn.cl/sparql?default-graph-uri=&query=SELECT+DISTINCT+%3FnombreTipo+%3FnombreOrganizacion+count%28%3Fnorma%29+as+%3Fcantidad+%0D%0AWHERE+%7B%0D%0A++++%3Fnorma+bcnnorms%3Atype+%3Ftipo.%0D%0A++++%3Ftipo+bcnnorms%3AhasName+%3FnombreTipo.%0D%0A++++%3Fnorma+bcnnorms%3AcreatedBy+%3Fministerio.%0D%0A++++%3Fministerio+rdfs%3Alabel+%3FnombreOrganizacion+.%0D%0A++++FILTER%28%3Fministerio+%3D+%3Chttp%3A%2F%2Fdatos.bcn.cl%2Frecurso%2Fcl%2Forganismo%2Fministerio-del-interior%3E%29%0D%0A%7D+%0D%0Agroup+by+%3FnombreTipo+%3FnombreOrganizacion+%0D%0AORDER+BY+%3Fcantidad&format=text%2Fhtml&timeout=0&debug=on)

### Consulta 3

Consultar por el número total de normas generadas por cada municipalidad.

```text
SELECT DISTINCT ?nombre  count(?norma) as ?cantidad
WHERE {
    ?norma bcnnorms:createdBy ?organizacion.
    ?organizacion bcnnorms:hasName ?nombre.
    ?organizacion rdf:type bcnnorms:GovernmentalOrganization.
    FILTER regex(?nombre, "^MUNICIPALIDAD") 
}
ORDER BY DESC (?cantidad)
```

[Ejecutar SPARQL](https://datos.bcn.cl/sparql?default-graph-uri=&query=%0D%0A%0D%0ASELECT+DISTINCT+%3Fnombre++count%28%3Fnorma%29+as+%3Fcantidad%0D%0AWHERE+%7B%0D%0A++++%3Fnorma+bcnnorms%3AcreatedBy+%3Forganizacion.%0D%0A%09%3Forganizacion+bcnnorms%3AhasName+%3Fnombre.%0D%0A%09%3Forganizacion+rdf%3Atype+bcnnorms%3AGovernmentalOrganization.%0D%0A%09FILTER+regex%28%3Fnombre%2C+%22%5EMUNICIPALIDAD%22%29+%0D%0A%7D%0D%0AORDER+BY+DESC+%28%3Fcantidad%29&format=text%2Fhtml&timeout=0&debug=on)

### Consulta 4

Consultar por las palabras clave con que se han etiquetado las normas que son  tratados internacionales con España.

```text
define input:inference "inference_bcnnorms"




SELECT DISTINCT  ?palabraClave



WHERE {

?termino rdfs:label ?palabraClave.

?norma frbr:subject ?termino.

?norma bcnnorms:hasVersion ?tratado .

?tratado bcnnorms:isTreatyWith ?pais .

?pais a bcnnorms:Country.

?pais rdfs:label ?nombrePais.

FILTER regex("España",?nombrePais,"i").

}
```

[Ejecutar SPARQL](https://datos.bcn.cl/sparql?default-graph-uri=&query=define+input%3Ainference+%22inference_bcnnorms%22%0D%0A%0D%0ASELECT+DISTINCT++%3FpalabraClave%0D%0AWHERE+%7B%0D%0A++++%3Ftermino+rdfs%3Alabel+%3FpalabraClave.%0D%0A++++%3Fnorma+frbr%3Asubject+%3Ftermino+.%0D%0A++++%3Fnorma+bcnnorms%3AhasVersion+%3Ftratado+.%0D%0A++++%3Ftratado+bcnnorms%3AisTreatyWith+%3Fpais+.%0D%0A++++%3Fpais+a+bcnnorms%3ACountry.%0D%0A++++%3Fpais+rdfs%3Alabel+%3FnombrePais.%0D%0A++++FILTER+regex%28%22Espa%C3%B1a%22%2C%3FnombrePais%2C%22i%22%29.%0D%0A%7D+limit+10&format=text%2Fhtml&timeout=0&debug=on)

### Consulta 5

Obtener los presidentes de Chile y sus periodos de acuerdo a los datos publicados en nuestro dataset.

```text
SELECT DISTINCT ?persona str(?nombre) as ?nombre ?anioInicio ?anioFin 

WHERE {
 
    ?persona  bcnbio:hasPublicOffice ?periodoEnElCargo.
    ?persona  foaf:name ?nombre .
    ?periodoEnElCargo bcnbio:hasPosition ?cargo .
    ?cargo a bcnbio:PresidenteDeLaRepublica .
    ?periodoEnElCargo bcnbio:hasBeginning ?inicio .
    ?inicio time:year ?anioInicio  .
    ?periodoEnElCargo bcnbio:hasEnd ?fin .
    ?fin time:year ?anioFin .
 
}
 
ORDER BY DESC(?anioInicio )
```

[Ejecutar SPARQL](https://datos.bcn.cl/sparql?default-graph-uri=&query=SELECT+DISTINCT+%3Fpersona+str%28%3Fnombre%29+as+%3Fnombre+%3FanioInicio+%3FanioFin+%0D%0A%0D%0AWHERE+%7B%0D%0A+%0D%0A++++%3Fpersona++bcnbio%3AhasPublicOffice+%3FperiodoEnElCargo.%0D%0A++++%3Fpersona++foaf%3Aname+%3Fnombre+.%0D%0A++++%3FperiodoEnElCargo+bcnbio%3AhasPosition+%3Fcargo+.%0D%0A++++%3Fcargo+a+bcnbio%3APresidenteDeLaRepublica+.%0D%0A++++%3FperiodoEnElCargo+bcnbio%3AhasBeginning+%3Finicio+.%0D%0A++++%3Finicio+time%3Ayear+%3FanioInicio++.%0D%0A++++%3FperiodoEnElCargo+bcnbio%3AhasEnd+%3Ffin+.%0D%0A++++%3Ffin+time%3Ayear+%3FanioFin+.%0D%0A+%0D%0A%7D%0D%0A+%0D%0AORDER+BY+DESC%28%3FanioInicio+%29%0D%0A&format=text%2Fhtml&timeout=0&debug=on)

### Consulta 6

Obtener una lista de los partidos políticos registrados en nuestro dataset.

```text
SELECT DISTINCT ?partido ?nombre

WHERE {
 
    ?partido foaf:name ?nombre .
    ?partido a bcnbio:PoliticalParty .
 
}
ORDER BY ?nombre
```

[Ejecutar SPARQL](https://datos.bcn.cl/sparql?default-graph-uri=&query=SELECT+DISTINCT+%3Fpartido+%3Fnombre%0D%0A%0D%0AWHERE+%7B%0D%0A+%0D%0A++++%3Fpartido+foaf%3Aname+%3Fnombre+.%0D%0A++++%3Fpartido+a+bcnbio%3APoliticalParty+.%0D%0A+%0D%0A%7D%0D%0AORDER+BY+%3Fnombre%0D%0A+%0D%0A%0D%0A&format=text%2Fhtml&timeout=0&debug=on)

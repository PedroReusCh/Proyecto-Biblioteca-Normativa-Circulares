# URIs del dataset

Para el uso de los patrones de URI aquí presentados, se debe anteponer la siguiente dirección que contiene los grafos rdf:

```text
http://datos.bcn.cl/recurso/
```

Para obtener las representaciones en los distintos formatos,  se debe añadir al final de la URI de recurso el siguiente fragmento:

```text
datos.{ext}
```

En donde {ext} representa alguno de los formatos de representación disponibles en la sección [manifestaciones](https://datos.bcn.cl/es/documentacion/manifestaciones/).

## 1) Obtener una norma

cl/{tipo}/{org}/{fecha_publicacion}/{numero}

Este patrón permite acceder a una norma raíz que indica todas las  referencias a versiones de una norma específica. En él se describen los  siguientes elementos variables:

- **{tipo}:** indica el tipo de la norma el cual será  definido mediante una abreviación. Como ejemplo algunos tipos de norma  son: Ley (LEY), Decreto (DTO) y Ordenanza (ORZ)
- **{org}:** indica el nombre del organismo emisor.
- **{fecha_publicacion}:** indica la fecha de publicación de la norma.
- **{numero}:** indica el número de la norma a la que se hace referencia.

Un ejemplo del RDF generado por este patrón de URI es el siguiente:

```text
<http://uri_a_norma1/> rdf:type
bcn-norms:RootNorm; bcn-norms:type <http://uri_al_tipo>;
dc:title "norma 1";
bcn-norms:publishDate "1982-10-17";
bcn-norms:hasNumber "11111";
bcn-norms:hasVersion <http://uri_a_version_1_norma1>;
bcn-norms:hasVersion <http://uri_a_version_2_norma1>;
...
bcn-norms:hasVersion <http://uri_a_version_n_norma1> .
<http://uri_a_version1_norma1> bcn-norms:isLatestVersion "true" .
```

### Ejemplos de uso

- [http://datos.bcn.cl/recurso/cl/ley/ministerio-del-interior/2005-02-16/20000](https://datos.bcn.cl/recurso/cl/ley/ministerio-del-interior/2005-02-16/20000)
- [http://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/1994-10-26/59](https://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/1994-10-26/59)

### Ejemplos de uso con vinculaciones

- [http://datos.bcn.cl/recurso/cl/ley/ministerio-del-interior/2005-02-16/20000/modificada-por](https://datos.bcn.cl/recurso/cl/ley/ministerio-del-interior/2005-02-16/20000/modificada-por)
- [http://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/1994-10-26/59/modificada-por](https://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/1994-10-26/59/modificada-por)

## 2) Normas por tipo y organismo creador

cl/{tipo}/{org}*

Este patrón permite consultar por todas las normas que cumplan el tipo y el organismo determinado por las variables.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago](https://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago)
- [http://datos.bcn.cl/recurso/cl/dto/ministerio-de-salud](https://datos.bcn.cl/recurso/cl/dto/ministerio-de-salud)

Ejemplos de uso con vinculaciones:

- [http://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/publicada-entre/1990-01-02-y-2000-12-23/limite/5](https://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/publicada-entre/1990-01-01-y-2000-12-23/limite/5)
- [http://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/publicada-entre/1990-01-02-y-2000-12-23](https://datos.bcn.cl/recurso/cl/orz/municipalidad-de-santiago/publicada-entre/1900-01-01-y-2000-12-23)

## 3) Acceder a la versión específica de una norma

cl/{tipo}/{org}/{fecha-pub}/{numero}/{lang}@{fecha-version} **

Este patrón permite acceder a una norma con versión.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/dto/ministerio-de-educacion/2004-09-21/173/es@2009-11-19](https://datos.bcn.cl/recurso/cl/dto/ministerio-de-educacion/2004-09-21/173/es@2009-11-19)
- [http://datos.bcn.cl/recurso/cl/dto/ministerio-de-educacion/2008-11-07/341/es@2008-11-07](https://datos.bcn.cl/recurso/cl/dto/ministerio-de-educacion/2008-11-07/341/es@2008-11-07)

Ejemplos de uso con vinculaciones:

- [http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-justicia/1995-10-18/1/refunde-a](https://datos.bcn.cl/recurso/cl/dfl/ministerio-de-justicia/1995-10-18/1/refunde-a)
- [http://datos.bcn.cl/recurso/cl/rec/ministerio-de-energia/2010-05-07/128/rectifica-a](https://datos.bcn.cl/recurso/cl/rec/ministerio-de-energia/2010-05-07/128/rectifica-a)

## 4) Obtener todos los tipos de norma

cl/norma/tipo#{nombre}

Permite acceder a los tipos de norma tales como Ley, Decreto, Ordenanza etc. y sus a sus metadatos.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/norma/tipo#ley](https://datos.bcn.cl/recurso/cl/norma/tipo#ley)
- [http://datos.bcn.cl/recurso/cl/norma/tipo#dto](https://datos.bcn.cl/recurso/cl/norma/tipo#dto)

## 5) Listado con organismos públicos que han generado normas

cl/organismo

Permite acceder a los organismos de gobierno y a sus metadatos.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/organismo](https://datos.bcn.cl/recurso/cl/organismo)

## 6) Información de un organismo específico

cl/organismo/{nombre}

Permite acceder a un organismo de gobierno específico.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/organismo/ministerio-de-salud](https://datos.bcn.cl/recurso/cl/organismo/ministerio-de-salud)
- [http://datos.bcn.cl/recurso/cl/organismo/municipalidad-de-valparaiso](https://datos.bcn.cl/recurso/cl/organismo/municipalidad-de-valparaiso)

## 7) Obtener las clasificaciones de normas

cl/norma/clasificacion

Permite acceder a las clasificaciones de normas.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/norma/clasificacion](https://datos.bcn.cl/recurso/cl/norma/clasificacion)

## 8) Todos los valores para una clasificación

cl/norma/clasificacion/{nombre-clasificacion}

Permite acceder a los valores de un tipo de clasificación.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/palabra-clave](https://datos.bcn.cl/recurso/cl/norma/clasificacion/palabra-clave)
- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo](https://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo)
- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo-internacional](https://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo-internacional)
- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/tratado-por-pais](https://datos.bcn.cl/recurso/cl/norma/clasificacion/tratado-por-pais)

## 9) Obtener las normas que estén clasificadas por un valor de clasificación

cl/norma/clasificacion/{nombre-clasificacion}/{valor-clasificacion}

Permite acceder a las normas clasificadas por un valor de clasificación dado.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/palabra-clave/cobre](https://datos.bcn.cl/recurso/cl/norma/clasificacion/palabra-clave/cobre)
- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo/ministerio-de-educacion](https://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo/ministerio-de-educacion)
- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo-internacional/banco-mundial](https://datos.bcn.cl/recurso/cl/norma/clasificacion/organismo-internacional/banco-mundial)
- [http://datos.bcn.cl/recurso/cl/norma/clasificacion/tratado-por-pais/peru](https://datos.bcn.cl/recurso/cl/norma/clasificacion/tratado-por-pais/peru)

## 10) Todos los organismos internacionales relacionados con normas

organismo

Permite acceder al listado de organismos internacionales.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/organismo](https://datos.bcn.cl/recurso/organismo)

## 11) Obtener información sobre un organismo internacional específico

organismo/{nombre}

Permite acceder al listado de organismos internacionales.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/organismo/mercosur](https://datos.bcn.cl/recurso/organismo/mercosur)
- [http://datos.bcn.cl/recurso/organismo/naciones-unidas](https://datos.bcn.cl/recurso/organismo/naciones-unidas)

## 12) Todos los países que tienen tratado internacional con Chile

pais

Permite acceder al listado de paises con los que se tiene tratado.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/pais](https://datos.bcn.cl/recurso/pais)

## 13) La descripción de un país específico

pais/{nombre}

Permite acceder a la descripción de un país con el que se tiene tratado.

Ejemplos de uso:

- [http://datos.bcn.cl/recurso/pais/brasil](https://datos.bcn.cl/recurso/pais/brasil)
- [http://datos.bcn.cl/recurso/pais/alemania](https://datos.bcn.cl/recurso/pais/alemania)

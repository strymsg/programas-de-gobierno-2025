# Clasificación de planes de gobierno

Con el uso de *LLM* se han evaluado los planes de gobierno para ver que tan alineados están con una lista de [afirmaciones](afirmaciones1_rg.md).

## Ejecución clasificación usando LLM (RAG + modelo de razonamiento)

El [notebook](notebooks/Rag_chromaDb_reasoning_using_api.ipynb) produce varios [resultados en notebooks/data](notebooks/data/) como archivos en formato json.

### Otros experimentos

Los resultados de la evaluación están dentro la carpeta [data](data/prueba_2) ejecutando el archivo `clasificacion-deepseek-reasoning.py` que usa el modelo [deepseek-reasoning](https://api-docs.deepseek.com/guides/reasoning_model) mediante API.

#### Ejecutar

Si quieres ejecutarlo y obtener tus propios resultados debes:

1. Clonar este proyecto
2. Ubicar una terminal en la carpeta del proyecto
3. Crear un entorno virtual con `pipenv shell`
4. Instalar dependencias `pipenv install`
5. Definir la variable de entorno `OPENAPI_API_KEY` con el token API que tengas para deepseek.
6. Ejecutar con `python clasificacion-deepseek-reasoning.py` (tarda varios minutos)
7. Revisar la carpeta `data/` donde se guardan los resultados en texto plano y json.

Este proyecto usa [los planes de gobierno obtenidos por Mauricio Foronda](https://github.com/mauforonda/programas-de-gobierno-2025).

# Planes de gobierno
## [Morena](programas/morena.md)

- Eva Copa

## [Alianza Libertad y Democracia](programas/alianza-libertad-y-democracia.md)

- Jorge Quiroga

## [Alianza Popular](programas/alianza-popular.md)

- Andrónico Rodríguez

## [Alianza Unidad](programas/alianza-unidad.md)

- Samuel Doria Medina

## [Nueva Generación Patriótica](programas/nueva-generacion-patriotica.md)

- Jaime Dunn

## [MAS-IPSP](programas/mas-ipsp.md)
v
- Eduardo del Castillo

## [APB Súmate](programas/apb-sumate.md)

- Manfred Reyes Villa

## [Libertad y Progreso](programas/libertad-y-progreso-adn.md)

- Paulo Folster

## [Partido Demócrata Cristiano](programas/partido-democrata-cristiano.md)

- Rodrigo Paz

## [Alianza La Fuerza del Pueblo](programas/alianza-la-fuerza-del-pueblo.md)

- Jhonny Fernández


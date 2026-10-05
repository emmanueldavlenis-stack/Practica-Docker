# Explicación y justificación del proyecto
 
## ¿Qué se construyó?
 
Una API de usuarios hecha con FastAPI y PostgreSQL, que expone métricas de su comportamiento. Esas métricas las recoge Prometheus y se muestran en dashboards de Grafana. Todo corre en contenedores Docker.
 
## Primera parte: construcción manual
 
En la primera parte del curso el objetivo era hacer el proceso a mano: escribir el `Dockerfile`, construir la imagen y levantar cada contenedor con `docker run`. Más que aprender una herramienta, el propósito era reforzar lo visto en clase y entender cómo se pone a correr un contenedor, qué pasa por debajo y cómo se conectan las piezas entre sí.
 
## Segunda parte: Docker Compose y buenas prácticas
 
En la segunda parte se usó Docker Compose para automatizar el mismo proceso que antes se hizo a mano, aplicando mejores prácticas. Un solo archivo describe todo el sistema y un solo comando lo levanta:
 
```bash
docker compose up -d --build
```
 
### Decisiones y su justificación
 
| Decisión | Justificación |
|---|---|
| **Redes (`networks`) en lugar de `--link`** | `--link` se queda cada vez más obsoleto y es difícil de escalar. Las redes definidas por el usuario resuelven los nombres de los servicios automáticamente y son la forma recomendada de comunicar contenedores. |
| **Dos redes: `backend` y `analisis`** | Aísla la base de datos. Prometheus y Grafana no tienen acceso a PostgreSQL; solo la API está en ambas redes y hace de puente. |
| **`healthcheck` y `depends_on` con `service_healthy`** | La API espera a que PostgreSQL esté realmente listo, no solo iniciado. Resuelve el error de conexión rechazada que ocurría en el arranque manual. |
| **Volúmenes (`pgdata`, `grafana_data`)** | Los datos de la base de datos y de Grafana sobreviven si se recrean los contenedores. |
| **Nombre del servicio como host** | La URL de la base de datos usa `postgres` y Prometheus apunta a `fastapi:8000`. Docker resuelve esos nombres, así que no se manejan IPs a mano. |
| **Versiones fijas en `requirements.txt`** | Hace la construcción reproducible: la imagen se comporta igual en cualquier máquina. |
| **Driver explícito (`postgresql+psycopg2://`)** | Evita que la conexión dependa de la versión de SQLAlchemy. |
 
## Monitoreo: Prometheus y Grafana
 
Además del CRUD, se añadió observabilidad:
 
1. **La API expone `/metrics`** con una métrica propia (`user_created_total`, que cuenta usuarios creados) y las métricas por defecto del proceso: memoria, CPU, archivos abiertos y tiempo de funcionamiento.
2. **Prometheus** consulta ese endpoint cada 5 segundos y guarda los datos como series de tiempo. Funciona por *pull*: es Prometheus quien va a buscar los datos, el servicio no los envía.
3. **Grafana** usa Prometheus como fuente de datos y presenta la información en dashboards, para ver de un vistazo cuántos usuarios se han creado, cuánta RAM y CPU usa la API, cuántos archivos tiene abiertos y cuánto tiempo lleva funcionando.
Los dashboards se exportaron como JSON y se guardaron en el proyecto, de modo que la configuración queda versionada y se puede reproducir.
 
## Qué aprendí
 
- **Prometheus:** es una herramienta de monitoreo que recolecta métricas de las aplicaciones y las guarda como series de tiempo. Aprendí que funciona por *pull*: Prometheus va a buscar los datos al endpoint `/metrics` de la API cada cierto tiempo, y que se le indica qué servicios consultar con un archivo de configuración.
- **Grafana:** es una herramienta de visualización que toma los datos de Prometheus y los presenta en dashboards con gráficas y paneles. Sirve para entender de un vistazo cómo se comporta una aplicación y detectar problemas, y los dashboards se pueden exportar como JSON para guardarlos y reproducirlos.
- **Docker Compose:** comprendí mejor para qué sirve y cómo funciona. Es una herramienta que permite describir en un solo archivo todos los servicios de una aplicación (imágenes, redes, volúmenes, variables de entorno y orden de arranque) y levantarlos con un solo comando. Es lo mismo que se hizo a mano con `docker run`, pero de forma declarativa, ordenada y reproducible.
## Conclusión
 
Hacer primero el proceso manual permitió entender qué automatiza Docker Compose y por qué: redes, volúmenes, variables de entorno y orden de arranque son piezas que se configuran a mano en `docker run`, y Compose las reúne en un archivo declarativo y reproducible. Añadir Prometheus y Grafana mostró que desplegar una aplicación no termina cuando arranca: también hay que poder observar su comportamiento. El resultado es un sistema completo que se levanta con un solo comando y cuyo funcionamiento se puede medir y visualizar.

# CI/CD Pipeline Demo

Proyecto de portfolio enfocado **exclusivamente en diseño de pipelines
de CI/CD** con GitHub Actions. La app incluida (`app.py`) es
intencionalmente trivial — un solo endpoint `/health` — porque el
protagonista de este repo es el pipeline en sí, no la lógica de negocio.

## Qué automatiza el pipeline

El archivo `.github/workflows/pipeline.yml` encadena 5 etapas:

```
push a main / PR
      │
      ▼
   [1. Lint] ──falla──► corta acá, no gasta más tiempo de CI
      │ ok
      ▼
   [2. Tests] (matrix: Python 3.11 y 3.12 en paralelo)
      │ ok
      ▼
   [3. Build & Push] ──► solo si es push a main (no en PRs)
      │                   publica imagen en Docker Hub:
      │                   - tag :latest
      │                   - tag :<sha-del-commit>  (trazabilidad)
      ▼
   [5. Deploy a staging] ──► requiere el Environment "staging"
                              (se puede configurar aprobación manual)

push de un tag "v*" (ej: v1.2.0)
      │
      ▼
   [2. Tests] ──ok──► [4. Release]
                        - publica imagen con tag :v1.2.0
                        - crea un Release en GitHub automáticamente
```

## Por qué cada decisión de diseño

- **Lint antes que tests**: si el código tiene un error de sintaxis,
  no tiene sentido gastar minutos de CI corriendo toda la suite de
  tests en dos versiones de Python.
- **`needs:`** entre jobs: expresa dependencias explícitas. El build
  de la imagen no arranca si los tests no pasaron antes.
- **Build & Push solo en `push` a `main`, nunca en PRs**: evita
  publicar imágenes de código que todavía no fue revisado ni
  mergeado.
- **Dos tags en cada imagen** (`latest` + SHA del commit): `latest`
  es cómodo para probar rápido, pero en un incidente real necesitás
  saber *exactamente* qué código generó la imagen que está corriendo
  — para eso sirve el tag con el SHA.
- **Job de `release` separado, disparado por tags de git**: separa el
  concepto de "esto pasó CI" de "esto es una versión oficial
  publicada". Permite tener control manual de cuándo se corta una
  versión (con `git tag v1.2.0 && git push --tags`), en vez de que
  cada push a main sea automáticamente una "versión".
- **`environment: staging` en el deploy**: los *Environments* de
  GitHub permiten exigir aprobación manual de una persona antes de
  que el job corra — así se modela, sin necesitar infraestructura
  real, cómo un pipeline real frena antes de tocar producción.

## Cómo configurarlo en tu propio fork

Este pipeline necesita dos *secrets* configurados en
**Settings → Secrets and variables → Actions** del repo:

| Nombre | Qué es |
|---|---|
| `DOCKERHUB_USERNAME` | Tu usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Un [access token](https://hub.docker.com/settings/security) de Docker Hub (no tu contraseña) |

Y una *variable* (no secret, es pública) en la misma sección, pestaña
"Variables":

| Nombre | Valor |
|---|---|
| `DOCKERHUB_USERNAME` | Tu usuario de Docker Hub (para armar el nombre de la imagen) |

También conviene crear el Environment `staging` en
**Settings → Environments**, aunque sea sin reglas de protección, para
que el job de deploy tenga dónde apuntar.

## Probarlo localmente (antes de confiar en el pipeline)

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v

pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

docker build -t cicd-pipeline-demo .
docker run --rm -p 5000:5000 cicd-pipeline-demo
```

## Estructura

```
cicd-pipeline-demo/
├── app.py
├── requirements.txt
├── Dockerfile
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        └── pipeline.yml
```

# Actividad — Semana 12: Integración Continua con GitHub Actions

**Objetivo:** poner en marcha el pipeline que ya trae el proyecto, entender cada línea, y comprobar que ejecuta los 59 tests con PostgreSQL real y que una regla impide fusionar a `main` si falla.

**Tiempo estimado:** 60 a 75 minutos.

## Antes de empezar

Necesitas: cuenta de GitHub, Git, Docker Desktop, `uv` y Python 3.14 (lo instala `uv`).

El repositorio trae el workflow listo en `.github/workflows/ci.yml`. **No lo escribes: lo lees, lo ejecutas y lo pones a prueba.** Todo el trabajo se hace en **tu propio repositorio**, creado a partir de la plantilla del curso. Las reglas de rama y los secrets se crean en un repositorio que sea tuyo.
 
## Preparación test

1. En GitHub, abre `DrSolonius/CD_CI_sistema_academico` y pulsa **Use this template**, luego **Create a new repository**. Ponle el nombre que quieras, déjalo **Public** y créalo en tu cuenta.
2. Clona **tu repositorio** (cambia `TU_USUARIO` y, si lo cambiaste, el nombre):

```bash
git clone https://github.com/TU_USUARIO/CD_CI_sistema_academico.git
cd CD_CI_sistema_academico
```

3. Comprueba que los tests pasan en tu computador:

```bash
cp .env.example .env             # ya trae valores de práctica para los tests
docker compose up -d db          # PostgreSQL; crea también la base clase_test
uv sync --group dev
uv run pytest
```

Debes ver `59 passed`. Si ves `Faltan variables para la base de pruebas`, falta alguna línea `TEST_DB_*` en tu `.env`. Para levantar la API (no para los tests) completa además `JWT_SECRET` y `ADMIN_PASSWORD`.

---

## Parte 1 — Leer el workflow

Abre `.github/workflows/ci.yml` y responde, mirando el archivo:

- ¿Qué eventos lo disparan?
- ¿Qué hace el bloque `services`? ¿Para qué sirve el `--health-cmd`?
- ¿De dónde sale la contraseña de la base?
- ¿Cuáles son los cuatro pasos (`steps`) y qué hace cada uno?
- ¿Qué cambia el `permissions: contents: read`?

**Pregunta 1:** ¿por qué la base de datos de CI se declara dentro del workflow y no usa tu `docker-compose.yml`?

## Parte 2 — Ejecutarlo: primero rojo, después verde

1. Crea una rama, haz un cambio mínimo (por ejemplo, una línea en `README.md`) y abre un pull request hacia `main` **de tu repositorio**:

```bash
git switch -c mi-prueba
# edita README.md
git add -A
git commit -m "prueba: primer pull request"
git push -u origin mi-prueba
```

> Abre el PR desde el enlace que muestra `git push`, o desde la pestaña *Pull requests*. Comprueba que *base* sea `main` de **tu** repositorio.

2. Abre el check `tests` del PR, en la pestaña **Checks** o en **Actions**.

**Qué debes observar:** el check termina en **rojo** y el job se detiene al iniciar la base de datos, antes de llegar a los tests. Abre el paso que falló y lee el mensaje.

3. **Crea el secret.** En tu repositorio: *Settings, Secrets and variables, Actions, New repository secret*. Nombre: `TEST_DB_PASSWORD` (exactamente ese). Valor: la contraseña que quieras, porque la base de CI es desechable.
4. Vuelve al PR, entra a la ejecución fallida y pulsa **Re-run all jobs**.

**Qué debes observar:** el check `tests` en **verde** y `59 passed` en el log.

**Pregunta 2:** ¿qué faltaba en el primer intento? ¿Por qué el secret no está escrito en el archivo del workflow?

## Parte 3 — Cobertura como compuerta

1. Abre el log del paso `uv run pytest --cov` y busca la tabla de cobertura y la línea `Required test coverage of 85.0% reached`.
2. El umbral está en `pyproject.toml` (`fail_under = 85`). En tu computador, comprueba qué pasa si la cobertura baja: comenta temporalmente uno de los tests de `tests/unit/test_estudiante.py` y corre `uv run pytest --cov`.

**Pregunta 3:** ¿qué ocurre al bajar de 85 %? Restaura el test al terminar.

## Parte 4 — Proteger `main`

En tu repositorio: *Settings, Branches, Add branch protection rule* (o *Add classic branch protection rule*), con la rama `main`:

- Activa **Require a pull request before merging**.
- Activa **Require status checks to pass before merging**, y en el buscador elige **`tests`**.

> El check aparece en la lista solo si ya se ejecutó al menos una vez (Parte 2).
> La regla exige el job por su nombre: si lo renombras en el YAML, deja de aplicar.
> Las reglas de rama están disponibles en repositorios públicos con cuenta gratuita.

**Qué debes observar:** en tu PR con el check verde, el botón de merge está habilitado.

## Parte 5 — Caché y medición

El workflow ya activa el caché con `enable-cache: true` en el paso de `setup-uv`.

1. Anota el tiempo total de la primera ejecución verde (pestaña Actions).
2. Pulsa **Re-run all jobs** en esa ejecución y anota el tiempo de la segunda.
3. Compara el tiempo del paso `Run astral-sh/setup-uv` y el de `uv sync` en las dos ejecuciones.

**Qué debes observar:** en la segunda ejecución el paso de instalación de dependencias tarda menos, porque reutiliza el caché.

**Pregunta 4:** ¿cuánto ahorró el caché? ¿Qué cambio haría que se descarte? (Pista: `uv.lock`.)

## Parte 6 — Romper un test a propósito

1. Crea una rama y cambia un `assert` para que falle. Por ejemplo, en `tests/unit/test_estudiante.py`, un valor esperado distinto del real.
2. Haz commit, push y abre un PR hacia `main` de tu repositorio.

```bash
git switch -c romper-test
# edita el test
git add -A
git commit -m "prueba: test roto a propósito"
git push -u origin romper-test
```

**Qué debes observar:** el check `tests` en **rojo**, el log indica qué test falló y **el botón de merge está bloqueado**.

3. Corrige el test y haz push. El check vuelve a verde y el merge se habilita.

**Pregunta 5:** ¿qué habría pasado sin la regla de la Parte 4? ¿Y sin el pipeline?

## Parte 7 (opcional) — Modifica el workflow

Esta es la única parte en la que editas el `ci.yml`. Agrega un paso que guarde el reporte de cobertura para descargarlo desde la ejecución:

1. Cambia el paso de pytest por `uv run pytest --cov --cov-report=html`.
2. Agrega, después de ese paso:

```yaml
      - uses: actions/upload-artifact@v7
        if: always()
        with:
          name: cobertura
          path: htmlcov/
```

3. Haz push y, en la ejecución, busca la sección **Artifacts** y descarga `cobertura`.

**Pregunta 6:** ¿para qué sirve `if: always()`?

---

## Entregable

1. Enlace al pull request de la Parte 2, con el check `tests` en verde.
2. Captura del pull request de la Parte 6 con el check en rojo y el merge bloqueado.
3. Los dos tiempos de la Parte 5.
4. Respuestas breves (máx. 5 líneas cada una) a las preguntas 1 a 5.

## Criterio de logro

- El workflow ejecuta los 59 tests con PostgreSQL y termina en verde.
- La contraseña de la base no aparece escrita en ningún archivo del repositorio.
- `main` no se puede fusionar con el check en rojo.

## Errores frecuentes

| Síntoma | Causa probable |
|---|---|
| El check falla al iniciar la base, sin llegar a los tests | El secret `TEST_DB_PASSWORD` no existe o está mal escrito. |
| El PR no muestra ningún check | El workflow solo corre en pull requests y en push a `main`; comprueba que el PR sea hacia `main`. |
| `Faltan variables para la base de pruebas` en CI | Falta alguna variable `TEST_DB_*` en el bloque `env` del job. |
| El check `tests` no aparece al crear la regla | El workflow todavía no se ejecutó, o el job tiene otro nombre. |
| `connection refused` en los tests | El puerto del `service` no coincide con `TEST_DB_PORT` (ambos 5432). |
| Error de YAML al editar el workflow (Parte 7) | Indentación: el YAML usa 2 espacios y no acepta tabulaciones. |

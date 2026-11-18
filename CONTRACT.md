# CONTRACT.md — Acuerdos del equipo

Este documento fija las interfaces entre las partes del proyecto y la forma de trabajar.
**Si algo de aquí cambia, se cambia primero en este fichero (por PR) y después en el código.**

---

## 1. Reparto

| Persona | Responsabilidades |
|---|---|
| **Diego** | Parser del config, `MazeGenerator` (algoritmos, modo perfect, modo Pac-Man, patrón "42"), camino más corto |
| **Carlos** | `a_maze_ing.py`, renderer ASCII, menú e interacciones, writer del fichero de salida, Makefile, packaging (`pyproject.toml` + build del `.whl`) |
| **Juntos** | README.md, LICENSE.md, tests, bonus, revisión cruzada |

---

## 2. Estructura del repo

```
a-maze-ing/
├── a_maze_ing.py          # Carlos · punto de entrada
├── config.txt             # config por defecto
├── Makefile               # Carlos
├── pyproject.toml         # Carlos · construye SOLO el paquete mazegen
├── requirements-dev.txt   # flake8, mypy, build, pytest
├── README.md
├── LICENSE.md
├── CONTRACT.md
├── .gitignore
├── mazegen-x.y.z-py3-none-any.whl   # se genera al final
│
├── mazegen/               # paquete reutilizable
│   ├── __init__.py        # exporta MazeGenerator
│   ├── generator.py       # clase MazeGenerator
│   └── README.md          # doc del módulo (va dentro del paquete)
│
├── maze_app/              # parte NO reutilizable
│   ├── __init__.py
│   ├── config_parser.py   # Diego
│   ├── output_writer.py   # Carlos
│   ├── renderer.py        # Carlos
│   └── menu.py            # Carlos
│
├── tests/
└── tools/
    └── maze_analyzer.py   # excluido de flake8/mypy
```

**Regla de dependencias:** `maze_app` puede importar `mazegen`. `mazegen` **nunca** importa nada de `maze_app`.

---

## 3. Herramientas y normas

- Python ≥ 3.10 *(versión exacta: pendiente, ver §9)*
- Dependencias: **pip + venv**, herramientas de desarrollo en `requirements-dev.txt`
- Linters: **flake8** + **mypy** (`make lint` debe pasar siempre)
- Docstrings: **estilo Google**
- Type hints en todas las funciones, parámetros y retornos
- Visualización: **ASCII** en terminal
- Código, nombres y commits en **inglés**

---

## 4. Contrato del parser

**Fichero:** `maze_app/config_parser.py`
**Responsable:** [login tuyo]
**Lo usa:** `a_maze_ing.py` (Carlo)

### Qué devuelve

Una dataclass inmutable con los valores **ya convertidos y validados**:

```python
@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]     # (x, y)
    exit: tuple[int, int]      # (x, y)
    output_file: str
    perfect: bool
    seed: int | None = None    # clave opcional SEED; None = aleatorio
```

| Campo | Clave en el config | Obligatoria | Ejemplo en el fichero | Valor en Python |
|---|---|---|---|---|
| `width` | `WIDTH` | Sí | `WIDTH=20` | `20` |
| `height` | `HEIGHT` | Sí | `HEIGHT=15` | `15` |
| `entry` | `ENTRY` | Sí | `ENTRY=0,0` | `(0, 0)` |
| `exit` | `EXIT` | Sí | `EXIT=19,14` | `(19, 14)` |
| `output_file` | `OUTPUT_FILE` | Sí | `OUTPUT_FILE=maze.txt` | `"maze.txt"` |
| `perfect` | `PERFECT` | Sí | `PERFECT=True` | `True` |
| `seed` | `SEED` | No | `SEED=42` | `42` / `None` |

### Errores

- Cualquier problema lanza **`ConfigError`** (excepción propia, definida en `config_parser.py`) con un mensaje claro en inglés.
- Casos que cubre: fichero inexistente o ilegible, línea sin `=`, clave obligatoria ausente, clave duplicada, valor con tipo incorrecto, tamaño no positivo, `ENTRY`/`EXIT` fuera de los límites, `ENTRY == EXIT`.
- Las líneas que empiezan por `#` y las líneas vacías se ignoran.
- **El parser nunca hace `print` ni `exit`.** `a_maze_ing.py` captura `ConfigError`, imprime el mensaje y termina con código de error.

---

## 5. Contrato de `MazeGenerator`

**Fichero:** `mazegen/generator.py`
**Responsable:** Diego
**Lo usan:** `a_maze_ing.py`, `renderer.py`, `output_writer.py`, `menu.py` (Carlos)

### Uso

```python
gen = MazeGenerator(width, height, entry, exit, perfect, seed)
gen.generate()
```

- El constructor solo guarda los parámetros y los valida (lanza `ValueError` si son inválidos, porque el módulo es reutilizable y no puede fiarse de quien lo llama).
- `generate()` construye el laberinto y calcula el camino más corto.
- Los atributos de abajo **solo son válidos después de llamar a `generate()`**.
- **Regenerar:** el menú crea un `MazeGenerator` nuevo con otra seed y llama a `generate()`.

### Qué expone

| Atributo | Tipo | Significado |
|---|---|---|
| `width` | `int` | Número de columnas |
| `height` | `int` | Número de filas |
| `grid` | `list[list[int]]` | Lista de filas; cada celda es un `int` de 0 a 15 (bits de muros, ver §6) |
| `entry` | `tuple[int, int]` | Entrada `(x, y)` |
| `exit` | `tuple[int, int]` | Salida `(x, y)` |
| `path` | `str` | Camino más corto de entrada a salida, letras `N` `E` `S` `W` |
| `pattern_cells` | `set[tuple[int, int]]` | Celdas `(x, y)` del patrón "42"; **vacío si no cabe** |

### Patrón "42" que no cabe

El generador no imprime nada. Si `pattern_cells` está vacío, **`a_maze_ing.py` imprime el aviso** por consola.

---

## 6. Convenciones del laberinto (LEER DOS VECES)

### Coordenadas

- Una coordenada es siempre **`(x, y)`**: `x` = columna, `y` = fila.
- **LA CELDA DE LA COORDENADA (x, y) ES `grid[y][x]`. NUNCA `grid[x][y]`.**
- **`y = 0` ES LA FILA DE ARRIBA.** `y` crece hacia abajo.

### Direcciones

| Dirección | Movimiento |
|---|---|
| `N` (Norte, arriba) | `y - 1` |
| `E` (Este, derecha) | `x + 1` |
| `S` (Sur, abajo) | `y + 1` |
| `W` (Oeste, izquierda) | `x - 1` |

### Bits de muros (iguales en `grid` y en el fichero)

| Bit | Valor | Muro |
|---|---|---|
| 0 | 1 | Norte |
| 1 | 2 | Este |
| 2 | 4 | Sur |
| 3 | 8 | Oeste |

Bit a 1 = muro cerrado. Ejemplos: `9` = Norte + Oeste, `5` = Norte + Sur, `15` (`f`) = celda totalmente cerrada.

**Coherencia:** si una celda tiene muro al Este, su vecina de la derecha tiene muro al Oeste (y lo mismo para Norte/Sur).

### Pruebas

Probar siempre también con laberintos **no cuadrados** (p. ej. 20×15): los errores de `x`/`y` no se ven en laberintos cuadrados.

---

## 7. Formato del fichero de salida

**Responsable:** Carlo (`output_writer.py`). Usa solo lo que expone `MazeGenerator` (§5).

```
<fila 0: un dígito hex por celda>
<fila 1>
...
<fila height-1>
                      ← línea vacía
<entry x>,<entry y>
<exit x>,<exit y>
<path en letras NESW>
```

- Un carácter hexadecimal por celda, una fila por línea.
- Todas las líneas terminan en `\n`.
- Se valida con `tools/maze_analyzer.py`.

---

## 8. Forma de trabajar

- **Ramas:** `feat/nombre-corto`, `fix/nombre-corto`. Nadie hace push directo a `main`.
- **Commits:** cortos, en inglés, con prefijo: `feat: parse ENTRY and EXIT`, `fix: wrong east border wall`.
- **Pull requests:** siempre los revisa el otro. Si no entiendes algo, se pregunta antes de aprobar.
- **Terminado =** pasa `make lint` + tiene docstrings y type hints + revisado por el otro + no rompe `maze_analyzer.py`.
- **Sincronización:** 10 minutos cada dos días (qué hice, qué voy a hacer, en qué estoy bloqueado).
- **README:** apuntar sobre la marcha la planificación, los cambios de plan y el uso de IA (lo pide el enunciado).

---

## 9. Pendiente de decidir

- [ ] `make lint` o `make lint-strict` como estándar (recomendado: `lint-strict`)
- [ ] Versión exacta de Python (comprobar la de los ordenadores del campus)
- [ ] Fecha del primer hito: parser + modo perfect + render básico integrados
- [ ] Licencia para LICENSE.md
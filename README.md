# Copenhague 2026 — guía del puente de diciembre

Web estática de una sola página, para **Alicia y Luis**, que van a Copenhague del **viernes 4 al
martes 8 de diciembre de 2026**. Como la de Londres y la de Lyon, **no lleva día a día**: va por zonas,
y cada zona trae lo que ver, **dónde comer allí mismo** y **las tiendas curiosas** que pillan de camino.
Hecha a partir de la plantilla de `viaje-lyon-2026`.

Publicada en → https://iaadileli.github.io/copenhague/

## Lo que tiene de propio esta guía

- **Navidad** (`#navidad`): Tivoli con el horario de cada día, el mercadillo de Nytorv y Gammeltorv,
  el Cascanueces, la tabla del resto de mercadillos (con lo que está y no está confirmado) y la luz de
  cada día (sale el sol a las 8:20 y se pone a las 15:40).
- **Tiendas raras** (`#tiendas`) con la **tienda de las pinzas**: Pico Copenhagen y Sui Ava, las dos en
  Grønnegade. 48 tiendas con ficha en sus zonas.
- **Comer**: 39 restaurantes, 36 panaderías y cafés; nota de 1 a 3 estrellas; tabla de **quién abre cada
  uno de los cinco días** (`e-abre.html`, sacada sola de los horarios con `curado.abre`) y la de las
  panaderías con la franja horaria de cada día; julefrokost; «qué hay que probar» con foto.
- **«¿Qué tengo cerca?» con filtros**: comida, café y dulce, tiendas o planes (los cuatro van en
  `sitios.js`, cada uno con su categoría `c`).

## Cómo se monta

El `index.html` **no se edita a mano**: se monta juntando las piezas de `generador/plantilla/`.

```bash
python3 generador/tiempo.py        # d0-tiempo.html (predicción, o histórico si aún no la hay)
python3 generador/mapa.py          # teselas de OSM -> img/mapa-cph.jpg + c3-mapa.html
.venv/bin/python generador/construir.py   # investigación + curado -> zonas, tablas, hoteles, probar, sitios.js
.venv/bin/python generador/montar.py      # junta las piezas -> index.html (y los créditos de las fotos)
.venv/bin/python generador/recursos-sw.py # lista de ficheros del sw.js (subir CACHE a mano al publicar)
node generador/revisar.mjs         # revisa la página EN MARCHA (obligatorio antes de dar nada por bueno)
node generador/capturas.mjs        # capturas para mirarla de verdad
```

- **`generador/datos-fuente/investigacion/*.json`** es la fuente única de los datos: lo que salió de
  buscar en la web el 19-oct-2026, **con las URL de las fuentes** y un campo `verificado`. Los `.md` de
  esa carpeta son los resúmenes (diciembre, comer, bollería, tiendas, práctico).
- **`generador/curado.py`** son mis decisiones: qué se queda fuera (cerrados, sin horario confirmado,
  alta cocina de solo mención), en qué zona va cada sitio, sellos y orden de los planes.
- Los **textos a mano** están en `plantilla/` (cabecera, Navidad, comer, panaderías, tiendas,
  transporte, práctico) y en `plantilla/zonas/<zona>.html` (la entrada de cada zona, con los huecos
  `{{VER}}`, `{{COMER}}` y `{{TIENDAS}}` que rellena `construir.py`).
- Fotos: `fotos-candidatas.py` y `platos-candidatas.py` (categorías de Commons) → `hoja-contacto.py` →
  mirar → `elegir.py` y `elegir-platos.py`, que dejan los créditos.

## Arreglado aquí y que conviene portar

1. **`tiempo.py` daba el sol una hora mal.** Open-Meteo aplica a todas las fechas el desfase horario
   de hoy: pedido en octubre (horario de verano, GMT+2), el amanecer de diciembre (GMT+1) salía a las
   9:19 en vez de a las 8:19. Ahora se pasa a UTC con el desfase que dice la API y se vuelve a la hora
   de ese día con `zoneinfo`. Afecta a cualquier guía que cruce el cambio de hora (Tailandia no, que no
   tiene horario de verano).
2. **`revisar.mjs`**: la comprobación de tablas de horarios ya no supone 3 días y 5 columnas; mira que
   cada fila tenga tantas celdas como su cabecera y ninguna vacía.

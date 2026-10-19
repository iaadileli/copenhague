# PLAN — Guía de Copenhague (puente de diciembre 2026)

Guía PWA para **Alicia y Luis**, del **viernes 4 al martes 8 de diciembre de 2026**.
Encargo de Adil del 19-oct-2026: «una guía como la de Londres, sin día a día, con muchos planes; búsqueda
muy grande de tiendas curiosas (hay una de pinzas para el pelo), panaderías, cafés, restaurantes,
pastelería danesa; el tiempo y el GPS de comida y actividades». Hecha esa misma noche, sin Adil delante.

- Web: https://iaadileli.github.io/copenhague/ · repo `iaadileli/copenhague` (rama `main`)
- Carpeta: `~/Proyectos Adil/copenhague/` · cómo se monta: `README.md`

## Estado

| Fase | Qué | Estado |
|---|---|---|
| 1 | Investigación (5 búsquedas en paralelo, con fuentes) → `generador/datos-fuente/investigacion/` | ✅ 19-oct |
| 2 | Plantilla desde Lyon, generador nuevo `construir.py` + `curado.py` | ✅ 19-oct |
| 3 | Textos a mano: portada, Navidad, 6 zonas, comer, panaderías, tiendas, hoteles, transporte, práctico | ✅ 19-oct |
| 4 | Fotos (zonas y platos), mapa, tiempo, iconos, portada para WhatsApp | ✅ 19-oct |
| 5 | Revisión ejecutando (`revisar.mjs`, `probar-cerca.mjs`, capturas móvil y escritorio) | ✅ 19-oct |
| 6 | Publicar en Pages y comprobar la web desplegada (`revisar.mjs` contra la URL publicada: todo correcto) | ✅ 19-oct |
| 7 | Adil la mira en el iPhone y dice qué cambiar | ⏳ |
| 8 | Repaso de horarios a finales de noviembre (Tivoli, mercadillos de Nyhavn y Højbro, Cascanueces) | ⏳ |

## Decisiones que tomé sin poder preguntar (19-oct, noche)

- **Repo `iaadileli/copenhague`**, como autorizaste, aunque las otras guías se llaman `viaje-<sitio>-2026`.
- **Seis zonas**: el centro (Indre By y Slotsholmen), Nyhavn y Frederiksstaden, Christianshavn (con
  Christiania y Refshaleøen), Vesterbro-Tivoli-Frederiksberg, Nørrebro-Østerbro y excursiones.
- **Fuera de las fichas**: Noma, Alchemist, Kadeau y Koan (alta cocina de 400-700 €, solo mención);
  Café Halvvejen (sin fuente de que siga abierto), Gasoline Grill («temporarily closed» en su web),
  Bageriet BRØD, Social Brew y Flindt & Ørsted (sin horario confirmado), Hotel Sanders como café,
  Reffen (cierra en diciembre), Flid's (año dudoso), la pista de Kongens Nytorv (sin confirmar).
- **Caprichos que sí van**: formel B y Jatak (una estrella, 200-230 € el menú). Escogiste «mezcla
  marcada por precio», no «darse un capricho», así que solo esos dos.
- **Hoteles**: precios reales de Booking con vuestras fechas, consultados el 19-oct. Mis tres
  recomendadas: Next House (156 €/noche, 624 € las 4), Wakeup Borgergade (183 €, 732 €) e Ibsens
  (203 €, 811 €). Zona recomendada: Vesterbro, junto a la estación.
- **«¿Qué tengo cerca?» con filtros** (todo / comer / café y dulce / tiendas / planes): es lo nuevo de
  esta guía y conviene portarlo a las otras.
- **La tienda de las pinzas**: no existe una que venda SOLO pinzas; casi seguro es **Pico Copenhagen**
  (Grønnegade 36), con Sui Ava en la misma calle. Las dos van con un sello propio rosa.

## Pendiente / dudas

- Fechas de 2026 sin anunciar a 19-oct: mercadillo de Nyhavn, pista de Kongens Nytorv y de Frederiksberg,
  horas exactas del Cascanueces en diciembre, precio de la entrada solo a Tivoli (~210 DKK, no oficial).
- Højbro Plads: Visit Copenhagen y la web del mercado se contradicen (¿se traslada a Rådhuspladsen?).
- Torre de Christiansborg: una web la da abierta y otra «cerrada hasta nuevo aviso».
- Fotos sin buena candidata en Commons (van sin foto): stegt flæsk, tarteletter, julefrokost y alguna más.
- Portar aquí lo de Lyon que no se usó (audioguías) solo si Adil lo pide.

## Resumen para Adil (noche del 19-oct-2026)

🔴 **La guía está publicada en https://iaadileli.github.io/copenhague/** y pasa la revisión ejecutándola
(en local y en la web publicada: recursos, enlaces, Booking con fechas 4→8 dic, buscador, modo oscuro,
móvil a 390 px, sin errores de JavaScript). El «¿qué tengo cerca?» lo probé con el GPS simulado en Nyhavn
y los cinco filtros. Falta que la abras tú en el iPhone. 🔴

Qué tiene: Navidad (Tivoli con horario de cada día, el mercadillo de Nytorv con pista de hielo gratis,
el Cascanueces, la luz de cada día), 6 zonas con 44 planes, 43 restaurantes, 33 panaderías y cafés y 47
tiendas raras (123 fichas en total), 33 platos para probar (28 con foto), la tabla de quién abre cada
uno de los cinco días, la ruta del kanelsnegl, 16 hoteles con precio de Booking por noche y el total de
las 4 noches, transporte (City Pass, metro 24 h) y Copenhagen Card con la cuenta de si compensa.

🔴 **Avísales de dos cosas ya:** los hoteles están caros y escasos para esas fechas (tres ya sin
habitaciones a 19-oct), así que conviene que reserven pronto y con cancelación gratis; y Schønnemann (el
smørrebrød más famoso) dice que en Navidad solo le quedan mesas de lunes a miércoles. 🔴

🔴 **La tienda de las pinzas:** no hay ninguna que venda SOLO pinzas. Casi seguro es **Pico Copenhagen**
(Grønnegade 36, la original de 2004); en la misma calle está **Sui Ava**, la otra candidata. Las dos
abren los cinco días. 🔴

Arreglos de esta noche que valen para las otras guías: `tiempo.py` daba el amanecer y el anochecer una
hora mal si el viaje cruza el cambio de hora, y la línea «Máximas de X a Y» mezclaba la mínima con la
máxima (en Lyon también estaba). El GPS con filtros es nuevo y se puede portar.

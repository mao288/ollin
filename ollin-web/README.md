# Ollin: sitio del evento

She No More + Cemican + Anna Fiori, Lunario del Auditorio Nacional, domingo 11 de julio de 2027.

Sitio estático (HTML/CSS/JS, sin dependencias) listo para Netlify.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | Inicio: menú, hero, concepto, puertas a las bandas, playlist, Lunario, registro y preguntas |
| `she-no-more.html`, `cemican.html`, `anna-fiori.html` | Página de cada banda. **Se generan**, no se editan a mano (ver abajo) |
| `datos/bandas.json` | Los datos de las tres bandas: lo único que hay que llenar para las páginas de banda |
| `banda.css` | Estilos de las páginas de banda |
| `ollin.ics` | Evento para agregar al calendario (iPhone, Outlook, etc.) |
| `herramientas/generar_bandas.py` | Genera las tres páginas de banda desde `datos/bandas.json` |
| `herramientas/google_forms_ollin.gs` | Script que crea el Google Form con las mismas preguntas |
| `formulario.html`, `formulario.css`, `formulario.js` | Formulario para que las bandas manden su información |
| `styles.css` | Estilos. La paleta está arriba, en `:root` |
| `main.js` | Cuenta regresiva, cosmos animado y envío del registro |
| `favicon.svg` | Ícono de la luna |
| `og-image.jpg` | Imagen de 1200×630 que se ve al compartir el link en WhatsApp o Facebook |
| `img/nebula.jpg`, `img/water.jpg`, `img/rock.jpg`, `img/frieze.jpg`, `img/moon.png` | Fondos: Vía Láctea con nubes de gas, polvo y estrellas de varios colores; el lago con el oleaje en perspectiva y el reflejo de la luna; el muro como los de Tenochtitlan: hiladas de piedra de corte burdo, sobre todo tezontle rojo y negro con sus poros, más andesita rosácea y gris y algo de basalto, en mortero de cal con arena volcánica y con restos de estuco (se repite sin costuras); el friso de grecas en basalto y la luna llena |
| `herramientas/piedra_tenochtitlan.py` | Genera el muro de piedra actual (`rock3.jpg` → `img/rock.jpg`). Las proporciones de material siguen las rocas del Templo Mayor: tezontle, andesitas, basalto y cal |
| `herramientas/fondos_realistas.py` | Genera la nebulosa y el agua (`python3 fondos_realistas.py nebula water`). Requiere numpy, scipy y Pillow. Todo es procedural, sin fotos de terceros |
| `herramientas/texturas.py`, `texturas_base.py` | Generan el friso de grecas y las funciones de ruido que usan los dos scripts |

## Nombre del evento

**Ollin: algo se mueve en el ombligo de la luna.**

- *Ollin* es "movimiento" en náhuatl, el signo del Quinto Sol (*Nahui Ollin*). Responde a lo que pidió Adrián Magaña: el nombre tiene que comunicar encuentro, proceso y que algo está pasando adentro.
- *El ombligo de la luna* es el lugar. Una de las lecturas de *Mēxihco* es *metztli* (luna), *xictli* (ombligo) y *-co* (lugar). El concepto completo, con fuentes, está en el documento "El Ombligo de la Luna: concepto del evento".
- En el copy se dice siempre "una de las lecturas", porque la etimología tiene debate académico.
- "Tzitzimime" queda libre para la canción de las tres bandas. El sitio no la anuncia.

## Tono del texto

Verbos de encuentro y de proceso: *se están encontrando, se está formando, lo que va pasando, se mueve*. Evitar el tono de cartel estático ("presentamos a…").

## Páginas de banda

Cada banda tiene su página con la misma estructura:

1. **Portada:** logo (o el nombre si no hay logo), su altura del cielo, su verbo y sus datos.
2. **Su camino:** foto de la banda, trayectoria e hitos.
3. **Integrantes:** una tarjeta por persona con foto, nombre, rol y link a su Instagram.
4. **Empieza por:** tres canciones con su porqué y el reproductor de Spotify.
5. **Discografía y redes.**
6. **Navegación:** banda anterior y siguiente, volver a Ollin y Avísame.

**Cómo llenarlas:**

1. Abre `datos/bandas.json` y reemplaza los placeholders con lo que mandaron en el formulario. Todo lo que esté vacío (`""`) o entre `[corchetes]` aparece en la página como pendiente: en cursiva gris con subrayado punteado, o como un recuadro punteado.
2. Las imágenes (logo, fotos de banda, de integrantes y portadas) van en `img/bandas/` y se escriben como ruta, por ejemplo `"foto": "img/bandas/cemican.jpg"`. Para Instagram basta con el `@usuario` o el link completo.
3. Para el reproductor: en Spotify, perfil de la banda → ⋯ → Compartir → Insertar, y copia el `src` del iframe en `spotify_embed`.
4. Corre `python3 herramientas/generar_bandas.py` desde la carpeta del sitio. Reescribe las tres páginas.

Si agregas o quitas integrantes, discos o hitos, la página se ajusta sola.

## Mejoras del Whiteboard ya aplicadas

- **Menú fijo** con Concepto, Bandas, El Lunario y Avísame. En celular se oculta "Concepto" para que quepa.
- **Cuenta regresiva en lunas llenas** con la fase de hoy dibujada al lado. Hoy marca 8 lunas llenas (241 noches). Se calcula sola con el ciclo lunar y la hora está en `EVENT_DATE` de `main.js`.
- **Playlist de Ollin:** para activarla, pega el link de embed de la playlist en el atributo `data-embed` de `#playlist-player` en `index.html`. Mientras esté vacío, se ve el placeholder.
- **Agrégalo a tu calendario:** botón de Google Calendar y archivo `ollin.ics` con recordatorio un día antes. Los dos están a las 19:00 provisionalmente: cuando confirmen la hora, cámbiala en el link de Google (`dates=`), en `ollin.ics` (`DTSTART` y `DTEND`) y en `EVENT_DATE`.
- **Instagram por integrante:** agregado al formulario del sitio y al Google Form, junto con la petición de fotos de integrantes y portadas.

## She No More: ya lleno

La ficha de SNM se llenó con lo que ya está en shenomore.com (versión 26):

- **Integrantes:** nombre, rol, Instagram y foto de cada uno. Las fotos se toman de Cloudinary con recorte automático a la cara (`c_thumb,g_face`).
- **Logo:** el blanco con los círculos (i.ibb.co).
- **Discografía:** las 8 portadas con su link a Spotify. Reproductor del perfil de artista.
- **Redes:** Instagram, Spotify, YouTube, Facebook, TikTok, Patreon, tienda y sitio. TikTok y Patreon solo aparecen en las bandas que los tengan.
- **Trayectoria e hitos:** reescritos en tercera persona desde "Nosotros" y las páginas de shows.
- **Foto de banda provisional:** `img/bandas/she-no-more.jpg` es una cuadrícula con los seis retratos de la sesión de "Buscaré". Cámbiala por una foto grupal cuando la tengan.

Quedan como placeholder: el año de inicio y el verbo para esa noche.

Pendientes del Whiteboard: generador de stories, glosario náhuatl y galería de backstage.

## Formulario para las bandas (`formulario.html`)

Página aparte, sin enlace desde el sitio y con `noindex`. Se manda por WhatsApp a Cemican y a Anna Fiori, y conviene que SNM la llene también para que las tres fichas salgan iguales.

- Las respuestas llegan a **Netlify → Forms → bandas**.
- Si cierran la página, lo escrito se queda guardado en su navegador.
- No hay subida de archivos: logo y fotos se piden como link a una carpeta, para no pelear con límites de tamaño.

**Dónde va cada respuesta en el sitio:**

| Del formulario | En el sitio |
|---|---|
| Origen, año, sonido | Ficha de la banda: "De" y "Suena a" |
| Trayectoria (máx. 450 caracteres) | Ficha de la banda: párrafo principal |
| Tres canciones con su porqué | "Empieza por" en la ficha |
| Qué traen al encuentro | Ficha de la banda: "Hilo" y la sección de concepto |
| Qué significa compartir escenario | Citas para el sitio y redes |
| Canción que conecta con la luna, el lago… | Confirma o corrige nuestras interpretaciones (por ejemplo, "Luna Desmembrada") |
| Un verbo para esa noche | Pieza de redes o titular: los tres verbos juntos |
| Integrantes con rol e Instagram | Tarjetas de integrantes en la página de la banda |
| Links, logo, fotos y crédito | Redes, logo en la portada, fotos de banda, integrantes y portadas de discos |

**Mensaje para mandar con el link** (cambia la URL):

> ¡Hola! Estamos armando el sitio de Ollin, el encuentro del 11 de julio en el Lunario. Queremos que las tres bandas se cuenten con la misma estructura para que se sienta como una sola historia. ¿Nos ayudan llenando esto? Son unos 15 minutos y lo que escriban va casi tal cual a su ficha. Antes de publicar les mandamos cómo quedó. 🖤
> https://TU-DOMINIO/formulario.html

## Qué falta llenar

Busca `EDITAR` en los archivos:

- [ ] **Link de Spotify de SNM.** Ahora apunta a una búsqueda.
- [ ] **Fichas de las bandas.** Cada una tiene el texto genérico "Esta ficha se está escribiendo junto con…". Cuando lleguen las respuestas del formulario, cámbialo por la trayectoria (busca `EDITAR` en `index.html`). Las canciones de SNM son "Dust On The Map", "Más Allá de la Tormenta" (antes "Tu Fuego") y "Buscaré".
- [ ] **Puertas, orden del cartel, edad y precios.** Están como "Por anunciar".
- [ ] **Hora del evento.** La cuenta regresiva usa las 20:00 h (`EVENT_DATE` en `main.js`).
- [ ] **og:image con URL absoluta.** Cuando tengas dominio, cambia `content="og-image.jpg"` por `https://tudominio/og-image.jpg`. Facebook y WhatsApp la necesitan completa.
- [ ] **Instagram de Anna Fiori.** No lo verifiqué, así que no lo puse. Están su Spotify, Bandcamp y sitio.
- [ ] **Logos de las bandas** (recomendado). En el flyer de *Tributo a Nuestros Muertos* se ve que cada banda tiene su logotipo. Si me pasan los tres en PNG o SVG con fondo transparente, sustituyo los nombres escritos en el hero y en las fichas.
- [ ] **Flyer oficial.** Cuando exista el póster del evento, conviene agregarlo como sección de cartel y usarlo como `og-image.jpg`. El sitio está pensado para convivir con un flyer ilustrado como los que ya usan.
- [ ] **Fotos de las bandas** (opcional). El diseño funciona solo con tipografía. Si quieren fotos, súbanlas a Cloudinary y me pasan las URLs.


## Deploy en Netlify

1. Sube la carpeta a un repo nuevo en GitHub, o arrastra la carpeta a **app.netlify.com → Add new site → Deploy manually**.
2. Netlify detecta el formulario `avisame` solo. Revísalo en **Site configuration → Forms**. Si aparece desactivado, haz clic en **Enable form detection** y vuelve a hacer deploy.
3. Los registros llegan a **Forms → avisame**, donde puedes exportarlos a CSV. Cada registro trae nombre, correo, WhatsApp (opcional) y **de qué fanbase viene**, para que Adrián vea cuánta gente aporta cada banda.
4. Para recibir un correo por cada registro: **Site configuration → Notifications → Emails and webhooks → Form submission notifications**.
5. Para el dominio: **Domain management → Add a domain**. Ideas: `ombligodelaluna.mx` o `elombligodelaluna.com`. No revisé si están disponibles.

El plan gratis de Netlify acepta 100 envíos de formulario al mes. Si esperan más registros, conviene subir de plan o conectar el formulario a otro servicio antes de anunciar.

> Recuerda: trabaja siempre desde este ZIP y no descargues el sitio en vivo, porque Cloudflare inyecta scripts que rompen el JS.

## Estética

- **Paleta:** tomada del flyer de Cemican y neutral para las tres bandas. Cempasúchil `#EE7B27`, oro viejo `#D6AF63`, jade `#64A58E`, sangre seca `#9A2E22`, piedra `#3A3027` y hueso `#EADFC8` sobre el negro del espacio `#07070D`. Ninguna banda tiene color propio.
- **Tipografía:** Rubik Dirt, piedra erosionada, solo en titulares y siempre en mayúsculas porque tiene un solo peso. El texto corrido va en Archivo.
- **Cosmos:** tres capas de nebulosa que derivan en sentidos distintos y además se desplazan a diferente velocidad con el scroll y el mouse. Las estrellas están fijas: solo parpadean y se mueven con el parallax. Cada 2 a 5 segundos cruza un cometa, y a veces uno lento y largo. Con "reducir movimiento" todo queda quieto.
- **El lago en movimiento:** `main.js` redibuja el agua en franjas horizontales que ondulan (finas y rápidas en el horizonte, amplias al acercarse) y le suma destellos de la luna que se encienden y se apagan. Corre a unos 30 cuadros por segundo, solo mientras el lago está en pantalla. Con "reducir movimiento" se queda la imagen fija.
- **Recorrido:** la luna llena en el cielo. En las tres alturas del cielo empieza *Metztliapan*, el lago de la luna, con su reflejo. El friso de grecas marca la orilla y de ahí para abajo está la piedra. Las estrellas y la nebulosa se apagan al llegar a la tierra (`updateFade()` en `main.js`).

## Qué hace cada sección

1. **Hero:** centrado, con la luna pequeña arriba, "Ollin", el subtítulo, la fecha y la cuenta regresiva en noches.
2. **Ollin es movimiento:** qué es *ollin*, el encuentro que se está formando y, en el ombligo de la luna, la etimología, el lago, Coyolxauhqui en el Templo Mayor y el Lunario en la orilla.
3. **El lago (*Metztliapan*):** las tres alturas del cielo (She No More, Anna Fiori, Cemican) sobre el agua, con el reflejo de la luna.
4. **Horizonte y piedra:** el friso de grecas marca la orilla y desde ahí empieza la roca.
5. **Quiénes se están encontrando:** ya sobre la piedra, una losa por banda con su nombre, un texto genérico, tres canciones y sus links. La trayectoria llega del formulario.
6. **El Lunario:** en la orilla del antiguo lago, "nos vemos en La Luna" (la escultura de Soriano), dirección y cómo llegar.
7. **Avísame:** el registro para la venta de boletos.
8. **Preguntas.**

## Accesibilidad y rendimiento

- Responsive desde 320 px.
- Foco visible al navegar con teclado.
- Si el usuario tiene "reducir movimiento" activado, las animaciones se apagan.
- El cielo se pausa cuando el hero sale de pantalla.
- No usa librerías externas; solo Google Fonts (Rubik Dirt y Archivo).

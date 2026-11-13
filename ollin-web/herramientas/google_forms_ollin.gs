/**
 * Ollin — Formulario de información por banda
 * Crea el Google Form completo y una hoja de cálculo donde caen las respuestas.
 *
 * Cómo usarlo:
 * 1. Entra a https://script.google.com con la cuenta de Google donde quieres el formulario.
 * 2. "Nuevo proyecto", borra lo que trae, pega todo este archivo y guarda.
 * 3. Elige la función crearFormularioOllin y presiona "Ejecutar". Autoriza los permisos.
 * 4. Abre "Registro de ejecución": ahí salen el link para compartir, el de edición y el de la hoja.
 */
function crearFormularioOllin() {
  var form = FormApp.create('Ollin: cuéntanos de tu banda');

  form.setDescription(
    'Ollin, algo se mueve en el ombligo de la luna. She No More, Cemican y Anna Fiori. ' +
    'Lunario del Auditorio Nacional, domingo 11 de julio de 2027.\n\n' +
    'POR QUÉ OLLIN\n' +
    'Ollin significa "movimiento" en náhuatl. Para los mexicas vivimos en la era del Quinto Sol, ' +
    'la de Nahui Ollin: un mundo que no se queda quieto. Eso es este encuentro: tres bandas que venían ' +
    'cada una por su camino y que se están moviendo hacia el mismo punto. "El ombligo de la luna" es una ' +
    'de las lecturas del nombre de México (metztli, luna; xictli, ombligo), y el Lunario está en la antigua ' +
    'orilla de ese lago.\n\n' +
    'PARA QUÉ ES ESTO\n' +
    'Les pedimos lo mismo a las tres bandas para que el sitio del evento se lea como una sola historia y no ' +
    'como tres carteles pegados. Son unos 15 minutos. Si algo no aplica, déjenlo en blanco. Los textos con ' +
    'límite de caracteres van casi tal cual al sitio. Antes de publicar les mandamos cómo quedó su ficha. 🖤'
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setLimitOneResponsePerUser(false);
  form.setConfirmationMessage(
    'Recibido. Antes de publicar les mandamos cómo quedó su ficha. Gracias por moverse con nosotros hacia el centro. 🖤'
  );

  // ---------- utilidades ----------
  function maxChars(n) {
    return FormApp.createTextValidation()
      .setHelpText('Máximo ' + n + ' caracteres.')
      .requireTextLengthLessThanOrEqualTo(n).build();
  }
  function maxCharsParrafo(n) {
    return FormApp.createParagraphTextValidation()
      .setHelpText('Máximo ' + n + ' caracteres.')
      .requireTextLengthLessThanOrEqualTo(n).build();
  }
  function esUrl() {
    return FormApp.createTextValidation()
      .setHelpText('Pega un link completo, que empiece con https://')
      .requireTextIsUrl().build();
  }
  function texto(titulo, ayuda, requerido, validacion) {
    var it = form.addTextItem().setTitle(titulo);
    if (ayuda) it.setHelpText(ayuda);
    if (requerido) it.setRequired(true);
    if (validacion) it.setValidation(validacion);
    return it;
  }
  function parrafo(titulo, ayuda, requerido, validacion) {
    var it = form.addParagraphTextItem().setTitle(titulo);
    if (ayuda) it.setHelpText(ayuda);
    if (requerido) it.setRequired(true);
    if (validacion) it.setValidation(validacion);
    return it;
  }
  function seccion(titulo, ayuda) {
    var p = form.addPageBreakItem().setTitle(titulo);
    if (ayuda) p.setHelpText(ayuda);
    return p;
  }

  // ---------- 1. La banda ----------
  form.addSectionHeaderItem().setTitle('1. La banda');
  form.addListItem()
    .setTitle('¿Qué banda o proyecto son?')
    .setChoiceValues(['She No More', 'Cemican', 'Anna Fiori'])
    .setRequired(true);
  texto('De dónde son', 'Ciudad, estado.');
  texto('Año en que empezaron', 'Ej. 2006',
        false,
        FormApp.createTextValidation().setHelpText('Escribe el año con cuatro dígitos.')
          .requireNumberBetween(1950, 2027).build());
  texto('Cómo describen su sonido, en una frase',
        'Ej. folk metal prehispánico con thrash y death', false, maxChars(80));
  parrafo('Integrantes: nombre, rol e Instagram de cada quien',
          'Cada integrante tiene su tarjeta en la página de la banda, con su foto y un link a su Instagram. ' +
          'Un integrante por línea. Ej. Tecuhtli, guitarra y voz, @usuario');

  // ---------- 2. Su camino ----------
  seccion('2. Su camino', 'Lo que va en su ficha del sitio.');
  parrafo('Su trayectoria en corto',
          'Escríbanla en tercera persona, como la leería alguien que no los conoce. Unas 4 o 5 líneas.',
          true, maxCharsParrafo(450));
  parrafo('Discografía principal', 'Un disco por línea: año y título.');
  parrafo('Hasta tres momentos que los definen',
          'Festivales, giras, premios, colaboraciones. Uno por línea.');

  // ---------- 3. Tres canciones ----------
  seccion('3. Tres canciones para empezar',
          'Las que le recomendarían a alguien que viene por otra de las bandas, con una línea de por qué.');
  for (var i = 1; i <= 3; i++) {
    texto('Canción ' + i);
    texto('Por qué la canción ' + i, null, false, maxChars(60));
  }

  // ---------- 4. El encuentro ----------
  seccion('4. El encuentro',
          'Esto es lo que va a hacer que la página se sienta como una sola cosa. Contesten con calma.');
  parrafo('¿Qué traen ustedes a este encuentro?',
          'Lo que su música aporta que las otras dos bandas no.', false, maxCharsParrafo(280));
  parrafo('¿Qué significa para ustedes compartir escenario con las otras dos bandas?',
          null, false, maxCharsParrafo(280));
  parrafo('¿Alguna canción suya conecta con la luna, las estrellas, el lago, el Mictlan o el centro?',
          'Cuál y qué cuenta. Nos ayuda a no interpretar de más.');
  texto('Un verbo para lo que va a pasar esa noche',
        'Ej. encender, invocar, despertar', false, maxChars(24));
  parrafo('Algo que quieran que el público de las otras bandas sepa de ustedes',
          null, false, maxCharsParrafo(200));

  // ---------- 5. Links y materiales ----------
  seccion('5. Links y materiales');
  texto('Spotify', 'Link del perfil de artista.', false, esUrl());
  texto('YouTube', null, false, esUrl());
  texto('Instagram', '@usuario');
  texto('Facebook', null, false, esUrl());
  texto('Bandcamp u otra tienda', null, false, esUrl());
  texto('Sitio web', null, false, esUrl());
  texto('Carpeta con logo y fotos',
        'Un link de Google Drive, Dropbox o WeTransfer con: el logo en PNG o SVG con fondo transparente, ' +
        'dos o tres fotos de la banda en alta, una foto de cada integrante (de preferencia cuadrada) ' +
        'y las portadas de sus discos.', false, esUrl());
  texto('Crédito de las fotos', 'Nombre del fotógrafo o fotógrafa.');

  // ---------- 6. Contacto y permiso ----------
  seccion('6. Contacto y permiso');
  texto('Quién llena esto', null, true);
  texto('WhatsApp', null, true);
  texto('Correo', null, false,
        FormApp.createTextValidation().setHelpText('Escribe un correo válido.').requireTextIsEmail().build());
  form.addCheckboxItem()
    .setTitle('Autorización')
    .setChoiceValues(['Autorizamos usar estos textos, links, logo y fotos en el sitio y las redes de Ollin. Antes de publicar nos mandan cómo quedó.'])
    .setRequired(true);
  parrafo('Algo más que quieran decirnos (opcional)');

  // ---------- hoja de respuestas ----------
  var hoja = SpreadsheetApp.create('Ollin: respuestas de las bandas');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());

  Logger.log('Link para compartir con las bandas: ' + form.getPublishedUrl());
  Logger.log('Link para editar el formulario: ' + form.getEditUrl());
  Logger.log('Hoja con las respuestas: ' + hoja.getUrl());
}

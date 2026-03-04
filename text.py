TUTORIAL = """Esta es una historia interactiva. Te encuentras en un mundo por explorar y en el puedes irte moviendo por las habitaciones y lugares. Puedes también tomar objetos que parezcan interesantes y usarlos para desbloquear otros lugares u objetos. Las descripciones de los lugares a veces son algo largas, por lo que si ves que no sale todo el texto, presiona enter y saldrá lo demás, en caso de que te haga una pregunta y luego una pausa, escribe una respuesta cortita ;D. Los comandos que tendrás a manos son:

MOVERSE A
Si estas en una habitación, puedes moverte a otra habitación adyacente. A cada habitación que entres, se te dará una descripción del lugar y de las habitaciones aledañas. Por ejemplo si tienes el siguiente texto:

              "Entras a la cocina, ves el refrigerador y un par de cuchillos en la meseta, no hay mucho más que ver. A tus espaldas, el Living."

Para regresar al Living, escribes MOVERSE A Living, no te preocupes por las mayúsculas y minúsculas, el programa se encarga de eso.
A su vez, si quieres inspeccionar ciertos objetos o lugares de una habitación, puedes utilizar este comando:
          
          "En el sótano parece haber una caja de herramientas"
          MOVERSE A caja
          "Una enorme caja de herramientas, hay un martillo y destornillador."

EXAMINAR
Puedes volver a ver la descripción de los objetos que veas o los lugares a los que vayas. Por ejemplo, ocupando el texto anterior, puedes escribir:
              
              EXAMINAR cocina

donde volveras a ver la descripción de la cocina.
              
              "Entras a la cocina, ves el refrigerador y un par de cuchillos en la meseta, no hay mucho más que ver. A tus espaldas, el Living."

en cambio, si escribes:
              
              EXAMINAR cuchillos
              
saldrá alguna descripción, como:
              
              "Un par de cuchillos viejos, el filo se ve algo desgastado y el mango de madera se nota oscurecido por el tiempo."

TOMAR
Puedes tomar algunos objetos que encuentres y te puedan servir. Para hacerlo, simplemente escribe:

              TOMAR objeto

donde "objeto" es el nombre del objeto que deseas tomar. Por ejemplo:

              TOMAR cuchillos

Esto añadirá el objeto a tu inventario y podrás usarlo más adelante en la historia.
En caso de que el objeto no lo puedas tomar, el programa te lo hará saber.
              
              TOMAR refrigerador
              "No creo que pueda tomar eso"

USAR _ EN _
Puedes usar objetos que se encuentren en tu inventario para desbloquear otros objetos o lugares. Para hacerlo, escribe:

              USAR objeto EN objetivo

donde "objeto" es el nombre del objeto que deseas usar y "objetivo" es el nombre del objeto o lugar que deseas desbloquear. Por ejemplo:

              USAR cuchillos EN refrigerador

Esto intentará usar el objeto "cuchillos" en el "refrigerador". Se desbloqueará y te entregará otro objeto o te dará alguna pista sobre que lugar visitar porque se produjo un cambio.
En caso de que no se pueda utilizar el objeto, el programa te lo hará saber.

              "No creo que pueda usar eso aquí."

PENSAR
Puedes pensar en voz alta para explorar tus ideas y reflexionar sobre la situación actual. A veces da pistas útiles que pueden ayudarte a avanzar en la historia.

              PENSAR
              "Quizás ese recuadro que vi antes contenga algo útil."
              
              PENSAR
              "Tengo hambre..."

AYUDA
Vuelve a mostrar este mensaje de tutorial por si olvidaste algo.

SALIR
Guarda tu progreso y sale del programa.

Presiona ENTER para continuar a la aventura.
"""
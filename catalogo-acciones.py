#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El catálogo de acciones del Plan Maestro de Marketing.

    python3 catalogo-acciones.py            # el catálogo en pantalla
    python3 catalogo-acciones.py --json     # los mismos datos, para el documento

Las acciones son datos, no párrafos escritos a mano. Así se pueden contar,
ordenar por coste o por plazo, cruzar con la cartera de campañas de la Parte VI
del Plan de Dirección y verificar. Un catálogo que vive en prosa no se puede auditar: se
puede leer, que es otra cosa.

REGLA DE ENTRADA. Una acción entra en este catálogo si —y solo si— puede
declarar en una línea qué gana el paciente. No «qué conseguimos nosotros»: qué
gana él. La columna «gana» no es decorativa; es el filtro. Si no se puede
rellenar, la acción no existe.

Campos
  cod       A01…, estable: se cita en actas y en el calendario
  grupo     el estado del paciente sobre el que actúa
  accion    qué se hace, en una línea
  gana      qué se lleva el paciente, aunque no compre nada
  quien     puesto responsable de que ocurra
  coste     banda anual: 0 · € (<1 k) · €€ (1–5 k) · €€€ (5–15 k) · €€€€ (>15 k)
  plazo     ya · trim (un trimestre) · año · estruct (cambia cómo trabajamos)
  efecto    1 a 5, efecto esperado sobre el objetivo del ejercicio
  indicador qué número se mueve si funciona
  sem       verde · amarillo · naranja, según el marco de publicidad sanitaria
  campana   campaña de la cartera del Plan de Dirección a la que pertenece, o «—»
"""
import json
import sys

# ---------------------------------------------------------------- los estados
# El paciente no recorre un embudo: recorre estados, y los recorre en los dos
# sentidos. Un embudo termina en la venta; una persona, no.
ESTADOS = [
    ("E1", "Ajeno", "No sabe que existimos y no tiene un problema con nombre."),
    ("E2", "Latente", "Algo le pasa en la boca y todavía no lo ha llamado por su nombre."),
    ("E3", "Despierto", "Ya lo ha nombrado. Aún no busca: lo aplaza."),
    ("E4", "En busca", "Busca activamente, casi siempre solo y casi siempre mal informado."),
    ("E5", "En consideración", "Nos tiene en una lista corta y compara."),
    ("E6", "En la puerta", "Ha pedido cita. Es nuestro durante una hora."),
    ("E7", "En decisión", "Tiene un presupuesto encima de la mesa y una conversación pendiente en casa."),
    ("E8", "En tratamiento", "Ha dicho que sí y ahora tiene miedo de haber acertado."),
    ("E9", "En cuidado", "Ha terminado y sigue con nosotros por decisión propia."),
    ("E10", "Prescriptor", "Habla de nosotros sin que se lo pidamos."),
    ("E11", "Dormido", "Fue paciente y se apagó. No se fue: dejó de venir."),
    ("E12", "Perdido", "Se fue, con motivo o sin él, y lo sabemos o deberíamos saberlo."),
]

GRUPOS = [
    ("G1", "E1 · E2 · E3", "Presencia y educación",
     "Actuar sobre quien todavía no nos busca. Es la parte del plan que no "
     "produce facturación este ejercicio y sin la cual no hay ninguno de los siguientes."),
    ("G2", "E4", "Encontrabilidad y respuesta",
     "Que quien nos busque nos encuentre, y que al encontrarnos le conteste "
     "alguien. La segunda mitad de esa frase es donde se pierde el dinero."),
    ("G3", "E5", "La duda",
     "El territorio propio del centro. Casi toda la ventaja competitiva de "
     "«no medias sonrisas» se cobra aquí."),
    ("G4", "E6", "La visita como medio",
     "La primera visita es el mejor soporte publicitario que tenemos y el "
     "único que ya está pagado."),
    ("G5", "E7 · E8", "La decisión y el tratamiento",
     "Nadie decide en la silla el día del miedo. Lo que se hace aquí decide "
     "la conversión de verdad, no el anuncio."),
    ("G6", "E9 · E11 · E12", "El cuidado, el sueño y la pérdida",
     "Donde está el dinero, según la aritmética de la propia Plan de Dirección: dos de "
     "estas campañas son el 63 % de lo que aporta la cartera."),
    ("G7", "E10", "Prescripción y alianzas",
     "Lo que otro dice de nosotros vale más que lo que digamos nosotros, y "
     "cuesta menos. También es lo más lento de construir."),
]

# cod, grupo, acción, qué gana el paciente, quién, coste, plazo, efecto, indicador, semáforo, campaña
A = [
# ---------------------------------------------------------------- G1
("A01","G1","Aula da Boca: charla mensual en asociaciones vecinales, centros culturales y clubes de la ciudad",
 "Entiende lo que le pasa en la boca sin que nadie le venda nada esa tarde","DC","€","trim",2,
 "Asistentes y primeras visitas con origen «charla»","verde","—"),
("A02","G1","Programa en residencias de mayores: revisión anual en el propio centro, con informe a la familia",
 "Alguien mira la boca de un mayor que ya no puede pedir cita solo","DR","€€","trim",3,
 "Residencias con convenio y revisiones hechas","amarillo","—"),
("A03","G1","Convenio con colegios: salud bucodental infantil, sin ninguna captación comercial dentro del aula",
 "Un niño aprende a cepillarse antes de necesitar un implante a los cincuenta","HIG","€","año",1,
 "Centros con convenio activo","naranja","—"),
("A04","G1","Ciclo abierto «lo que nadie le cuenta de los implantes», en el propio centro, con turno de preguntas",
 "Pregunta lo que no se atreve a preguntar en una consulta con el reloj corriendo","DR","€","trim",2,
 "Asistentes y conversión a primera visita a 90 días","amarillo","—"),
("A05","G1","Material informativo en farmacias de barrio, sin promesa de resultado ni oferta",
 "Recibe información útil de alguien en quien ya confía","RAC","€","trim",1,
 "Farmacias con material y origen declarado en la PV","amarillo","—"),
("A06","G1","Contenido que responde a las preguntas que la gente hace de verdad, no a las que nos gustaría que hiciera",
 "Encuentra una respuesta honesta escrita por un clínico y no por un redactor","DG","€","año",3,
 "Preguntas respondidas y tráfico de intención informativa","amarillo","C9"),
("A07","G1","Recorrido en vídeo por la clínica, sin pacientes y sin música de anuncio",
 "Ve dónde va a meterse antes de meterse","DG","€","trim",2,
 "Reproducciones completas y menciones en la acogida","verde","C9"),
("A08","G1","Prótesis a la vista: jornada de puertas abiertas al laboratorio y al flujo digital",
 "Ve con sus ojos por qué una pieza cuesta lo que cuesta","DC","€","año",2,
 "Asistentes y efecto sobre la objeción de precio","verde","—"),
("A09","G1","Presencia en medios locales como fuente experta, no como anunciante",
 "Lee sobre salud bucodental en su periódico y no un publirreportaje","DG","0","año",1,
 "Apariciones no pagadas","amarillo","—"),
("A10","G1","Patrocinio deportivo de base con contrapartida sanitaria: revisión al equipo, no logotipo en la camiseta",
 "Su hijo tiene la boca revisada porque su club juega con nosotros","DC","€€","año",2,
 "Clubes con revisión hecha","verde","—"),
("A11","G1","Programa de salud bucodental para empresas del puerto, del polígono y de la conserva",
 "Le revisan la boca en horario de trabajo, que es el único que tiene","GER","€€","año",3,
 "Empresas con acuerdo y trabajadores revisados","amarillo","—"),
("A12","G1","Señalética y fachada legibles desde la calle, con el número de registro sanitario visible",
 "Sabe qué hay dentro antes de entrar y quién responde de ello","GER","€€","ya",1,
 "Entradas espontáneas registradas","verde","—"),
# ---------------------------------------------------------------- G2
("A13","G2","Ficha de negocio completa: horarios reales, fotos propias, servicios y accesibilidad",
 "No se planta en la puerta un día que está cerrado","REC","0","ya",3,
 "Impresiones, llamadas y cómo-llegar","verde","C9"),
("A14","G2","Web construida sobre preguntas reales, con la respuesta firmada por quien la sostiene",
 "Sabe quién le está hablando y puede pedirle cuentas","DG","€€","trim",3,
 "Páginas vistas de intención alta","amarillo","C9"),
("A15","G2","Página por tratamiento con precio de partida publicado y qué incluye",
 "Sabe el orden de magnitud antes de sentarse, y no le sorprenden en el peor momento","GER","0","trim",3,
 "Conversión de página a cita","amarillo","C9"),
("A16","G2","Página por localidad de la ría con el tiempo real de desplazamiento y dónde aparcar",
 "Sabe si le compensa venir desde Cangas, Moaña o Baiona antes de llamar","DG","€","trim",2,
 "Primeras visitas por localidad de origen","verde","C9"),
("A17","G2","Búsqueda de pago acotada a intención alta y a radio corto, con tope mensual duro",
 "Encuentra una clínica que existe de verdad a veinte minutos de su casa","GER","€€€€","ya",3,
 "Coste por primera visita y su tendencia","amarillo","C9"),
("A18","G2","Respuesta en menos de quince minutos en horario; fuera de él, respuesta automática que dice la verdad sobre cuándo se le contestará",
 "No se queda esperando sin saber si alguien le ha leído","REC","0","ya",4,
 "Tiempo hasta primera respuesta, mediana y p90","verde","—"),
("A19","G2","Cita en línea con hueco real, no formulario de contacto",
 "Cierra su cita a las once de la noche, que es cuando se acuerda","REC","€€","trim",3,
 "Citas cerradas fuera de horario","verde","—"),
("A20","G2","WhatsApp de centro con norma publicada: aquí no se diagnostica por foto",
 "No recibe un diagnóstico falso por una foto mal hecha","REC","0","ya",2,
 "Consultas resueltas y derivadas a visita","naranja","—"),
("A21","G2","Teléfono contestado por persona durante todo el horario, con registro de llamadas perdidas",
 "Le contesta alguien, no un menú","REC","€€","ya",4,
 "Llamadas perdidas sobre recibidas","verde","—"),
("A22","G2","Recuperación de toda llamada perdida antes de dos horas, sin excepción",
 "Le devuelven la llamada aunque él ya se haya rendido","REC","0","ya",4,
 "Llamadas perdidas recuperadas","verde","—"),
("A23","G2","Solicitud sistemática de reseña a todo paciente al alta, nunca incentivada y nunca filtrada",
 "Lee opiniones que no están compradas","RAC","0","ya",3,
 "Reseñas nuevas al mes y nota media","naranja","C9"),
("A24","G2","Respuesta pública a toda reseña, y en veinticuatro horas a la negativa",
 "Ve cómo tratamos a quien se queja, que es el único dato fiable","DG","0","ya",3,
 "Reseñas negativas con respuesta y su plazo","naranja","C9"),
# ---------------------------------------------------------------- G3
("A25","G3","Segunda Opinión Honesta: informe escrito que el paciente se lleva, diga lo que diga",
 "Se lleva un documento suyo, aunque decida tratarse en otro sitio","DR","€€","ya",4,
 "Segundas opiniones emitidas y su conversión","amarillo","C7"),
("A26","G3","Publicación anual del índice de «no necesita tratamiento» sobre las segundas opiniones",
 "Puede comprobar con un número cuántas veces decimos que no hace falta","DG","0","año",3,
 "Índice publicado y su evolución","amarillo","C7"),
("A27","G3","Consulta del Miedo: primera visita para quien lleva más de diez años sin ir, sin propuesta de tratamiento ese día",
 "Entra sin que nadie le proponga nada. Solo a contar y a que le escuchen","DR","€€","trim",4,
 "Consultas del miedo y su conversión a 90 días","amarillo","C5"),
("A28","G3","Presupuesto sin prisa: sin caducidad comercial, con la consecuencia clínica de esperar seis, doce y veinticuatro meses",
 "Decide con información en vez de con urgencia inventada","DR","0","ya",5,
 "Tasa de aceptación y días hasta aceptar","amarillo","—"),
("A29","G3","Explicación de qué se paga: material, tiempo clínico, laboratorio, garantía y revisión",
 "Entiende el precio en vez de sospechar de él","GER","0","trim",3,
 "Objeciones de precio registradas en la Fase 10","verde","—"),
("A30","G3","Casos reales contados por el clínico, con consentimiento expreso y sin promesa de resultado",
 "Ve un caso parecido al suyo contado por quien lo trató","DR","€","trim",3,
 "Casos publicados y menciones espontáneas","naranja","C2"),
("A31","G3","Visita previa de cinco minutos para ver la clínica y conocer al equipo, sin sillón",
 "Conoce el sitio sin comprometerse a nada","REC","0","ya",2,
 "Visitas previas y su conversión","verde","C5"),
("A32","G3","Comparativa honesta con tratarse fuera: coste total incluyendo revisiones, garantía y quién responde si falla",
 "Compara peras con peras antes de coger un avión","DR","0","trim",3,
 "Pacientes con tratamiento previo fuera atendidos","amarillo","C7"),
("A33","G3","Financiación con coste total visible y sin comisión para quien la ofrece",
 "Nadie gana nada por empujarle a financiar","GER","0","ya",3,
 "Financiaciones y tasa de impago","naranja","—"),
("A34","G3","Tabla de garantías publicada por tipo de tratamiento, entregada con cada presupuesto",
 "Sabe por escrito qué pasa si algo falla dentro de cinco años","DG","0","ya",4,
 "Presupuestos entregados con tabla adjunta","amarillo","—"),
# ---------------------------------------------------------------- G4
("A35","G4","Recordatorio de cita que cuenta lo que va a pasar, cuánto dura y qué traer",
 "Llega sabiendo a qué viene y no en ayunas por si acaso","REC","0","ya",2,
 "Ausencias sin avisar","verde","—"),
("A36","G4","Acogida en noventa segundos, por su nombre y sin mostrador de por medio",
 "Le reciben como a una persona esperada, no como a un turno","REC","0","ya",3,
 "Cumplimiento observado de la Fase 1","verde","—"),
("A37","G4","El Acompañante: silla, nombre, y copia del plan también para él",
 "Quien viene con él entiende lo mismo y puede ayudarle a decidir en casa","REC","0","ya",4,
 "Planes entregados por duplicado","amarillo","C8"),
("A38","G4","Sala de espera sin televisión comercial ni publicidad de tratamiento",
 "Espera sin que le vendan mientras está nervioso","GER","€","ya",2,
 "Verificación trimestral de sala","verde","—"),
("A39","G4","Explicación con el modelo y la imagen en la mano, no con folleto",
 "Ve su propia boca en vez de la de un catálogo","DR","€€","trim",3,
 "Comprensión verificada al cierre de la visita","verde","—"),
("A40","G4","Entrega del plan por escrito el mismo día, siempre, también cuando el plan es no hacer nada",
 "Sale con papel. Siempre","DR","0","ya",4,
 "Planes entregados el mismo día sobre visitas","verde","—"),
("A41","G4","Nada se cierra el día del miedo: por norma se le invita a pensarlo",
 "Nadie le arranca un sí el día que llegó asustado","DG","0","ya",4,
 "Aceptaciones diferidas sobre el total","verde","C5"),
("A42","G4","Registro literal de lo que dijo que le preocupaba, en su ficha y en sus palabras",
 "La próxima vez alguien se acuerda de lo que le importaba","RAC","0","ya",3,
 "Fichas con preocupación registrada","verde","—"),
("A43","G4","Encuesta de una sola pregunta al salir, contestada de pie y en diez segundos",
 "Le preguntan cuando aún se acuerda","REC","0","ya",2,
 "Respuestas y su serie mensual","verde","—"),
("A44","G4","Hueco útil: la cancelación se ofrece por orden clínico a quien espera, no por orden de importe",
 "Entra antes porque su caso corre más prisa, no porque pague más","REC","0","trim",3,
 "Huecos reasignados sobre cancelaciones","verde","—"),
("A45","G4","Información real de aparcamiento, bus y accesibilidad, publicada y comprobada",
 "Sabe dónde dejar el coche y si entra con silla de ruedas","REC","0","ya",2,
 "Incidencias de acceso registradas","verde","—"),
("A46","G4","Atención en gallego y apoyo de traducción para quien lo necesite",
 "Le atienden en la lengua en la que piensa","DC","€","trim",2,
 "Visitas atendidas con apoyo idiomático","verde","—"),
# ---------------------------------------------------------------- G5
("A47","G5","Llamada del propio clínico veinticuatro horas después de cualquier cirugía",
 "Le llama quien le operó, no un número desconocido","DR","0","ya",4,
 "Llamadas hechas sobre cirugías","verde","C1"),
("A48","G5","Vía directa para cuando algo va mal, con nombre, número y plazo de respuesta comprometido",
 "Sabe a quién llamar a las diez de la noche de un sábado","DC","€","ya",4,
 "Incidencias atendidas dentro de plazo","verde","—"),
("A49","G5","Informe de progreso a mitad de tratamiento, con lo hecho y lo que queda",
 "Sabe por dónde va sin tener que preguntar","DR","0","trim",2,
 "Informes entregados sobre tratamientos largos","verde","—"),
("A50","G5","El Archivo de tu Boca: su historia clínica, imágenes y plan, en formato que se lleva aunque se marche",
 "Es dueño de su propia historia y puede llevársela a cualquier sitio","DC","€€€","año",4,
 "Archivos entregados sobre altas","naranja","C1"),
("A51","G5","Fotografía clínica normalizada para el archivo del paciente, no para el escaparate",
 "Sus imágenes existen para tratarle, no para anunciarnos","HIG","€€","trim",2,
 "Casos con serie fotográfica completa","naranja","—"),
("A52","G5","Acompañamiento pactado paso a paso para el paciente con miedo, con señal de parada acordada",
 "Puede parar la intervención con una señal, y se respeta","DR","0","ya",3,
 "Pacientes en circuito de miedo y abandonos","verde","C5"),
("A53","G5","Aviso antes de ejecutar cualquier cambio de coste sobre el plan aprobado",
 "Nunca le llega una factura que no esperaba","GER","0","ya",4,
 "Desviaciones comunicadas antes de ejecutar","verde","—"),
("A54","G5","Documento de alta con lo conseguido y lo que toca a partir de ahora",
 "Sabe qué pasa el año que viene y el siguiente","DR","0","ya",3,
 "Altas con documento entregado","verde","C1"),
("A55","G5","Encuesta de experiencia al alta con una pregunta abierta que alguien lee",
 "Su queja llega a una persona con capacidad de cambiar algo","RAC","0","trim",2,
 "Respuestas y acciones abiertas a partir de ellas","verde","—"),
("A56","G5","Política de devolución en supuestos tasados, resuelta sin discusión y sin abogado",
 "Sabe de antemano cuándo se le devuelve el dinero","DG","€€","trim",3,
 "Devoluciones y días hasta resolver","amarillo","—"),
# ---------------------------------------------------------------- G6
("A57","G6","Giraldo Te Cuida: programa anual de mantenimiento, revisión y prioridad de agenda",
 "Su tratamiento se vigila en vez de olvidarse","DC","€€","ya",5,
 "Altas incorporadas al programa","amarillo","C1"),
("A58","G6","La Carta del Tercer Año: se escribe para confirmar que aquello sigue funcionando, no para vender nada",
 "Recibe una carta que no le pide dinero","DG","€","año",3,
 "Cartas enviadas y respuestas espontáneas","verde","C1"),
("A59","G6","Revisión sistemática que evita la cirugía: se llama por criterio clínico, no por calendario comercial",
 "Le llaman antes de que el problema cueste una cirugía","HIG","€€","ya",5,
 "Revisiones hechas y hallazgos precoces","amarillo","C6"),
("A60","G6","El Día de los que no Volvieron: una jornada al año para reabrir planes abandonados, sin presión y sin oferta",
 "Puede volver sin dar explicaciones ni sentirse juzgado","RAC","€","año",3,
 "Planes reabiertos y aceptados","amarillo","C3"),
("A61","G6","Rescate del paciente dormido por antigüedad y por riesgo clínico, en ese orden",
 "Le llaman porque su caso lo pide, no porque toque campaña","RAC","€","trim",4,
 "Dormidos contactados y reactivados","amarillo","C3"),
("A62","G6","Entrevista de salida al paciente que se va, sin ningún intento de retenerle",
 "Se le pregunta por qué se va y no se le retiene a la fuerza","GER","0","trim",2,
 "Entrevistas hechas sobre bajas","verde","—"),
("A63","G6","Aviso de mantenimiento por tipo de prótesis y fecha de colocación",
 "Le avisan cuando toca, aunque él lo haya olvidado","HIG","€","trim",3,
 "Avisos enviados y citas generadas","amarillo","C6"),
("A64","G6","Cadencia de higiene profesional según riesgo individual, no según calendario comercial",
 "Viene las veces que necesita, ni una más","HIG","0","trim",3,
 "Pacientes con cadencia asignada por riesgo","verde","C6"),
("A65","G6","Recuperación del producto pendiente heredado: caja ya cobrada que hay que convertir en producción",
 "Recibe el tratamiento que ya pagó a la titularidad anterior","GER","€","ya",5,
 "Producto pendiente convertido","amarillo","—"),
("A66","G6","Contacto anual con el paciente sin tratamiento activo, con algo útil y sin oferta",
 "Sabe que seguimos aquí sin que le persigan","RAC","€","año",2,
 "Contactos hechos y bajas de lista","amarillo","—"),
# ---------------------------------------------------------------- G7
("A67","G7","Prescripción de pacientes: se pide de frente, se agradece siempre y no se paga nunca",
 "Recomienda sin cobrar, que es la única forma de que su palabra valga","RAC","€","ya",4,
 "Primeras visitas con origen «prescripción»","amarillo","C8"),
("A68","G7","Red de derivación con médicos de familia, odontólogos generalistas y protésicos",
 "Su médico le manda a un sitio concreto y no a buscar en internet","DG","€€€","trim",4,
 "Derivadores activos y visitas derivadas","naranja","C4"),
("A69","G7","Acuerdo con cofradías y armadores: revisión antes del embarque",
 "No embarca con un problema que va a estallar a mil millas de un dentista","GER","€€","trim",4,
 "Revisiones previas al embarque","amarillo","—"),
("A70","G7","Campaña de Mar: ventana de tratamiento en tierra, ajustada al calendario real de las campañas de pesca",
 "Se trata en las semanas en que está en tierra, sin perder marea","GER","€€€","año",4,
 "Tratamientos completados dentro de ventana","amarillo","—"),
("A71","G7","Informe de aptitud dental para el embarque, dirigido al propio tripulante",
 "Embarca con un papel que dice cómo tiene la boca","DR","€","año",3,
 "Informes emitidos","naranja","—"),
("A72","G7","Protocolo de urgencia dental a distancia y contenido del botiquín de a bordo",
 "Sabe qué hacer si le duele una muela a tres días de puerto","DR","€","año",2,
 "Consultas a distancia atendidas","naranja","—"),
("A73","G7","Convenio con residencias y servicios de ayuda en el hogar",
 "Alguien lleva la boca de un dependiente que no puede ir solo","DC","€€","año",3,
 "Convenios activos y pacientes atendidos","amarillo","—"),
("A74","G7","Alianza con clubes deportivos: férulas de protección y revisión de temporada",
 "Su hijo juega con la boca protegida","HIG","€€","año",2,
 "Férulas hechas y equipos revisados","verde","—"),
("A75","G7","Acuerdo con empresas: revisión anual como retribución en especie para la plantilla",
 "Le revisan la boca sin pedir un día libre","GER","€€","año",3,
 "Empresas con acuerdo y trabajadores atendidos","amarillo","—"),
("A76","G7","Presencia como docente en colegio profesional y formación de posgrado",
 "Le trata quien enseña a otros a hacerlo","DR","€€","estruct",2,
 "Horas de docencia impartidas","verde","—"),
]

BANDA = {"0": (0, 0), "€": (0, 1000), "€€": (1000, 5000), "€€€": (5000, 15000), "€€€€": (15000, 40000)}
PLAZO = {"ya": "Ya", "trim": "Un trimestre", "año": "Un año", "estruct": "Estructural"}
PUESTO = {"DG": "Dirección General", "GER": "Gerencia", "DC": "Dirección de Centros",
          "REC": "Recepción", "RAC": "RAC", "DR": "Doctor", "HIG": "Higienista"}


def campos(a):
    c = dict(zip(("cod", "grupo", "accion", "gana", "quien", "coste",
                  "plazo", "efecto", "indicador", "sem", "campana"), a))
    c["coste_max"] = BANDA[c["coste"]][1]
    return c


def calcula():
    acciones = [campos(a) for a in A]
    por_grupo = {g[0]: [x for x in acciones if x["grupo"] == g[0]] for g in GRUPOS}
    sin_coste = [x for x in acciones if x["coste"] == "0"]
    inmediatas = [x for x in acciones if x["plazo"] == "ya"]
    con_campana = [x for x in acciones if x["campana"] != "—"]
    return {
        "acciones": acciones,
        "grupos": GRUPOS,
        "estados": ESTADOS,
        "por_grupo": {k: len(v) for k, v in por_grupo.items()},
        "total": len(acciones),
        "sin_coste": len(sin_coste),
        "inmediatas": len(inmediatas),
        "con_campana": len(con_campana),
        "fuera_de_cartera": len(acciones) - len(con_campana),
        "techo_anual": sum(x["coste_max"] for x in acciones),
        "por_semaforo": {s: len([x for x in acciones if x["sem"] == s])
                         for s in ("verde", "amarillo", "naranja")},
        "por_puesto": {p: len([x for x in acciones if x["quien"] == p]) for p in PUESTO},
    }


def _integridad(d):
    """Ninguna acción entra sin decir qué gana el paciente. Es la regla del plan
    y se comprueba aquí, no en la revisión de estilo."""
    codigos = [x["cod"] for x in d["acciones"]]
    assert len(set(codigos)) == len(codigos), "hay códigos repetidos"
    assert codigos == sorted(codigos), "los códigos no van en orden"
    for x in d["acciones"]:
        assert x["gana"] and len(x["gana"]) > 20, "%s no dice qué gana el paciente" % x["cod"]
        assert x["indicador"], "%s no mueve ningún número" % x["cod"]
        assert x["quien"] in PUESTO, "%s no tiene dueño válido" % x["cod"]
        assert x["sem"] in ("verde", "amarillo", "naranja"), x["cod"]


def main():
    d = calcula()
    _integridad(d)
    if "--json" in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return
    print("CATÁLOGO DE ACCIONES · %d acciones en %d grupos\n" % (d["total"], len(GRUPOS)))
    for cod, estados, titulo, _ in GRUPOS:
        print("%s · %-34s %s  ·  %d acciones" % (cod, titulo, estados, d["por_grupo"][cod]))
        for x in d["acciones"]:
            if x["grupo"] != cod:
                continue
            print("   %s  %-4s %-5s ef%d  %-9s %s"
                  % (x["cod"], x["coste"], x["plazo"], x["efecto"],
                     x["campana"] if x["campana"] != "—" else "", x["accion"][:64]))
        print()
    print("SIN COSTE DIRECTO ...... %d de %d acciones" % (d["sin_coste"], d["total"]))
    print("EJECUTABLES YA ......... %d" % d["inmediatas"])
    print("DENTRO DE LA CARTERA ... %d  ·  fuera de ella: %d"
          % (d["con_campana"], d["fuera_de_cartera"]))
    print("TECHO DE GASTO ANUAL ... %s €  si se activara todo el catálogo"
          % "{:,}".format(d["techo_anual"]).replace(",", "."))
    print("SEMÁFORO LEGAL ......... " + " · ".join("%s %d" % (k, v) for k, v in d["por_semaforo"].items()))


if __name__ == "__main__":
    main()

# Aquí se guardan todas las clases creadas

import pygame
import pygame_widgets
from threading import Thread
import time
from Constantes import *
from Funciones import *


# Objeto animador
class Animador(object):
    stop_thread = False  # Flag que señala al thread de terminar

    def __init__(self, obj_anim, timeout, target, identificador):
        """
        :param obj_anim: Objeto que se quiere animar, el que se escoja
        :param timeout: Tiempo que dura un loop de animación
        :param target: Lista [Parametro por modificar = Valor objetivo]
        :param identificador: ID que identifica el tipo de animación que es
        """
        self.obj_anim = obj_anim
        self.timeout = timeout
        self.target = target
        self.id = identificador  # ID podría ser palabra reservada. Posible BUG OJO!
        self.thread = Thread()  # Objeto Thread donde se ejecutará el loop de animación
        self.busy = False  # Será True mientras se ejecute el Thread

    # Asigna a thread la funcion loop y luego arranca el thread
    def start(self):
        if not self.busy:
            self.thread = Thread(target=self.loop)
            self.thread.start()

    # Bucle de animación
    def loop(self):
        # Evitamos multiples instancia del mismo thread
        if not self.busy:
            self.busy = True

            # Este clock limitará el numero de ejecuciones por segundo del calculo de la animación
            clock = pygame.time.Clock()

            # Comprobamos si estamos trabajando con un numero (valor individual), o un lista/tuple (secuencia)
            num_inicial = 'nada'
            tup_inicial = []

            if self.target[0] in ANIMABLES_NUM:
                num_inicial = self.obj_anim.get(self.target[0])
            elif self.target[0] in ANIMABLES_TUP:
                tup_inicial = self.obj_anim.get(self.target[0])

            # Nos guardamos el tiempo de inicio del bucle, para poder cumplir el timeout
            start_time = time.time()

            # Bucle de animacón en sí
            while time.time() - start_time < self.timeout:
                # Nº de calculos por segundo
                clock.tick(30)

                # Comprobamos si el flag nos indica que hay que parar
                if self.stop_thread:
                    self.stop_thread = False
                    self.busy = False
                    return

                # Decide la proporcionalidad del incremento/decremento
                step = (time.time() - start_time) / self.timeout

                # Animación de un valor numerico
                if not num_inicial == 'nada':
                    new_value = num_inicial + step * (self.target[1] - num_inicial)
                    self.obj_anim.set(self.target[0], new_value)
                # Animación de un valor secuencial
                elif tup_inicial:
                    new_value = []
                    for i in range(len(tup_inicial)):
                        new_value.append(tup_inicial[i] + step * (self.target[1][i] - tup_inicial[i]))
                    self.obj_anim.set(self.target[0], new_value)

            # Nos aseguramos que al acabar el valor es exactamente el que queriamos
            self.obj_anim.set(self.target[0], self.target[1])

        self.busy = False


# Base de cada jugador. Donde está el castillo, la vida, etc.
# Maneja las torres, la muralla, textos y numeros
class Base(pygame.sprite.Sprite):
    def __init__(self, x, y, mult_ancho, mult_alto, torre_izq, torre_der, torre_cen, muralla, hp,
                 texto_hp, hp_muro, texto_hp_muro):
        """
        :param x: Coordenada x
        :param y: Coordenada y
        :param mult_ancho: Multiplicador de anchura
        :param mult_alto: Multiplicador de altura
        :param torre_izq: Objeto Torre que representa la torre de la izquierda
        :param torre_der: Objeto Torre que representa la torre de la derecha
        :param torre_cen: Objeto Torre que representa la torre central
        :param muralla: Objeto Torre que representa la muralla
        :param hp: Numero .Marca la vida del castillo
        :param texto_hp: Objeto TextoColgado que representa hp
        :param hp_muro: Numero. Marca la vida de la muralla
        :param texto_hp_muro: Objeto TextoColgado que representa hp_muro
        """
        super().__init__()
        self.x = x
        self.y = y
        self.mult_ancho = mult_ancho
        self.mult_alto = mult_alto
        self.torre_izq = torre_izq
        self.torre_der = torre_der
        self.torre_cen = torre_cen
        self.muralla = muralla
        self.hp = hp
        self.texto_hp = texto_hp
        self.hp_muro = hp_muro
        self.texto_hp_muro = texto_hp_muro

        self.anim = {}  # Diccionario con objetos Animador

    def get(self, attr):
        if attr == 'hp':
            return self.hp
        elif attr == 'hp_muro':
            return self.hp_muro

    def set(self, attr, value):
        if attr == 'hp':
            self.hp = value
        elif attr == 'hp_muro':
            self.hp_muro = value

    # Multiplica el ancho y alto de los objets Torre por sus multiplicadores
    def update(self, win):
        # Reparte el daño entre muralla y las torres y calcula los offsets
        self.muralla.y_off = (self.muralla.alto * (100 - self.get('hp_muro')) / 100)
        if self.hp >= 70:
            self.torre_izq.y_off = 0
            self.torre_cen.y_off = 0
            self.torre_der.y_off = (self.torre_der.alto * (100 - self.get('hp')) / 30)
        elif self.hp >= 40:
            self.torre_izq.y_off = (self.torre_izq.alto * (70 - self.get('hp')) / 30)
            self.torre_cen.y_off = 0
            self.torre_der.y_off = self.torre_der.alto
        elif self.hp > 0:
            self.torre_izq.y_off = self.torre_izq.alto
            self.torre_cen.y_off = (self.torre_cen.alto * (40 - self.get('hp')) / 40)
            self.torre_der.y_off = self.torre_der.alto
        else:
            self.torre_izq.y_off = self.torre_izq.alto
            self.torre_cen.y_off = self.torre_cen.alto
            self.torre_der.y_off = self.torre_der.alto

        # Predispone las torres y muras del castillo
        for a in [self.torre_cen, self.torre_der, self.torre_izq, self.muralla]:
            a.ancho = int(a.ancho_base * self.mult_ancho)
            a.alto = int(a.alto_base * self.mult_alto)
            a.x = self.x
            a.y = self.y

        # Añade offset por hundimiento
        self.torre_izq.y = self.y + self.torre_cen.alto - self.torre_izq.alto + self.torre_izq.y_off
        self.torre_izq.x = self.x - self.muralla.ancho / 2 + self.torre_cen.ancho / 2 + self.torre_izq.ancho
        self.torre_der.y = self.y + self.torre_cen.alto - self.torre_der.alto + self.torre_der.y_off
        self.torre_cen.y += self.torre_cen.y_off
        self.torre_der.x = self.x + self.muralla.ancho / 2 - self.torre_cen.ancho / 2 - self.torre_der.ancho * 2 / 3
        self.muralla.y = self.y + self.torre_cen.alto - self.muralla.alto + self.muralla.y_off
        self.muralla.x = self.x - self.muralla.ancho / 2 + self.torre_cen.ancho / 2

        # Ponemos el suelo debajo, para esconder lo que se hunde.
        # Temporal, el suelo irá por separado (o no...)
        pygame.draw.rect(win, VERDE_CLARO,
                         (self.x - self.muralla.ancho / 2 + self.torre_cen.ancho / 2,
                          self.y + self.torre_cen.alto - 1,
                          self.muralla.ancho, self.torre_cen.alto), 0)

    # Reescribe el texto
    def redraw(self, win):
        self.texto_hp.valor = self.hp
        self.texto_hp_muro.valor = self.hp_muro
        self.texto_hp.renderSelf()
        self.texto_hp_muro.renderSelf()
        win.blit(self.texto_hp.texto, (self.x, self.y))
        win.blit(self.texto_hp_muro.texto, (self.x + 50, self.y))

    # Saber si el ratón se encuentra por encima
    def mouseOver(self, pos):
        pass  # LLamar mouseOver de otros objetos

    # Cuelga objetos sobre este objeto, para poder ser usado a traves de este objeto
    # Por ejemplo colgar distintos tipos de animaciones
    def loadObject(self, objeto):
        if type(objeto) == Animador:
            self.anim[objeto.id] = objeto


# Las torres. Tienen puntos de vida HP y tal
class Torre(pygame.sprite.Sprite):

    def __init__(self, enlace, x=1, y=1, ancho=1, alto=1):
        """
        :param dimen_base: Lista. Dimensiones base [ancho, alto]
        :param enlace: String. Ruta a la imagen de la imagen
        :param coord: Lista. Coordenadas [x,y]
        """
        super().__init__()
        self.x = x
        self.x_off = 0
        self.y = y
        self.y_off = 0
        self.ancho = ancho
        self.ancho_base = ancho
        self.alto = alto
        self.alto_base = alto
        self.enlace = enlace
        self.icono = pygame.image.load(enlace)
        self.image = pygame.Surface([1, 1])
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    # Actualiza posición, escala, etc. Y vuelve a "pintar" el icono
    def update(self, win):
        self.rect.midbottom = [self.x, self.y]
        self.icono = pygame.image.load(self.enlace)
        self.icono = pygame.transform.scale(self.icono, (self.ancho, self.alto))

        # Escalar el "cuadrado" del sprite. Para DEBUG
        # self.image = pygame.transform.scale(self.image, (int(self.ancho / 1), int(self.alto / 1)))

        win.blit(self.icono, self.rect)


# Las cartas en si. Puedes hacer click en ellas y desaparecen tras usarse
class Carta(pygame.sprite.Sprite):
    overed = False  # Indica si está siendo sobrevolada por el raton
    expanding = False  # Indica si la carta se está expandiendo
    shrinking = False  # Indica si la carta se está encojiendo

    def __init__(self, coord, dimen, color, tipo, descr, link_icono):
        """
        :param coord: Lista. Coordenadas [x,y]
        :param dimen: Lista. Dimensiones [ancho,alto]
        :param color: Color de fondo
        :param tipo: String. Tipo de carta. Identificador de algun tipo
        :param descr: Objeto TextoColgado. Muestra el nombre de la carta
        :param link_icono: String. Ruta a la imagen del icono
        """
        super().__init__()
        self.coord = coord
        self.dimen = dimen
        self.color = color
        self.icono = pygame.image.load(link_icono)
        self.link_icono = link_icono
        self.image = pygame.Surface(dimen)
        self.rect = self.image.get_rect()
        self.rect.center = coord
        self.link_icono = link_icono
        self.descr = descr
        self.tipo = tipo
        self.anim = {}  # Diccionario con objetos Animador

    def set(self, attr, value):
        if attr == 'dimen':
            self.dimen = value

    def get(self, attr):
        if attr == 'dimen':
            return self.dimen

    # Detecta si el ratón está por encima del objeto
    def mouseOver(self, pos):
        return self.rect.collidepoint(pos)

    # Actualiza graficamente el objeto
    def update(self, win):
        self.animSelf()
        self.image = pygame.Surface(self.dimen)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = [self.coord[0], self.coord[1]]
        self.icono = pygame.image.load(self.link_icono)
        self.icono = pygame.transform.scale(self.icono, [int(self.dimen[0]), int(self.dimen[1])])

        self.overed = self.rect.collidepoint(pygame.mouse.get_pos())

        # Actualiza graficamente los textos del objeto

    def redraw(self, win):
        win.blit(self.icono, (self.coord[0] - self.dimen[0] / 2, self.coord[1] - self.dimen[1] / 2))
        self.descr.renderSelf()
        win.blit(self.descr.texto, (self.coord[0] + self.dimen[0] / 8, self.coord[1] - self.dimen[1] / 5))

    # Gestiona animaciones de forma pasiva y automatica
    def animSelf(self):
        if self.overed:
            if not self.expanding:
                self.expanding = True
                self.shrinking = False
                self.anim['encojer'].stop_thread = True
                self.anim['expandir'].stop_thread = False
                self.anim['expandir'].start()
        else:
            if self.expanding:
                self.expanding = False
                self.shrinking = True
                self.anim['expandir'].stop_thread = True
                self.anim['encojer'].stop_thread = False
                self.anim['encojer'].start()

    # Cuelga objetos sobre este objeto, para poder ser usado a traves de este objeto
    # Por ejemplo colgar distintos tipos de animaciones
    def loadObject(self, objeto):
        if type(objeto) == Animador:
            self.anim[objeto.id] = objeto


# Texto extra de otros objetos. Titulos, descripciones, etc.
# "Colgado" porque su posición será relativa al objeto del que se cuelgue
class TextoColgado(object):
    texto = ''

    def __init__(self, valor, font, color):
        self.valor = valor
        self.font = font
        self.color = color

    def renderSelf(self):
        self.texto = self.font.render(str(self.valor), 1, self.color)

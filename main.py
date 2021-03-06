# Crear objetos animadores que se cuelgan dentro de los objetos que se supone que animarán
# Poder llamar estos animadores a través del objeto dueño
# Crear animaciones para las cartas
# Expandir el tipo de variables que pueden manejar las animaciones
# Estabilizar las animaciones con FPS fijo
# Hello its me

import pygame
import pygame_widgets
import random
from Constantes import *
from Clases import *
from Funciones import *

# Creamos la ventana donde se muestra todo
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Test4')


# Mezcla las cartas
def shuffle():
    grupo_cartas.empty()
    # Generamos 8 cartas
    for i in range(8):
        # Escojemos al azar entre dos tipos de cartas
        if random.choice([True, False]):
            carta_n = Carta([100 + i * (WIDTH - 100) / 8, HEIGHT - 150], [90, 100], NEGRO, 'LADRILLO1', texto_reparar,
                            LADRILLO1)
        else:
            carta_n = Carta([100 + i * (WIDTH - 100) / 8, HEIGHT - 150], [90, 100], NEGRO, 'ESPADA1', texto_daño,
                            ESPADA1)
        # Creamos y añadimos las animaciones a la carta creada
        expandir_carta_n = Animador(carta_n, 0.3, ['dimen', [150, 150]], 'expandir')
        encojer_carta_n = Animador(carta_n, 0.3, ['dimen', [50, 50]], 'encojer')
        carta_n.loadObject(expandir_carta_n)
        carta_n.loadObject(encojer_carta_n)

        grupo_cartas.add(carta_n)


# "Pinta" la pantalla
def renderWindow():
    WIN.fill(AZUL_CLARO)

    # Mostramos las cartas
    grupo_cartas.update(WIN)
    grupo_cartas.draw(WIN)
    for carta in grupo_cartas:
        carta.redraw(WIN)

    # Mostramos las bases y torres
    grupo_base1.update(WIN)
    grupo_base1.draw(WIN)
    grupo_base2.update(WIN)
    grupo_base2.draw(WIN)
    for base in bases:
        base.update(WIN)
        base.redraw(WIN)

    # Testeo. Mostramos los widgets
    for widget in lWidgets:
        widget.draw()

    # Se actualiza la ventana
    pygame.display.update()


# Restringe un numero entre un minimo y un maximo
def clamp(numero, minimo=0, maximo=100):
    return max(min(numero, maximo), minimo)


# Gestiona la posición del raton respecto a otras entidades
def mouseHandler(pos):
    for carta in grupo_cartas:
        if carta.mouseOver(pos):
            cardHandler(carta.tipo)


# Gestiona las pulsaciones de teclas
def keyHandler(key):
    pass


# Gestiona la activación de botones y widgets
def botonHandler(tipo):
    if tipo == 1:
        if not bases[0].anim['resta hp'].busy:
            bases[0].anim['resta hp'].target = ['hp', clamp(bases[0].get('hp') - 25, 0, 100)]
            bases[0].anim['resta hp'].start()
    elif tipo == 2:
        if not bases[0].anim['resta hp_muro'].busy:
            bases[0].anim['resta hp_muro'].target = ['hp_muro', clamp(bases[0].get('hp_muro') - 25, 0, 100)]
            bases[0].anim['resta hp_muro'].start()


# Gestiona el uso de cartas
def cardHandler(tipo):
    if tipo == 'ESPADA1':
        if not bases[1].anim['resta hp'].busy:
            bases[1].anim['resta hp'].target = ['hp', clamp(bases[1].get('hp') - 25, 0, 100)]
            bases[1].anim['resta hp'].start()
    elif tipo == 'LADRILLO1':
        if not bases[0].anim['suma hp_muro'].busy:
            bases[0].anim['suma hp_muro'].target = ['hp_muro', clamp(bases[0].get('hp_muro') + 25, 0, 100)]
            bases[0].anim['suma hp_muro'].start()


# Genera los castillos al principio
def generaCastillos():
    for i in range(2):
        torrel = Torre(TORRESENCILLA2, 1, 1, 25, 125)
        torrer = Torre(TORRESENCILLA2, 1, 1, 25, 125)
        torrec = Torre(TORRESENCILLA2, 1, 1, 30, 150)
        muralla = Torre(MURALLA2, 1, 1, 175, 55)
        hp = 100
        hp_texto = TextoColgado(100, TEST_FONT_DESCR, AZUL)
        hp_muro = 100
        hp_muro_texto = TextoColgado(100, TEST_FONT_DESCR, ROJO)

        if i == 0:
            grupo_base1.add(torrel, torrer, torrec, muralla)
        else:
            grupo_base2.add(torrel, torrer, torrec, muralla)

        base = Base(125 + i * (WIDTH - 250), 150, 1, 1, torrel, torrer, torrec, muralla, hp, hp_texto, hp_muro,
                    hp_muro_texto)
        bases.append(base)
        anim_base1 = Animador(bases[i], 1.2, ['hp', bases[i].get('hp') - 5], 'resta hp')
        anim_base2 = Animador(bases[i], 1.2, ['hp', bases[i].get('hp') + 5], 'suma hp')
        anim_mura1 = Animador(bases[i], 1.2, ['hp_muro', bases[i].get('hp_muro') - 5], 'resta hp_muro')
        anim_mura2 = Animador(bases[i], 1.2, ['hp_muro', bases[i].get('hp_muro') + 5], 'suma hp_muro')
        base.loadObject(anim_base1)
        base.loadObject(anim_base2)
        base.loadObject(anim_mura1)
        base.loadObject(anim_mura2)


# Grupos de sprites para las torres de las dos bases
grupo_base1 = pygame.sprite.Group()
grupo_base2 = pygame.sprite.Group()
# Grupo para las dos bases
bases = []
# Grupo de sprites para las cartas
grupo_cartas = pygame.sprite.Group()
# Texto para las cartas
texto_daño = TextoColgado('Daño', TEST_FONT_DESCR, ROJO)
texto_reparar = TextoColgado('Reparar', TEST_FONT_DESCR, AZUL)

# Barajamos las cartas una primera vez, y creamos los castillos
shuffle()
generaCastillos()

# Widget para testear
boton_damage = pygame_widgets.Button(WIN, 250, 300, 125, 40, text='Dañar castillo', onClick=botonHandler,
                                     onClickParams=[1])
boton_damage_muro = pygame_widgets.Button(WIN, 250, 350, 125, 40, text='Dañar muras', onClick=botonHandler,
                                          onClickParams=[2])
boton_shuffle = pygame_widgets.Button(WIN, 450, 325, 125, 40, text='Cartas nuevas', onClick=shuffle)

lWidgets = [boton_damage, boton_damage_muro, boton_shuffle]


def main():
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(30)
        # Comprobamos que eventos han ocurrido y actuamos respecto a ellos
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseHandler(pygame.mouse.get_pos())
        keyHandler(pygame.key.get_pressed())

        # Testeo
        for boton in lWidgets:
            boton.listen(events)

        renderWindow()
    pygame.quit()


if __name__ == '__main__':
    main()

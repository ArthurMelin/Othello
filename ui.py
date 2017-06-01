################################################################################
#                                                                              #
# ui.py : Module qui contient des fonctions permettant d'afficher différentes  #
#     interfaces et qui contrôle les évènements de la fenêtre du jeu           #
#     (principalement ceux générés par la souris)                              #
#                                                                              #
################################################################################

import time
from sdl2 import *

import display

# ============================================================================ #
# CONSTANTES                                                                   #
# ============================================================================ #

# Valeur renvoyée par certaines fonctions de ce module indiquant à l'appelant
# que l'utilisateur souhaite fermer la fenêtre du jeu et qu'il faut donc arrêter
# le programme
SIG_CLOSE_WINDOW = -1

# ============================================================================ #
# FONCTIONS                                                                    #
# ============================================================================ #

def Init():
# Fonction qui initialise l'interface graphique en initialisant le sous-système
# évènement et également le module display
# AUCUN PARAMÈTRE

    if SDL_InitSubSystem(SDL_INIT_EVENTS) != 0:
        raise Exception("Erreur d'initialisation de SDL2 (Évènements) : " +
                        SDL_GetError().decode())
    display.Init()

# ============================================================================ #

def WaitClick(board, ui, data):
# Fonction qui attend un clic dans la fenêtre et renvoit ses coordonnées (ou
# SIG_CLOSE_WINDOW si la fenêtre a été fermée)
# PARAMÈTRES:
#     board : tableau 2D des cases du plateau à afficher derrière l'interface
#     ui : valeur indiquant quelle interface doit être affichée
#     data : données supplémentaires à transmettre à display.DrawUI()

    # Initialisation des différentes variables
    event = SDL_Event()

    # Variables de contrôle de la fréquence de raffraîchissement
    lastDraw = 0
    needDraw = True

    # Coordonnées du curseur dans la fenêtre et statut du bouton gauche
    mouse_x = -1
    mouse_y = -1
    mouse_dw = False

    while True:
        # Demande à la SDL si un évènement s'est produit et le cas échéant le
        # traite en fonction des informations qu'il contient pour suivre les
        # déplacements et les clics de la souris
        while SDL_PollEvent(event) != 0:
            if event.type == SDL_WINDOWEVENT:
                # L'utilisateur veut fermer la fenêtre, on renvoie
                # SIG_CLOSE_WINDOW pour indiquer que le programme doit s'arrêter
                if event.window.event == SDL_WINDOWEVENT_CLOSE:
                    return SIG_CLOSE_WINDOW
                # La souris quitte la fenêtre, on réinitialise les variables
                elif event.window.event == SDL_WINDOWEVENT_LEAVE:
                    mouse_x = -1
                    mouse_y = -1
                    mouse_dw = False
                    needDraw = True
                # La fenêtre revient au 1er plan, on doit réafficher son contenu
                elif event.window.event == SDL_WINDOWEVENT_FOCUS_GAINED:
                    needDraw = True
            # La souris a été déplacée dans la fenêtre
            elif event.type == SDL_MOUSEMOTION:
                mouse_x = event.motion.x
                mouse_y = event.motion.y
                mouse_dw = bool(event.motion.state & SDL_BUTTON_LMASK)
                needDraw = True
            # Le bouton gauche de la souris est pressé
            elif event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.button == SDL_BUTTON_LEFT:
                    mouse_x = event.button.x
                    mouse_y = event.button.y
                    mouse_dw = True
                    needDraw = True
            # Le bouton gauche de la souris est relaché = clic
            elif event.type == SDL_MOUSEBUTTONUP:
                if event.button.button == SDL_BUTTON_LEFT:
                    return (event.button.x, event.button.y)

        # Affiche le plateau et l'interface graphique tout en faisant en sorte
        # d'alléger la charge processeur en ne raffraîchissant l'affichage que
        # lorsque c'est nécessaire et à la fréquence maximale de 60Hz (fréquence
        # de raffraîchissement des écrans la plus commune)
        if needDraw and (time.time() - lastDraw) >= 1/60:
            display.DrawBoard(board)
            display.DrawUI(ui, mouse_x, mouse_y, mouse_dw, data)
            display.UpdateWindow()
            needDraw = False
            lastDraw = time.time()
        else:
            time.sleep(1/120)
    return

# ============================================================================ #

def WaitPlay(board, possibilities, playerColor):
# Fonction qui attend qu'un joueur joue son tour et renvoie les coordonnées du
# pion qu'il a posé
# PARAMÈTRES:
#     board : tableau 2D qui représente les cases du plateau
#     possibilities : liste des cases où le joueur peut placer un pion
#     playerColor : couleur des pions du joueur

    while True:
        click = WaitClick(board, display.UI_MODE_INGAME,
                          [possibilities, playerColor])
        # Si l'utilisateur ferme la fenêtre, on transmet le signal
        if click == SIG_CLOSE_WINDOW:
            return SIG_CLOSE_WINDOW
        else:
            # On calcule les coordonnées de la case qui a été sélectionnée
            tile_x = int((click[0]-32) / 66)
            tile_y = int((click[1]-32) / 66)
            # On vérifie si le joueur peut jouer sur cette case, si c'est le
            # cas on renvoit ses coordonnées
            for possibility in possibilities:
                if possibility[0] == tile_x and possibility[1] == tile_y:
                    return possibility
    return

# ============================================================================ #

def DisplayScores(board, scores):
# Fonction qui affiche l'interface des scores, avec 2 boutons pour lancer une
# nouvelle partie ou quitter le jeu
# Renvoie SIG_CLOSE_WINDOW quand le joueur ferme la fenêtre ou clique sur le
# bouton "Quitter le jeu"
# Renvoie None si le joueur clique sur le bouton "Nouvelle partie"
# PARAMÈTRES:
#     board : tableau 2D qui représente les cases du plateau
#     scores : liste qui contient le score de la partie qui vient de se finir

    while True:
        # On attend un clic du joueur
        click = WaitClick(board, display.UI_MODE_SCORES, scores)

        # Si le joueur a fermé la fenêtre on transmet le signal
        if click == SIG_CLOSE_WINDOW:
            return SIG_CLOSE_WINDOW
        else:
            # Si le joueur a cliqué sur "Nouvelle partie", on renvoit None
            if display.MouseIn(click[0], click[1],  70, 295, 370, 408):
                return
            # Si le joueur a cliqué sur "Quitter le jeu", on renvoit le signal
            # SIG_CLOSE_WINDOW
            if display.MouseIn(click[0], click[1], 328, 521, 370, 408):
                return SIG_CLOSE_WINDOW
    return

# ============================================================================ #

def Quit():
# Fonction qui nettoie le module display et quitte le sous-système évènement de
# la SDL
# AUCUN PARAMÈTRE

    display.Quit()
    SDL_QuitSubSystem(SDL_INIT_EVENTS)

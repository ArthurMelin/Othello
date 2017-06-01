################################################################################
#                                                                              #
# game.py : Module qui permet de jouer au jeu de l'Othello                     #
#                                                                              #
################################################################################

from math import fabs

# ============================================================================ #
# CONSTANTES                                                                   #
# ============================================================================ #

# Constantes utilisée pour identifier le contenu d'une case
TILE_EMPTY = 0  # Case vide
TILE_LIGHT = 1  # Pion blanc
TILE_DARK  = 2  # Pion noir

# Tableau 2D des positions de départ des pions d'une partie d'Othello classique
BOARD_INIT = [[0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 2, 0, 0, 0],
              [0, 0, 0, 2, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0]]

# ============================================================================ #
# FONCTIONS                                                                    #
# ============================================================================ #

def SwitchPlayer(currentPlayer):
# Fonction qui renvoie le numéro du joueur opposé à celui donné en paramètre :
# SwitchPlayer(1) = 2   et   SwitchPlayer(2) = 1
# PARAMÈTRES:
#     currentPlayer : numéro du joueur actuel

    return currentPlayer - (2*currentPlayer) + 3

# ============================================================================ #

def Walk(direction, way):
# Fonction qui fait avancer ou reculer un 'vecteur' d'une case dans la direction
# vers laquelle il va déjà.
# PARAMÈTRES:
#     direction : vecteur à modifier
#     way : sens dans lequel on doit aller (1:avancer; -1:reculer)

    for i in range(len(direction)):
        if direction[i] != 0:
            # Ajoute 1 ou -1 en fonction du sens où on va et du sens du vecteur
            direction[i] += way * int(direction[i]/fabs(direction[i]))
    return

# ============================================================================ #

def GetMiddleDisks(board, x, y, color):
# Fonction qui trouve les pions qui pourraient être retourner lors du placement
# d'un pion à une position donnée et renvoie une liste de leurs coordonnées
# Paramètres: board : tableau 2D qui correspond au plateau
#     x : colonne où le pion serait placé
#     y : ligne où le pion serait placé
#     color : couleur du pion à placer

    # Liste des coordonnées des pions adverses entre le pion de départ en (x,y)
    # et un autre pion de la même couleur qu'on cherche ensuite
    middleDisks =  []
    # Toutes les directions et sens vers lesquels on doit chercher un pion qui
    # encadre des pions adverses
    directions = [[0,1], [1,1], [1,0], [1,-1], [0,-1], [-1,-1], [-1,0], [-1,1]]
    for direction in directions:
        # Coordonnées par défaut du pion encadrant, celle du pion de départ
        x_b, y_b = x, y

        # Boucle infinie qui recherche un pion encadrant jusqu'à en trouver un,
        # arriver sur une case vide, ou sortir du plateau
        while True:
            # Coordonnées du pion observé
            x_o, y_o = x+direction[0], y+direction[1]

            # Si on sort du plateau ou si la case est vide, on sort de la boucle
            if not (0 <= x_o <= 7 and 0 <= y_o <= 7) \
            or board[y_o][x_o] == TILE_EMPTY:
                break

            # Si on trouve un pion encadrant, on enregistre ses coordonnées et
            # on sort de la boucle
            if board[y_o][x_o] == color:
                x_b, y_b = x_o, y_o

                # Tant que le pion en (x_b,y_b) n'est pas celui de départ, on
                # recule et on ajoute les coordonnées des cases traversées
                # (contenant des pions adverses retournables) à la liste
                while True:
                    Walk(direction,-1)
                    x_b, y_b = x+direction[0], y+direction[1]
                    if x_b == x and y_b == y:
                        break
                    middleDisks.append([x_b,y_b])
                break

            # Sinon, on avance d'une case le 'vecteur' direction
            Walk(direction,1)

    return middleDisks

# ============================================================================ #

def GetPlayPossibilities(board, color):
# Fonction qui cherche les possibilités de jeu d'un joueur sur le plateau
# PARAMÈTRES:
#     board : tableau 2D qui correspond aux cases du plateau
#     color : couleur des pions du joueur

    possibilities = []
    for y in range(8):
        for x in range(8):
            # Si en plaçant un pion dans cette case on peut retourner des pions
            # adverses et que cette case est vide, on l'ajoute à la liste
            if len(GetMiddleDisks(board, x, y, color)) > 0 \
            and board[y][x] == TILE_EMPTY:
                possibilities.append((x, y))
    return possibilities

# ============================================================================ #

def GetScore(board):
# Fonction qui calcule le score des joueurs en comptant leurs pions respectifs
# sur le plateau
# PARAMÈTRES:
#     board : tableau 2D qui correspond aux cases du plateau

    score = [0, 0]
    for y in range(8):
        for x in range(8):
            if board[y][x] == TILE_LIGHT:
                score[0] += 1
            elif board[y][x] == TILE_DARK:
                score[1] += 1
    return score

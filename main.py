################################################################################
#                                                                              #
# main.py : Module central du programme, supervise les différents sous-modules #
#     pour permettre de jouer au jeu de l'Othello dans une interface graphique #
#                                                                              #
################################################################################

# (Pour Windows) Configuration du chemin d'accès des DLLs de la SDL2 en fonction
# de l'architecture utilisée par Python
import platform, os
if platform.system() == "Windows":
    os.environ["PYSDL2_DLL_PATH"] = os.getcwd() + "\\sdl2-dll-" \
                                  + platform.architecture()[0]

import copy
import game, ui

# ============================================================================ #
# PROGRAMME PRINCIPAL                                                          #
# ============================================================================ #

# Initialisation de l'interface graphique
ui.Init()

# Boucle principale du jeu, continue tant que l'utilisateur n'a pas fermé le jeu
running = True
while running:
    # On (ré)initialise les variables de la partie:
    # On copie le tableau du plateau de départ
    board = copy.deepcopy(game.BOARD_INIT)
    # Le joueur noir commence en premier
    playerColor = game.TILE_DARK

    # Boucle d'une partie, continue tant que la partie n'est pas finie
    gameover = False
    while running and not gameover:
        # On récupère la liste des possibilités de jeu pour ce tour
        possibilities = game.GetPlayPossibilities(board, playerColor)

        # Si le joueur peut jouer ce tour
        if len(possibilities) > 0:
            # On attend que le joueur pose un pion
            play = ui.WaitPlay(board, possibilities, playerColor)

            # Si l'utilisateur a fermé la fenêtre on termine la partie et le
            # programme
            if play == ui.SIG_CLOSE_WINDOW:
                running = False
            else:
                # On place le pion du joueur dans le tableau du plateau
                board[play[1]][play[0]] = playerColor
                # On obtient la liste des pions qui sont retournés avec ce tour
                middleDisks = game.GetMiddleDisks(board, play[0], play[1],
                                                  playerColor)
                # On "retourne" chacun de ces pions dans le tableau du plateau
                for middleDisk in middleDisks:
                    board[middleDisk[1]][middleDisk[0]] = playerColor
        # Sinon, si l'autre joueur ne peut pas jouer non plus, la partie est
        # terminée
        elif len(game.GetPlayPossibilities(board,
                                          game.SwitchPlayer(playerColor))) == 0:
            # On affiche l'interface avec les scores des joueurs, si
            # l'utilisateur a décidé d'arrêter de jouer, on termine le programme
            # Sinon, la boucle de la partie s'arrête, et une nouvelle partie est
            # lancée
            if ui.DisplayScores(board, game.GetScore(board)) \
                                                         == ui.SIG_CLOSE_WINDOW:
                running = False
            else:
                gameover = True
        # On passe au joueur suivant avant de passer au tour suivant
        playerColor = game.SwitchPlayer(playerColor)

# On ferme la fenêtre et on nettoie la mémoire utilisée par l'interface
ui.Quit()

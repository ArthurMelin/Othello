################################################################################
#                                                                              #
# display.py : Module qui contrôlent toute la partie graphique du jeu, c'est   #
#     à dire la fenêtre du jeu, les textures et l'affichage du plateau et de   #
#     l'interface graphique                                                    #
#                                                                              #
################################################################################

# NOTE : Les 'b' précédents certaines chaînes de caractères ainsi que les
# fonctions .encode() et .decode() sont utilisés pour faire correspondre des
# chaînes de caractères et des chaînes d'octets représentant ces chaînes en
# UTF-8 pour les utiliser avec la SDL2

from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *

# ============================================================================ #
# CONSTANTES                                                                   #
# ============================================================================ #

# Valeurs utilisées par DrawUI() pour déterminer quelle interface afficher dans
# la fenêtre
UI_MODE_INGAME   = 0  # Mode jeu de l'interface
UI_MODE_SCORES   = 1  # Affiche le score de chaque joueur

# Couleurs d'arrière-plan des boutons des différentes interfaces
BUTTON_BG_COLOR = [SDL_Color(0x00, 0x40, 0xD0),
                   SDL_Color(0x08, 0x50, 0xE0),
                   SDL_Color(0x16, 0x60, 0xF0)]

# ============================================================================ #
# GLOBALES                                                                     #
# ============================================================================ #

# Objet qui correspond à la fenêtre du jeu
Window = None

# Tableau référençant les structures qui correspondent aux textures du jeu
# Format: [SDL_Surface : texture, str : nom du fichier]
Textures = [[None, "board.png"], # Cadre du plateau
            [None, "light.png"], # Pion blanc
            [None, "dark.png" ], # Pion noir
            [None, "tile.png" ]] # Fond d'une case du plateau

# Masque transparent qui est appliqué par dessus le plateau pour l'assombrir et
# afficher l'interface graphique
Mask = None

# Tableau référençant les polices d'écriture utilisés par l'interface
# Format: [TTF_Font : police, str : nom du fichier, int : taille de la police]
Fonts = [[None, "tahoma.ttf", 32], # Police pour la plupart des textes
         [None, "tahoma.ttf", 40], # Police pour des éléments plus grands
         [None, "Alegreya_SC-M.ttf", 32]] # Police pour les boutons

# Tableau qui contiendra les caches de surfaces et les informations de validité
# pour chaque type d'interface utilisateur pour éviter de les regénérer à chaque
# raffraîchissement
UiCaches = [[None, None], # INGAME -> pions avec transparence
            [None, None]] # SCORES -> textes et boutons de l'interface

# ============================================================================ #
# FONCTIONS                                                                    #
# ============================================================================ #

def MouseIn(mouse_x, mouse_y, start_x, end_x, start_y, end_y):
# Fonction qui vérifie si la souris survole une zone specifiée
# PARAMÈTRES:
#     mouse_x : coordonnée x de la souris dans la fenêtre
#     mouse_y : coordonnée y de la souris dans la fenêtre
#     start_x : coordonnée x du début de la zone
#     end_x : coordonnée x de fin de la zone
#     start_y : coordonnée y du début de la zone
#     end_y : coordonnée y de fin de la zone
    return True if start_x <= mouse_x <= end_x and start_y <= mouse_y <= end_y \
        else False

def Init():
# Fonction qui initialise les librairies externes, charge les textures et la
# police de texte de l'interface, puis ouvre la fenêtre du jeu. Cette fonction
# lève des exceptions si une erreur survient pour suspendre le programme.
# AUCUN PARAMÈTRE

    # On identifie les variables suivantes comme des globales puisque nous les
    # modifions dans cette fonction
    global Window, Textures, Mask, Fonts

    # Initialisation de la librairie SDL2 et de ses extensions
    if SDL_InitSubSystem(SDL_INIT_VIDEO) != 0:
        raise Exception("Erreur d'initialisation de SDL2 (Vidéo) : " +
                        SDL_GetError().decode())
    if TTF_Init() != 0:
        raise Exception("Erreur d'initialisation de SDL_TTF :" +
                        TTF_GetError().decode())
    if IMG_Init(IMG_INIT_PNG) != IMG_INIT_PNG:
        raise Exception("Erreur d'initialisation de SDL_Image : " +
                        IMG_GetError().decode())

    # Chargement des textures
    for texture in Textures:
        # On ouvre puis charge le fichier de texture
        rwops = SDL_RWFromFile(texture[1].encode(), b"r")
        texture[0] = IMG_Load_RW(rwops, True)
        # On vérifie que la texture a bien été chargée
        if not texture[0]:
            raise Exception("Erreur du chargement de la texture " + texture[1] +
                            " : " + IMG_GetError().decode())

    # On génère le masque transparent appliqué entre le plateau et l'interface
    Mask = SDL_CreateRGBSurface(0, 592, 592, 32,
                                0xFF, 0xFF<<8, 0xFF<<16, 0xFF<<24)
    SDL_FillRect(Mask, None, 0xA0000000) # (Noir - Opacité 60%)

    # Chargement des polices d'écriture pour l'interface graphique
    for font in Fonts:
        # On ouvre et on charge la police
        rwops = SDL_RWFromFile(font[1].encode(), b"r")
        font[0] = TTF_OpenFontRW(rwops, True, font[2])
        # On vérifié que la police a bien été chargée
        if not font[0]:
            raise Exception("Erreur du chargement de la police " + font[1] +
                            " : " + TTF_GetError().decode())

    # Ouverture de la fenêtre du jeu (taille 592x592px, centrée sur l'écran)
    # avec le pion blanc comme icône
    Window = SDL_CreateWindow(b"Jeu de l'Othello", SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, 592, 592, 0)
    SDL_SetWindowIcon(Window, Textures[1][0])

# ============================================================================ #

def DrawBoard(board):
# Fonction qui affiche le plateau avec les pions dans la fenêtre
# PARAMÈTRES:
#     board : tableau 2D qui correspond aux cases du plateau

    windowSurface = SDL_GetWindowSurface(Window)

    # Affichage du bord du plateau
    SDL_BlitSurface(Textures[0][0], None, windowSurface, None)

    # Affichage des cases du plateau
    for y in range(8):
        for x in range(8):
            # Structure qui décrit la position de la case dans la fenêtre
            rect = SDL_Rect(32 + x*66, 32 + y*66)
            # Affichage du fond de la case
            SDL_BlitSurface(Textures[3][0], None, windowSurface, rect)
            # Si la case n'est pas vide, on dessine le pion de la bonne couleur
            color = board[y][x]
            if color != 0:
                SDL_BlitSurface(Textures[color][0], None, windowSurface, rect)
    return

# ============================================================================ #

def DrawUI(ui, mouse_x, mouse_y, mouse_dw, data):
# Fonction qui affiche une interface graphique dans la fenêtre du jeu
# Chaque interface a son propre cache de surfaces lui permettant de
# gagner du temps de rendu en ne générant ces surfaces que lorsque c'est
# nécéssaire
# PARAMÈTRES:
#     ui : valeur qui indique quelle type d'interface afficher
#     mouse_x : coordonnée x de la souris dans la fenêtre (-1 si à l'extérieur)
#     mouse_y : coordonnée y de la souris dans la fenêtre (-1 si à l'extérieur)
#     mouse_dw : booléen indiquant si le bouton de la souris est pressé
#     data: complément de données utilisées par certaines interfaces (ex: score)

    windowSurface = SDL_GetWindowSurface(Window)
    uiCache = UiCaches[ui]

    # Interface 0 : UI_MODE_INGAME:
    # Mode qui affiche les indices de jeu pour le joueur actuel
    # data : [list : coordonnées des indices, int : couleur des pions du joueur]
    if ui == UI_MODE_INGAME:
        # Si cela n'a pas déjà été fait, on génère les surfaces des pions
        # transparents pour les indices et on les place dans le cache
        if uiCache[0] == None:
            uiCache[0] = []

            for i in range(6):
                uiCache[0].append(SDL_CreateRGBSurface(0, 66, 66, 32,
                                             0xFF, 0xFF<<8, 0xFF<<16, 0xFF<<24))
                # Pour i = {0;1;2} pion blanc, pour i = {3;4;5} pion noir
                SDL_BlitSurface(Textures[1+int(i/3)][0], None, uiCache[0][i],
                                None)

                # Pour i = {0;3} opacité 30%
                if i%3 == 0:
                    SDL_SetSurfaceAlphaMod(uiCache[0][i], 0x50)
                # Pour i = {1;4} opacité 60% (case survolée par la souris)
                elif i%3 == 1:
                    SDL_SetSurfaceAlphaMod(uiCache[0][i], 0xA0)
                # Pour i = {2;5} opacité 80% (case selectonnée par la souris)
                else:
                    SDL_SetSurfaceAlphaMod(uiCache[0][i], 0xD0)


        # Affiche les indices de jeu d'un joueur s'ils ont été renseignés
        if data != None:
            for hint in data[0]:
                # Structure qui décrit la position de la case dans la fenêtre
                rect = SDL_Rect(32 + hint[0]*66, 32 + hint[1]*66)

                # Détecte si la case est survolée par la souris
                hovered = MouseIn(mouse_x, mouse_y,
                                  rect.x, rect.x+65, rect.y, rect.y + 65)

                # Si la case est survolée et que le bouton gauche de la souris
                # est pressé, la case est selectionnée
                selected = hovered and mouse_dw

                # Affiche la surface correspondante à la situation
                SDL_BlitSurface(uiCache[0][3*(data[1]-1) + hovered + selected],
                                None, windowSurface, rect)

    # Avant de dessiner d'autres types d'interfaces, on applique le masque
    # transparent qui assombri l'arrière-plan de ces interfaces par dessus le
    # plateau (déjà affiché par un appel précédent à DrawBoard())
    else:
        SDL_BlitSurface(Mask, None, windowSurface, None)

    # Interface 1 : UI_MODE_SCORES
    # Affiche les scores des joueurs, qui a gagné et deux boutons "Nouvelle
    # partie" et "Quitter le jeu"
    # data: [int : score joueur blanc, int : score joueur noir]
    if ui == UI_MODE_SCORES:
        # Si cela n'a pas déjà été fait, on génère les surfaces constantes de ce
        # mode et on les place dans le cache
        if uiCache[0] == None:
            # On initialise le cache de surfaces avec 7 emplacements
            # (initialisés par None)
            uiCache[0] = [None] * 7

            # Fond blanc de l'interface
            uiCache[0][0] = SDL_CreateRGBSurface(0, 592, 300, 32,
                                              0xFF, 0xFF<<8, 0xFF<<16, 0xFF<<24)
            SDL_FillRect(uiCache[0][0], None, 0xFFFFFFFF) # Blanc

            # On génère les différentes surfaces des textes de l'interface
            uiCache[0][1] = TTF_RenderUTF8_Shaded(Fonts[1][0],
                                                  "Partie terminée!".encode(),
                                                  SDL_Color(0x00,0x00,0x00),
                                                  SDL_Color(0xFF,0xFF,0xFF))
            uiCache[0][3] = TTF_RenderUTF8_Shaded(Fonts[0][0],
                                                  "a gagné".encode(),
                                                  SDL_Color(0x00,0x00,0x00),
                                                  SDL_Color(0xFF,0xFF,0xFF))
            uiCache[0][4] = TTF_RenderUTF8_Shaded(Fonts[0][0],
                                                  "Égalité".encode(),
                                                  SDL_Color(0x00,0x00,0x00),
                                                  SDL_Color(0xFF,0xFF,0xFF))

            # Initialisation des valeurs de vérification du cache:
            # Aucune des surfaces dynamique n'a été générée, donc on initialise
            # à -1 pour qu'elles soient générées plus tard
            uiCache[1] = [-1, -1, -1, -1]

        # Si la surface du score en cache ne correspond plus au score actuel
        # (score de la partie précédente), on la régénère
        if uiCache[1][2] != data[0] \
        or uiCache[1][3] != data[1]:
            # On libère la surface précédente
            SDL_FreeSurface(uiCache[0][2])
            # On formatte le texte affiché avec le score
            score_str = "{:>2d} - {:<2d}".format(data[0], data[1])
            # On génère la surface et on la place dans le cache
            uiCache[0][2] = TTF_RenderUTF8_Shaded(Fonts[0][0],
                                                  score_str.encode(),
                                                  SDL_Color(0x00,0x00,0x00),
                                                  SDL_Color(0xFF,0xFF,0xFF))
            # On met à jour les informations de validité du cache
            uiCache[1][2] = data[0]
            uiCache[1][3] = data[1]

        # On vérifie si la souris survole ou sélectionne un des boutons de
        # l'interface
        newgame_button_hovered = MouseIn(mouse_x, mouse_y, 70, 295, 370, 408)
        newgame_button_selected = newgame_button_hovered and mouse_dw
        quitgame_button_hovered = MouseIn(mouse_x, mouse_y, 328, 521, 370, 408)
        quitgame_button_selected = quitgame_button_hovered and mouse_dw

        # On régère la surface du bouton "Nouvelle partie" si son statut n'est
        # plus le même que celui de la surface dans le cache
        if newgame_button_hovered + newgame_button_selected != uiCache[1][0]:
            SDL_FreeSurface(uiCache[0][5])
            uiCache[0][5] = TTF_RenderUTF8_Shaded(Fonts[2][0],
                                                  " Nouvelle partie ".encode(),
                                                  SDL_Color(0x00,0x00,0x00),
                                       BUTTON_BG_COLOR[newgame_button_hovered +
                                                       newgame_button_selected])
            uiCache[1][0] = newgame_button_hovered + newgame_button_selected

        # De même pour le bouton "Quitter le jeu"
        if quitgame_button_hovered + quitgame_button_selected != uiCache[1][1]:
            SDL_FreeSurface(uiCache[0][6])
            uiCache[0][6] = TTF_RenderUTF8_Shaded(Fonts[2][0],
                                                  " Quitter le jeu ".encode(),
                                                  SDL_Color(0x00,0x00,0x00),
                                      BUTTON_BG_COLOR[quitgame_button_hovered +
                                                      quitgame_button_selected])
            uiCache[1][1] = quitgame_button_hovered + quitgame_button_selected

        # On affiche enfin les différentes surfaces dans la fenêtre
        # Fond blanc
        SDL_BlitSurface(uiCache[0][0], None, windowSurface, SDL_Rect(0,   146))
        # "Partie terminée"
        SDL_BlitSurface(uiCache[0][1], None, windowSurface, SDL_Rect(156, 160))
        # Score
        SDL_BlitSurface(uiCache[0][2], None, windowSurface, SDL_Rect(246, 242))
        SDL_BlitSurface(Textures[1][0], None, windowSurface, SDL_Rect(182,230))
        SDL_BlitSurface(Textures[2][0], None, windowSurface, SDL_Rect(346,230))

        # "X a gagné" ou "Égalité"
        if data[0] != data[1]:
            winner = 1 if data[0] > data[1] else 2
            SDL_BlitSurface(uiCache[0][3], None, windowSurface,
                            SDL_Rect(270, 302))
            SDL_BlitSurface(Textures[winner][0], None, windowSurface,
                            SDL_Rect(206,290))
        else:
            SDL_BlitSurface(uiCache[0][4], None, windowSurface,
                            SDL_Rect(248,302))

        # Bouton "Nouvelle partie"
        SDL_BlitSurface(uiCache[0][5], None, windowSurface, SDL_Rect(70,  370))
        # Bouton "Quitter le jeu"
        SDL_BlitSurface(uiCache[0][6], None, windowSurface, SDL_Rect(328, 370))
    return

# ============================================================================ #

def UpdateWindow():
# Fonction qui raffraîchit l'écran (les modifications effectuées sur la fenêtre
# avec SDL_BlitSurface() n'apparaissent pas spontanément)

    SDL_UpdateWindowSurface(Window)

# ============================================================================ #

def Quit():
# Fonction qui libère la mémoire utilisée par les surfaces, ferme la fenêtre du
# jeu et décharge les librairies externes.
# AUCUN PARAMÈTRE

    # On libère les différentes surfaces et les polices qui sont en mémoire
    for uiCache in UiCaches:
        if uiCache[0] != None:
            for surface in uiCache[0]:
                SDL_FreeSurface(surface)
    for texture in Textures:
        SDL_FreeSurface(texture[0])
    SDL_FreeSurface(Mask)

    for font in Fonts:
        TTF_CloseFont(font[0])

    # On ferme la fenêtre du jeu
    SDL_DestroyWindow(Window)

    # On libère les différentes librairies externes
    IMG_Quit()
    TTF_Quit()
    SDL_QuitSubSystem(SDL_INIT_VIDEO)

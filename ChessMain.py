import pygame 
import math as mt
from copy import copy
# list = [[1, 2, 3],
#         [4, 5, 6],
#         [7, 8, 9]]
# diagonal 1 = [list[x][x] for x in range(len(list))]
# diagonal 2 = [list[x][~x] for x in range(len(list))]
#
display_side = 600


class Label(object):
    def __init__(self, name):
        self.name = [8, 7, 6, 5, 4, 3, 2, 1][name] if type(name) == type(1) else name
        self.number = "abcdefgh".index(name) if type(name) == type("") else name
        self.pos = (self.number, 0) if type(name) == type("") else (0, self.number)
        x = pos_to_coor(self.pos)
        self.coor = x if type(name) == type("") else (x[0], x[1] + Cell.side*.8)

    def show(self):
        font = pygame.font.Font("Sitka.ttc", 100)
        labelSurface = font.render(str(self.name), True, DARK_GREEN)
        labelSurface = pygame.transform.scale(labelSurface, (round(Cell.side/5), round(Cell.side/5)))
        pygame.display.get_surface().blit(labelSurface, self.coor)

class Cell(object):
    """A cell class that has a color, position, piece , and belongs to a board object."""
    dis_side = display_side
    side = mt.sqrt((dis_side**2)/64) 
    def __init__(self, color, position, board, current_piece=None, attackable=False,x=None, y=None):
        if x != None or y != None:
            self.x = x
            self.y = y
        else: 
            self.x = position[0] * Cell.side
            self.y = position[1] * Cell.side
        self.color = color
        self.position = position
        self.board = board
        self.current_piece = current_piece
        self.attackable = {"white":False, "black":False}
        self.parent_attacker = {"white":set([]), "black":set([])}

    # setters
    def set_x(self, new_x):
        self.x = new_x

    def set_y(self, new_y):
        self.y = new_y

    def set_color(self, new_color):
        self.color = new_color

    def set_position(self, new_position):
        self.position = new_position

    def set_board(self, new_board):
        self.board = new_board

    def set_current_piece(self, new_piece):
        self.current_piece = new_piece

    def set_attackable(self, new_attack, grp):
        if type(grp) == type(""):
            self.attackable[grp] = new_attack
        else:
            if new_attack:
                self.parent_attacker[grp.get_group()].add(grp.get_position())
            else:
                self.parent_attacker[grp.get_group()].discard(grp.get_position())
        self.attackable[grp.get_group()] = new_attack

    # getters
    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_color(self, string=False):
        return self.color

    def get_position(self):
        return self.position

    def get_board(self):
        return self.board

    def get_current_piece(self):
        return self.current_piece

    def get_parent_attacker(self, grp):
        return self.parent_attacker[give_my_enemy(grp)]

    # a functoin that draws a square as a rectangle on the secreen
    def draw(self):
        pygame.draw.rect(pygame.display.get_surface(), self.color, [(self.x, self.y), (Cell.side, Cell.side)])
        # if self.attackable["black"]:
        #     pygame.draw.rect(pygame.display.get_surface(), RED, [(self.x, self.y), (Cell.side, Cell.side)])
        # if self.attackable["white"]:
        #     pygame.draw.rect(pygame.display.get_surface(), GREY, [(self.x, self.y), (Cell.side, Cell.side)])
        # if self.attackable["white"] and self.attackable["black"]:
        #     pygame.draw.rect(pygame.display.get_surface(), BLUE, [(self.x, self.y), (Cell.side, Cell.side)])

    def has_piece(self):
        return self.current_piece != None

    def is_touching_mouse(self):
        m_pos = pygame.mouse.get_pos()
        return (self.x <= m_pos[0] and m_pos[0] <= self.x + Cell.side) and (self.y <= m_pos[1] and m_pos[1] <= self.y + Cell.side)

    def is_attackable(self, by_who):
        return self.attackable[by_who]

    def has_enemy(self, pos):
        if self.get_board().get_cell(pos).get_current_piece() == None:
            return {}
        me = self.current_piece.get_group()
        other = self.board.get_cell(pos).get_current_piece().get_group()
        return other == give_my_enemy(me)


class Board(object):
    """A class that represents the board with 64 Cell 
    objects that represent each of the spots on the checkerboard"""
    def __init__(self, surface, cell1_color, cell2_color):
        self.cell1_color = cell1_color
        self.cell2_color = cell2_color
        self.surface = surface
        # even = light color /// odd = dark color
        self.checkerboard = [[Cell(self.cell1_color, (c, r), self) if (r + c)%2 == 0 else Cell(self.cell2_color, (c, r), self) for r in range(8)] for c in range(8)]

    # getters
    def get_cell(self, pos):
        try:
            return self.checkerboard[pos[0]][pos[1]]
        except:
            pass

    def get_checkerboard(self):
        return self.checkerboard

    def get_pos_of(self, unk_cell):
        return find(unk_cell, self.checkerboard)

    def draw(self):
        for r in self.checkerboard:
            for c in r:
                c.draw()


class PossiblePosition(object):
    # A circle object that would represent points 
    # (small circles) as the possible move given 
    # the piece as an argument and the color.
    image = pygame.transform.scale(pygame.image.load("position.png"), (round(Cell.side/5), round(Cell.side/5)))
    def __init__(self, position, parent, color=(0, 255, 0)):
        self.position = position
        self.parent = parent
        self.drawing = None
        self.chosen = None

    def get_position(self):
        return self.position

    def set_chosen(self, new_c):
        self.chosen = new_c

    def is_chosen(self):
        return self.chosen

    def show(self):
        pygame.display.get_surface().blit(PossiblePosition.image, pos_to_coor(self.position, True))
        if self.is_chosen() and self.position:
            self.parent.update_cell(self.position)


class Piece(object):
    def __init__(self, cell, name, peers=None, enemies=None, image=None):
        self.cell = cell
        n_g = name.split("_")
        self.name = n_g[1]
        self.group = n_g[0]
        self.move_count = 0
        if image == None:
            self.image = pygame.transform.scale(pygame.image.load("images/" + name + ".png"), (round(cell.side), round(cell.side)))
        else: 
            self.image = image
        self.cell.set_current_piece(self)
        self.possibilities = None
        self.position_objects = []
        self.peers = peers
        self.enemies = enemies
        self.check = None
        self.suspended = False
        if self.name == "king":
            self.check = False
            self.savers = []

    # setters
    def set_name(self, new_name):
        n_g = new_name.split("_")
        self.name = n_g[1]
        self.group = n_g[0]
        self.image = pygame.transform.scale(pygame.image.load("images/" + self.group + "_" + self.name + ".png"), (round(self.cell.side), round(self.cell.side)))

    def set_peers_and_enemies(self, new_peers, new_enemies):
        x = copy(new_peers)
        x.remove(self)
        self.peers = x
        self.enemies = new_enemies

    def set_possi(self, att=True):
        global king_in_check
        sign = 1 if self.group == "black" else -1
        pos1 = (self.get_position()[0]+1, self.get_position()[1]+sign)
        pos2 = (self.get_position()[0]-1, self.get_position()[1]+sign)
        
        # CLEARING ALL THE POSSIBILITIES
        if type(self.possibilities) == type([]):
            if self.name == "pawn":
                if not out_of_range(pos1):
                    self.get_cell().get_board().get_cell(pos1).set_attackable(not att, self)
                if not out_of_range(pos2):
                    self.get_cell().get_board().get_cell(pos2).set_attackable(not att, self)
            elif self.name != "king":
                for cell in self.possibilities:
                    self.cell.get_board().get_cell(cell).set_attackable(not att, self)
        po = get_possible_positions(self)
        self.possibilities = po[0]
        # if the piece is a king check for checkmate
        if self.name == "king":
            self.check = po[1]
            if self.check:
                king_in_check = self.group
        else:
            try:
                self.suspended = self.peers[0].check
            except:
                pass
        self.position_objects = [PossiblePosition(pos, self) for pos in self.possibilities]
        # if the piece is a pawn you will see the attackable for the
        # 2 diagonal moves only because the pawn can't capture a piece that is in front of it
        if self.name == "pawn":
            if not out_of_range(pos1, 8):
                self.cell.get_board().get_cell(pos1).set_attackable(att, self)
            if not out_of_range(pos2, 8):
                self.cell.get_board().get_cell(pos2).set_attackable(att, self)
        else:
            for cell in self.possibilities:
                self.cell.get_board().get_cell(cell).set_attackable(att, self)

    # getters
    def get_cell(self):
        return self.cell

    def get_image(self):
        return self.image

    def get_name(self):
        return self.name

    def get_group(self):
        return self.group

    def get_center(self):
        return (round(((self.cell.x * 2) + cell.side)/2), round(((self.cell.y * 2) + cell.side)/2))

    def get_move_count(self):
        return self.move_count

    def get_position(self):
        return self.cell.get_position()

    def get_peers(self):
        return self.peers

    def get_possibilities(self):
        return self.possibilities

    def get_position_objs(self):
        return self.position_objects

    def show(self):
        my_display.blit(self.image, (self.cell.x, self.cell.y))

    def is_touching_mouse(self):
        return self.cell.is_touching_mouse()

    def show_possible_moves(self):
        if self.group == current_side:
            if not self.suspended:             
                for possi in self.position_objects:
                    possi.show()
            else:
                savers = saving_moves(self.group)
                for possi in self.position_objects:
                    if possi.get_position() in savers:
                        possi.show()


    def update_cell(self, new_cell_pos):
        order = give_my_enemy(self.group)
        self.set_possi(False)
        future_cell = self.cell.get_board().get_cell(new_cell_pos)
        if future_cell.get_current_piece() != None:
            future_cell_piece = future_cell.get_current_piece()
            # if future_cell_piece.get_name() != "king":
            #     future_cell_piece.set_possi(False)
            future_cell_piece.set_possi(False)
            self.enemies.remove(future_cell_piece) 
        self.cell.set_current_piece(None)
        self.cell = future_cell
        self.cell.set_current_piece(self)
        self.show()
        self.move_count += 1
        switch_side()
        [piece.set_possi() for piece in white_pieces]
        [piece.set_possi() for piece in black_pieces]
        white_pieces[0].set_possi()
        black_pieces[0].set_possi()
        [piece.set_possi() for piece in white_pieces[1:]]
        [piece.set_possi() for piece in black_pieces[1:]]

def give_my_enemy(group):

    return {"black":"white", "white":"black"}[group]

def switch_side():
    global current_side
    current_side = give_my_enemy(current_side)

def find(value, l):
    """A function that returns the index of value in a 2D list l"""
    row =None
    column = None
    for row in range(len(l)):
        if value in l[row]:
            return (row, l[row].index(value))
    return -1

def has_negative(l):
    """A function that takes in a tuple and tests whether this tuple has negative element in it"""
    for x in l:
        if x < 0:
            return True
    return False

def has_overpositive(l, over):
    for x in l:
        if not x < over:
            return True
    return False

def out_of_range(l, over=8):

    return has_negative(l) or has_overpositive(l, over)    

def pos_to_coor(position, circle=False):
    """A funciton the takes in a position tuple and returns a the cooresponding 
    coordinate to this tuple based on the side length of the cell."""
    if circle:
        rad = Cell.side*.1
        coor = (position[0] * Cell.side, position[1] * Cell.side)
        coor = (round((((coor[0] * 2) + Cell.side)/2) - rad), round((((coor[1] * 2) + Cell.side)/2) - rad))
    else:
        coor = (position[0] * Cell.side, position[1] * Cell.side)
    return coor

def get_possible_positions(piece):
    """A function that takes a piece object and a board object as an input an returns a list of 
    all the possible positions on the board based on the name of that piece."""
    def_pos = piece.get_position()
    x = def_pos[0]
    y = def_pos[1]
    cell_brd = piece.get_cell().get_board()
    sign = -1 if piece.get_group() == "black" else 1
    possibilities = []
    check = False
    check_mate = None
    # for pawn
    if piece.get_name() == "pawn":
        sign = sign*-1
        # checks the adjacent diagonal pieces if they have an enemy on them and adds their positions accordingly
        pawn_moves = ((x+1, y+sign), (x-1, y+sign))
        for move in pawn_moves:
            if not out_of_range(move, 8):
                if piece.get_cell().has_enemy(move):
                    possibilities.append(move)
        # checks whether the cell in front of my piece has an enemy (would result in just one allowable move on 
        # the enemy piece rather than a double move) and adds it to the list of the possibilities
        if not out_of_range((x, y+sign), 8):
            enemy_status = piece.get_cell().has_enemy((x, y+sign))
            # if there was not an enemy in front of my piece it will just move on top of it
            if enemy_status  == {}:
                possibilities.append((x, y+sign))
                if (not piece.get_cell().has_enemy((x, y+(2*sign))) == True) and piece.get_move_count() == 0: 
                    possibilities.append((x, y+(2*sign)))
    # for knight
    elif piece.get_name() == "knight":
        # all the possible moves of a knight hardcoded
        knight_moves = (
                        (x+(sign * -2), y+(sign * -1)),
                        (x+(sign * -1), y+(sign * -2)),
                        (x+(sign), y+(sign * -2)),
                        (x+(sign * 2), y+(sign * -1)),
                        (x+(sign * 2), y+(sign)),
                        (x+(sign), y+(sign * 2)),
                        (x+(sign * -1), y+(sign * 2)),
                        (x+(sign * -2), y+(sign))
                        )
        for cell in knight_moves:
            if not out_of_range(cell, 8):
                if (piece.get_cell().get_board().get_cell(cell).get_current_piece() == None) or (piece.get_cell().has_enemy(cell)):
                    possibilities.append(cell)
    # for rook
    elif piece.get_name() == "rook":
        # a list comprehension that makes a list of all the cells in 
        # the same row as the rook and all the cells in the same column as the rook
        rook_moves = [(x, y) for x in range(8)] + [(x, y) for y in range(8)]
        rook_moves.remove(def_pos)
        rook_moves.remove(def_pos)
        rm_up = [cell for cell in rook_moves if cell[0] == x and cell[1] < y] # for the cells above the rook
        rm_up.reverse()
        rm_down = [cell for cell in rook_moves if cell[0] == x and cell[1] > y] # for the cells below the rook       
        rm_left = [cell for cell in rook_moves if cell[1] == y and cell[0] < x] # for the cells to the left of the rook
        rm_left.reverse()
        rm_right = [cell for cell in rook_moves if cell[1] == y and cell[0] > x] # for the cells to the right of the rook
        rook_moves = (rm_up, rm_down, rm_left, rm_right)
        for rm in rook_moves: # loop that goes through the 4 groups and takes all the cells up to and not including the one that is not empty
            counter = 0
            for cell in rm:
                if piece.get_cell().get_board().get_cell(cell).get_current_piece() != None: # is the cell occupied ???
                    if piece.get_cell().has_enemy(cell) == True:
                        possibilities.append(rm[counter])
                    break
                possibilities.append(cell)
                counter += 1
    # for bishop
    elif piece.get_name() == "bishop":
        # list comprehensions of topleft, topright, bottomleft, and bottomright in a dirverging order from the bishop position
        bm_topleft = [(x+(sign*dig), y+(sign*dig)) for dig in range(1, 9) if not out_of_range((x+(sign*dig), y+(sign*dig)), 8)]
        bm_bottomright = [(x-(sign*dig), y-(sign*dig)) for dig in range(1, 9) if not out_of_range((x-(sign*dig), y-(sign*dig)), 8)]
        bm_topright = [(x+(sign*dig), y+(sign*(~dig+1))) for dig in range(1, 9) if not out_of_range((x+(sign*dig), y+(sign*(~dig+1))), 8)]
        bm_bottomleft = [(x-(sign*dig), y-(sign*(~dig+1))) for dig in range(1, 9) if not out_of_range((x-(sign*dig), y-(sign*(~dig+1))), 8)]
        bishop_moves = (bm_topleft, bm_bottomright, bm_topright, bm_bottomleft)
        for bm in bishop_moves: # loop that goes through the 4 groups and takes all the cells up to and not including the one that is not empty
            counter = 0
            for cell in bm:
                if piece.get_cell().get_board().get_cell(cell).get_current_piece() != None: # is the cell occupied ???
                    if piece.get_cell().has_enemy(cell) == True:
                        possibilities.append(bm[counter])
                    break
                possibilities.append(cell)
                counter += 1
    # for queen
    elif piece.get_name() == "queen":
        horver_moves = [(x, y) for x in range(8)] + [(x, y) for y in range(8)] # a list comprehension that combines the hor (horizontal possible moves) and the ver (vertical possible moves)
        horver_moves.remove(def_pos)
        horver_moves.remove(def_pos)
        hv_up = [cell for cell in horver_moves if cell[0] == x and cell[1] < y] # for the cells above the rook
        hv_up.reverse()
        hv_down = [cell for cell in horver_moves if cell[0] == x and cell[1] > y] # for the cells below the rook       
        hv_left = [cell for cell in horver_moves if cell[1] == y and cell[0] < x] # for the cells to the left of the rook
        hv_left.reverse()
        hv_right = [cell for cell in horver_moves if cell[1] == y and cell[0] > x] # for the cells to the right of the rook
        horver_moves = (hv_up, hv_down, hv_left, hv_right)
        dd_topleft = [(x+(sign*dig), y+(sign*dig)) for dig in range(1, 9) if not out_of_range((x+(sign*dig), y+(sign*dig)), 8)]
        dd_bottomright = [(x-(sign*dig), y-(sign*dig)) for dig in range(1, 9) if not out_of_range((x-(sign*dig), y-(sign*dig)), 8)]
        dd_topright = [(x+(sign*dig), y+(sign*(~dig+1))) for dig in range(1, 9) if not out_of_range((x+(sign*dig), y+(sign*(~dig+1))), 8)]
        dd_bottomleft = [(x-(sign*dig), y-(sign*(~dig+1))) for dig in range(1, 9) if not out_of_range((x-(sign*dig), y-(sign*(~dig+1))), 8)]
        diagonal_moves = (dd_topleft, dd_bottomright, dd_topright, dd_bottomleft)
        queen_moves = (horver_moves + diagonal_moves)
        for qm in queen_moves: # loop that goes through the 4 groups and takes all the cells up to and not including the one that is not empty
            counter = 0
            for cell in qm:
                if piece.get_cell().get_board().get_cell(cell).get_current_piece() != None: # is the cell occupied ???
                    if piece.get_cell().has_enemy(cell) == True:
                        possibilities.append(qm[counter])
                    break
                possibilities.append(cell)
                counter += 1
    elif piece.get_name() == "king":
        me = piece.get_group()
        enemy = give_my_enemy(me)
        false_moves_by_attackable = 0
        for col in range(3):
            for row in range(3):
                pos = (x+(row-1), y+(col-1))
                if not (out_of_range(pos) or pos == def_pos) :
                    cell = piece.get_cell().get_board().get_cell(pos)
                    if not out_of_range(pos) and pos != def_pos:
                        if cell.get_current_piece() == None:    
                            if not cell.is_attackable(enemy):
                                possibilities.append(pos)
                            else:
                                false_moves_by_attackable += 1
                        else:
                            if cell.get_current_piece().get_group() != piece.get_group():
                                possibilities.append(pos)
        # if len(possibilities) == 0 and false_moves_by_attackable > 0:
        #     check = True
        if piece.get_cell().is_attackable(enemy):
            check = True
    return (possibilities, check)

def get_cell_touching_mouse():
    pos = pygame.mouse.get_pos()
    cell_position = (mt.ceil(pos[0]/Cell.side) - 1, mt.ceil(pos[1]/Cell.side)-1)
    return cell_position if not out_of_range(cell_position, 8) else (-1, -1)

def get_cell_clicked(cor=False):
    if not cor:
        output = clicked
    else:
        output = NotImplemented
    if pygame.mouse.get_pressed()[0]:
        touched_cell = get_cell_touching_mouse()
        output = my_board.get_cell(touched_cell).get_position()
    return output

def rev(x):
    return {0:1, 1:0}[x]

def direct_diff(point1, point2, moves_list):
    l = []
    diff = 0 if point1[0] == point2[0] else 1
    sign = 1 if point2[diff] < point1[diff] else -1
    l = [(point2[rev(diff)] + (sign * y), point1[diff]) if diff else (point1[diff], point2[rev(diff)] + (sign * y)) for y in range(abs(point1[rev(diff)] - point2[rev(diff)]))]
    for pos in l:
        moves_list.append((abs(pos[0]), abs(pos[1]))) 

def diagonal_diff(point1, point2, moves_list):
    x_sign = 1 if point2[0] < point1[0] else -1
    y_sign = 1 if point2[1] < point1[1] else -1
    diff = abs(point1[0] - point2[0])
    for xy in range(diff):
        moves_list.append((point2[0] + (x_sign * xy), point2[1] + (y_sign * xy)))
 
def saving_moves(king_side):
    moves = []
    enemy = give_my_enemy(king_side)
    if king_side == "white":
        king = white_pieces[0]
    else:
        king = black_pieces[0]
    king_cell = king.get_cell()
    attackers = list(king_cell.get_parent_attacker(king_side))
    if len(attackers) > 1:
        return []
    elif len(attackers) == 1:
        king_pos = king.get_position()
        enemy_pos = attackers[0]
        enemy_type = my_board.get_cell(enemy_pos).get_current_piece().get_name()
        if enemy_type == "knight":
            return enemy_pos
        elif enemy_type == "pawn":
            return enemy_pos
        elif enemy_type == "rook":
            direct_diff(king_pos, enemy_pos, moves)
        elif enemy_type == "bishop":
            diagonal_diff(king_pos, enemy_pos, moves)
        elif enemy_type == "queen":
            if king_pos[0] == enemy_pos[0] or king_pos[1] == enemy_pos[1]:
                direct_diff(king_pos, enemy_pos, moves)
            else:
                diagonal_diff(king_pos, enemy_pos, moves)
    return moves


pygame.display.init()
pygame.font.init()

# colors
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
VIOLET = (255, 0, 255)
BROWN = (218,165,32)
DARK_GREEN = (3, 125, 80)


# icon
game_icon = pygame.image.load("chess_icon.png")

# initializing variables
# display_side = 600
game_loop = True
block_dims = (50, 15)
block_coor = (5, 5)
background = WHITE
clicked = None
clicked_piece = None
need_poss = False
current_side = "white"
pre_move_clicked = None
king_in_check = None

# display settings
my_display = pygame.display.set_mode((display_side, display_side))
pygame.display.set_caption("Chess Game")
pygame.display.set_icon(game_icon)


# FPS
clock = pygame.time.Clock()

# the instance of the board object
my_board = Board(my_display, WHITE, BROWN)
# the standard layout of the pieces that will be used to arrange the pieces
layout = [["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"], "pawn"]
# list comprehensions that construct 2 lists for both sets in the correct order
white_pieces = [Piece(my_board.get_cell((x, ~y)), "white_" + (layout[y] if y == 1 else layout[y][x])) for x in range(8) for y in range(2)]
black_pieces = [Piece(my_board.get_cell((x, y)), "black_" + (layout[y] if y == 1 else layout[y][x])) for x in range(8) for y in range(2)]
# moving the king to the end of the list for both pieces
white_pieces.insert(0, white_pieces.pop(8))
black_pieces.insert(0, black_pieces.pop(8))
# # setting the pissibilites for both pieces
[piece.set_possi() for piece in white_pieces]
[piece.set_possi() for piece in black_pieces]
# # setting the enemies and peers for both pieces
[piece.set_peers_and_enemies(white_pieces, black_pieces) for piece in white_pieces]
[piece.set_peers_and_enemies(black_pieces, white_pieces) for piece in black_pieces]

labels = [Label("abcdefgh"[x]) if x < 8 else Label(x-8) for x in range(16)]

def drawDisplay():
    global clicked_piece, need_poss, clicked
    # drawing the board
    my_board.draw()
    # showing the pieces
    [piece.show() for piece in white_pieces]
    [piece.show() for piece in black_pieces]
    [label.show() for label in labels]
    if need_poss:
        try:
            clicked_piece.show_possible_moves()
        except:
            pass

# # # Game loop
while game_loop:
    # EVENTS
    for event in pygame.event.get():
        # QUITTING
        if event.type == pygame.QUIT:
            game_loop = False
    inst_click = get_cell_clicked()
    if inst_click != None:
        occupied_positions = {"white":[piece.get_position() for piece in white_pieces], "black":[piece.get_position() for piece in black_pieces]}
        if inst_click in occupied_positions[current_side]:
            pre_move_clicked = inst_click
            clicked_piece = my_board.get_cell(pre_move_clicked).get_current_piece()
            occupied_positions[current_side].remove(pre_move_clicked)
            if pre_move_clicked in occupied_positions[current_side]:
                need_poss = True
            else:
                need_poss = False
        else:
            clicked = inst_click
            try:
                if clicked in clicked_piece.get_possibilities():
                    need_poss = True
                    clicked_index = clicked_piece.get_possibilities().index(clicked)
                    clicked_piece.get_position_objs()[clicked_index].set_chosen(True)
                    clicked = None
            except:
                pass
        need_poss = True
    
    drawDisplay() 
    pygame.display.update()
    clock.tick(10)
    


pygame.quit()
quit()


import numpy as np
from random import randint

WIDTH = 6
HEIGHT = 6
FOOD = WIDTH*HEIGHT


def pos_to_board(x, y):
    return y*WIDTH + x


def board_to_pos(board):
    y = int(board / WIDTH)
    x = board % WIDTH
    return x, y


def _random_free_space(board):
    if 0 not in board:
        return -1
    while True:
        space = randint(0, WIDTH*HEIGHT-1)
        if board[space] == 0:
            return space

class Game:
    def __init__(self):
        self.currentPlayer = 1
        action_space = np.array([0]*WIDTH*HEIGHT, dtype=np.int)
        action_space[_random_free_space(action_space)] = 1
        action_space[_random_free_space(action_space)] = -1
        action_space[_random_free_space(action_space)] = FOOD
        self.gameState = GameState(action_space, self.currentPlayer)
        self.grid_shape = (WIDTH,HEIGHT)
        self.input_shape = (3,WIDTH,HEIGHT)
        self.name = 'battlesnake'
        self.state_size = len(self.gameState.binary)
        self.action_size = len(action_space)

    def reset(self):
        self.currentPlayer = 1
        action_space = np.array([0]*WIDTH*HEIGHT, dtype=np.int)
        action_space[_random_free_space(action_space)] = 1
        action_space[_random_free_space(action_space)] = -1
        action_space[_random_free_space(action_space)] = FOOD
        self.gameState = GameState(action_space, self.currentPlayer)
        return self.gameState

    def step(self, action, turn):
        next_state, value, done = self.gameState.takeAction(action, turn)
        self.currentPlayer = -self.currentPlayer
        self.gameState = next_state
        info = None
        return next_state, value, done, info

    def identities(self, state, actionValues):
        identities = [(state, actionValues)]
        board_matrix = np.reshape(state, (WIDTH, HEIGHT))
        av_matrix = np.reshape(state, (WIDTH, HEIGHT))

        for k in range(1,4):
            if WIDTH != HEIGHT and k % 2 != 0:
                continue
            current_board = np.squeeze(np.asarray(np.rot90(board_matrix, k)))
            current_av = np.squeeze(np.asarray(np.rot90(av_matrix, k)))
            identities.append((GameState(current_board, state.playerTurn), current_av))

        return identities


class GameState:
    def __init__(self, board, playerTurn, action=None):
        self.board = board
        self.pieces = {'1': 'X', '0': '-', '-1': 'O'}
        self.playerTurn = playerTurn
        self.binary = self._binary()
        self.id = self._convertStateToId()
        self.allowedActions = self._allowedActions()
        self.score = self._getScore()
        self.first_player_action = action

    def _allowedActions(self):
        head = np.where(self.board==self.playerTurn)[0][0]
        x,y = board_to_pos(head)
        allowed = []
        if x+1 < WIDTH:
            allowed.append(pos_to_board(x+1, y))
        if x-1 >= 0:
            allowed.append(pos_to_board(x-1, y))
        if y+1 < HEIGHT:
            allowed.append(pos_to_board(x, y+1))
        if y-1 >= 0:
            allowed.append(pos_to_board(x, y-1))

        return allowed

    def _binary(self, current_player=None):
        if not current_player:
            current_player = self.playerTurn

        player1 = np.array(self.board, copy=True)
        player1[(self.board<0) | (self.board!=FOOD)] = 0

        player2 = np.array(self.board, copy=True)
        player2[self.board>0] = 0

        if current_player == 1:
            position = np.append(player1, player2)
        else:
            position = np.append(player2, player1)

        food = np.array(self.board, copy=True)
        food[self.board==FOOD] = 1

        position = np.append(position, food)

        return position


    def _convertStateToId(self):
        position = self._binary(1)

        id = ''.join(map(str, position))

        return id

    def _getScore(self):
        score_board = np.array(self.board, copy=True)
        score_board[score_board==FOOD] = 0
        score_board[score_board<0] = -1
        score_board[score_board>0] = 1
        unique_counts = dict(zip(*np.unique(score_board, return_counts=True)))
        return unique_counts.get(self.playerTurn, 0), unique_counts.get(-self.playerTurn, 0)

    def takeAction(self, action, turn):
        done = 0
        value = 0
        if turn >= 500:
            if self.score[0] > self.score[1]:
                value = self.playerTurn
            elif self.score[0] < self.score[1]:
                value = -self.playerTurn
            return GameState(self.board, -self.playerTurn), value, 1
        if not self.first_player_action:
            newState = GameState(self.board, -self.playerTurn, action)
        else:
            newBoard = np.array(self.board)

            if self.first_player_action == action:
                done = 1
                if self.score[0] > self.score[1]:
                    value = self.playerTurn
                elif self.score[0] < self.score[1]:
                    value = -self.playerTurn
            else:
                if newBoard[self.first_player_action] == WIDTH*HEIGHT:
                    self.move_snake(newBoard, -self.playerTurn, self.first_player_action, True)
                elif newBoard[self.first_player_action] != 0:
                    done = 1
                    value = self.playerTurn
                else:
                    self.move_snake(newBoard, -self.playerTurn, self.first_player_action)

                if newBoard[action] == WIDTH*HEIGHT:
                    self.move_snake(newBoard, self.playerTurn, action, True)
                elif newBoard[action] != 0:
                    done = 1
                    if value != 0:
                        value = 0
                    else:
                        value = -self.playerTurn
                else:
                    self.move_snake(newBoard, self.playerTurn, action)

            if not done and FOOD not in newBoard:
                food_space = _random_free_space(newBoard)
                if food_space == -1:
                    done = 1
                    if self.score[0] > self.score[1]:
                        value = self.playerTurn
                    elif self.score[0] < self.score[1]:
                        value = -self.playerTurn
                else:
                    newBoard[food_space] = FOOD

            newState = GameState(newBoard, -self.playerTurn)

        return newState, value, done

    def move_snake(self, board, player, action, add_to_tail=False):
        if player == -1:
            tail = np.amin(board)
            body = tail
            if not add_to_tail:
                board[board == tail] = 0
                body += 1
            while body < 0:
                board[board == body] = body - 1
                body += 1
        else:
            tempBoard = np.array(board, copy=True)
            tempBoard[board==FOOD] = 0
            tail = np.amax(tempBoard)
            body = tail
            if not add_to_tail:
                board[board == tail] = 0
                body -= 1
            while body > 0:
                board[board == body] = body + 1
                body -= 1

        board[action] = player

    def render(self, logger):
        logger.info('')
        for r in range(HEIGHT):
            row = []
            for x in self.board[WIDTH * r: (WIDTH * (r+1))]:
                if x == FOOD:
                    row.append("F")
                elif x == -1:
                    row.append("O")
                elif x == 1:
                    row.append("X")
                elif x < -1:
                    row.append("o")
                elif x > 1:
                    row.append("x")
                else:
                    row.append("-")
            logger.info(row)
        logger.info('--------------')
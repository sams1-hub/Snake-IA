
from gameModule import (
    RIGHT,
    LEFT,
    DOWN,
    UP,
    SNAKE_CHAR,
    FOOD_CHAR,
    WALL_CHAR,
)
import math
import heapq
import time


class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent

        self.g = 0
        self.h = 0
        self.f = self.g + self.h

    def __repr__(self):
        return f"({self.position[0]}, {self.position[1]})"

    def __lt__(self, other):
        return self.f < other.f

    def __key(self):
        return self.position

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.__key() == other.__key()
        return NotImplemented


class IA_Astar:
    def __init__(self, args, game):
        self.moves = [RIGHT, DOWN, LEFT, UP]
        self.best_path = []  # The path used by the snake
        self.first = True  # Boolean
        self.args = args
        self.game = game

    def reset_state(self):
        self.best_path = []  # The path used by the snake
        self.first = True  # Boolean

    def eat(self):
        """
        This function is useless here, it is a placeholder for a function needed in the other
        algorithm.
        """
        pass

    def choose_next_move(self, state):
        """
            This function is called by the game instance in order to find the next move chosen by the used algorithm.
            In our case, there are 5 different algorithms : Random, SShaped, A*, A* weighted and A* reversed. All of
            them are described in detail in the report

        :param state: The state containing the grid, the snake body, the score and a boolean indicating if the snake
                      is alive
        :return: The move chosen by the algorithm
        """

        grid, score, alive, snake = state
        head = snake[0]

        if self.args.astar and self.best_path == []:
            self.best_path = self.astar(state, self.game.food, interactive=True)
        elif self.args.sshaped and self.best_path == []:
            self.best_path = self.sshape(state)

        # the snake goes DOWN when A* does not work
        if self.best_path == "No path":
            print("A* did not find path")
            # try to go away from tail
            d = (head[0] - snake[1][0], head[1] - snake[1][1])
            return d

        next_move = self.get_next_move(self.best_path, head)

        return next_move

    def get_next_move(self, path, head):
        """
            This function finds the next move to do based on the head and the path.
        :param path: The path followed by the snake
        :param head: The head of the snake
        :return: The next move
        """
        next_node = path.pop()
        next_pos = next_node.position
        next_mov_bool = []

        for i in range(len(next_pos)):
            next_mov_bool.append(next_pos[i] - head[i])

        return next_mov_bool[:2]

    def h_cost(self, current, end):
        """
            Cost used in the A* algorithm
        :param current: current node
        :param end: end node
        :return: the euclidian distance between the current node and the end node
        """
        # res = abs(current.position[0] - end.position[0]) + abs( # Manhanttan
        #    current.position[1] - end.position[1]
        # )
        res = math.sqrt(
            (current.position[0] - end.position[0]) ** 2
            + (current.position[1] - end.position[1]) ** 2
        )
        return res

    def is_in_grid(self, pos, grid):
        return 0 <= pos[0] < len(grid) and 0 <= pos[1] < len(grid[0])

    def astarr(self, state, goal_pos, interactive=False):
        """
        This function is an implementation of the A* algorithm
        :param state: The current state of the game
        :param goal_pos: The position where the snake has to go
        :param interactive: Display the execution of the A* algorithm
        :return: The path to the goal
        """
        grid, score, alive, snake = state
        head = snake[0]
        closed_list = set()
        open_list = []
        head_node = Node(head)
        food_node = Node(goal_pos)

        heapq.heappush(open_list, head_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            closed_list.add(current_node)

            if current_node == food_node:
                path = []
                while current_node.parent is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                if interactive:
                    for el in path:
                        self.game.grid[el.position[0]][el.position[1]] = "A"
                        self.game.draw()
                    time.sleep(0.1)
                    for el in path + open_list + list(closed_list):
                        self.game.grid[el.position[0]][el.position[1]] = " "
                    self.game.grid[food_node.position[0]][
                        food_node.position[1]
                    ] = FOOD_CHAR
                    self.game.grid[head_node.position[0]][
                        head_node.position[1]
                    ] = SNAKE_CHAR
                    self.game.draw()
                return path

            for new_position in self.moves:
                node_position = (
                    current_node.position[0] + new_position[0],
                    current_node.position[1] + new_position[1],
                )
                # Make sure within range
                if not self.is_in_grid(node_position, grid):
                    continue
                # Make sure walkable terrain
                if (
                    grid[node_position[0]][node_position[1]] == SNAKE_CHAR
                    or grid[node_position[0]][node_position[1]] == WALL_CHAR
                ):
                    continue
                # Create new node
                child = Node(node_position, current_node)

                # Child is on the closed list
                if child in closed_list:
                    continue

                # Child is in the openlist with smaller cost
                if (
                    child in open_list
                    and open_list[open_list.index(child)].g
                    <= current_node.g + 1
                ):
                    continue
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = self.h_cost(child, food_node)
                child.f = child.g + child.h
                child.parent = current_node

                # Add the child to the open list
                heapq.heappush(open_list, child)

                # Animation of Astar
                if (
                    interactive
                    and not self.game.grid[child.position[0]][child.position[1]]
                    == "+"
                ):
                    self.game.grid[current_node.position[0]][
                        current_node.position[1]
                    ] = "C"
                    self.game.grid[child.position[0]][child.position[1]] = "S"
                    time.sleep(0.001)
                    self.game.draw()

        return "No path"

    def sshape(self, state):
        """
            SShaped implementation. The snake does the same path during all the game and it gives the perfect score.
        :param state: The current state of the game
        :return: The path the snake has to follow
        """
        grid, score, alive, snake = state
        head = snake[0]
        path = []
        # Snake starts at random pos, so go to top right
        if self.first:
            self.first = False
            start_x = min(head[0] + 1, len(grid) - 1)
            path.append(Node((start_x, head[1])))
            path.extend(
                (Node((start_x, j)) for j in range(head[1] + 1, len(grid[0])))
            )
            path.extend(
                (
                    Node((i, len(grid[0]) - 1))
                    for i in range(start_x - 1, -1, -1)
                )
            )
        # Then travel down in S shape, right to left and down
        for i in range(len(grid)):
            path.extend(
                (
                    Node((i, j)) if i % 2 else Node((i, len(grid[0]) - 2 - j))
                    for j in range(len(grid[0]) - 1)
                )
            )
        # Then go up on the last column right
        path.extend(
            (Node((i, len(grid[0]) - 1)) for i in range(len(grid) - 1, -1, -1))
        )
        return path[::-1]

    def astar(self, state, goal_pos, interactive=False):
        """
        This function is an implementation of the A* algorithm
        :param state: The current state of the game
        :param goal_pos: The position where the snake has to go
        :param interactive: Display the execution of the A* algorithm
        :return: The path to the goal
        """
        grid, score, alive, snake = state
        head = snake[0]
        closed_list = set()
        open_list = []
        head_node = Node(head)
        food_node = Node(goal_pos)
        self.hamiltionian_generate(grid)
        hamiltonian_path = [[3, 2, 1, 16],
                            [4, 5, 6, 15],
                            [9, 8, 7, 14],
                            [10, 11, 12, 13]]
        n = 20
        hamiltonian_path = [[0 for i in range(n)] for j in range(n)]
        # Fill the matrix with zigzag pattern
        for i in range(n):
            for j in range(1, n):
                if i % 2 == 0:
                    hamiltonian_path[i][j] = (n - 1) * i + j
                else:
                    hamiltonian_path[i][j] = (n - 1) * i - j + n
        for i in range(n):
            hamiltonian_path[i][0] = n * n - i

        heapq.heappush(open_list, head_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            closed_list.add(current_node)

            if current_node == food_node:
                path = []
                while current_node.parent is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                return path

            for new_position in self.moves:
                node_position = (
                    current_node.position[0] + new_position[0],
                    current_node.position[1] + new_position[1],
                )
                # Make sure within range
                if not self.is_in_grid(node_position, grid):
                    continue
                # Make sure walkable terrain
                if (
                    grid[node_position[0]][node_position[1]] == WALL_CHAR
                ):
                    continue

                #Make sure shortcut is legal
                if len(snake) > current_node.g:
                    tail_node = Node(snake[-1-current_node.g])
                else:
                    tail_node = current_node
                    for i in range(len(snake)-1):
                        tail_node = tail_node.parent
                h_pos_tail = hamiltonian_path[tail_node.position[0]][tail_node.position[1]]
                h_pos_head = hamiltonian_path[current_node.position[0]][current_node.position[1]]
                h_pos_new_head = hamiltonian_path[node_position[0]][node_position[1]]

                if h_pos_tail < h_pos_head and h_pos_tail < h_pos_new_head and h_pos_new_head < h_pos_head:
                    continue
                if h_pos_head < h_pos_tail:
                    if h_pos_tail < h_pos_new_head and h_pos_head < h_pos_new_head:
                        continue
                    if h_pos_tail > h_pos_new_head and h_pos_head > h_pos_new_head:
                        continue
                if h_pos_tail == h_pos_new_head:
                    continue

                # Create new node
                child = Node(node_position, current_node)

                # Child is on the closed list
                if child in closed_list:
                    continue

                # Child is in the openlist with smaller cost
                if (
                    child in open_list
                    and open_list[open_list.index(child)].g
                    <= current_node.g + 1
                ):
                    continue
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = self.h_cost(child, food_node)
                child.f = child.g + child.h
                child.parent = current_node

                # Add the child to the open list
                heapq.heappush(open_list, child)

        return "No path"

    def hamiltionian_generate(self, grid):
        graph = []
        size = len(grid)
        for y in range(size):
            for x in range(size):
                connections = []
                for i in range(size**2):
                    connections.append(0)
                if self.is_in_grid((x - 1,y), grid) and grid[x - 1][y] != WALL_CHAR:
                    connections[x - 1 + y * size] = 1
                if self.is_in_grid((x + 1, y), grid) and grid[x + 1][y] != WALL_CHAR:
                    connections[x + 1 + y * size] = 1
                if self.is_in_grid((x, y - 1), grid) and grid[x][y - 1] != WALL_CHAR:
                    connections[x + (y - 1) * size] = 1
                if self.is_in_grid((x, y + 1), grid) and grid[x][y + 1] != WALL_CHAR:
                    connections[x + (y + 1) * size] = 1
                graph.append(connections)

        print(graph)

        NODE = size**2
        path = [None] * NODE

        def displayCycle():
            print("Cycle:", end=" ")

            for i in range(NODE):
                print(path[i], end=" ")
            print(path[0])  # print the first vertex again

        def isValid(v, k):
            if graph[path[k - 1]][v] == 0:  # if there is no edge
                return False

            for i in range(k):  # if vertex is already taken, skip that
                if path[i] == v:
                    return False
            return True

        def cycleFound(k):
            if k == NODE:  # when all vertices are in the path
                if graph[path[k - 1]][path[0]] == 1:
                    return True
                else:
                    return False

            for v in range(1, NODE):  # for all vertices except starting point
                if isValid(v, k):  # if possible to add v in the path
                    path[k] = v
                    if cycleFound(k + 1) == True:
                        return True
                    path[k] = -1  # when k vertex will not be in the solution
            return False

        def hamiltonianCycle():
            for i in range(NODE):
                path[i] = -1
            path[0] = 0  # first vertex as 0

            if cycleFound(1) == False:
                print("Solution does not exist")
                return False

            displayCycle()
            return True

        hamiltonianCycle()



        #Partie Sami : 
    def hamiltonianCycle():
     for i in range(NODE):
                path[i] = -1
            path[0] = 0  # first vertex as 0

            if cycleFound(1) == False:
                print("Solution does not exist")
                return False

            displayCycle()
            return True

def getMoveDirection(src, dest):
    if src // size == dest // size and src + 1 == dest:
        return "RIGHT"
    elif src // size == dest // size and src - 1 == dest:
        return "LEFT"
    elif src % size == dest % size and src + size == dest:
        return "DOWN"
    elif src % size == dest % size and src - size == dest:
        return "UP"
    else:
        return "invalid"

def displayCycle():
    print("Hamiltonian Cycle Moves:")
    moves = []
    for i in range(NODE):
        moves.append(getMoveDirection(path[i], path[(i + 1) % NODE]))
    displayMoves(moves)

def displayMoves(moves):
    print(moves)

# Call the hamiltonianCycle function
hamiltonianCycle()



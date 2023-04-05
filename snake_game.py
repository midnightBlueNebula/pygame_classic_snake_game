#exec(open("Scripts/snake_game.py").read())

import pygame
import sys
import random

from pygame.locals import (

    K_UP,

    K_DOWN,

    K_LEFT,

    K_RIGHT,

    K_ESCAPE,

    KEYDOWN,

    QUIT,

)


#Size of the screen and game objects.
SCREENX = 640
SCREENY = 360
NODESIZE = 20
FOODSIZE = 5


class Position:
    def __init__(self, rect, x, y):
        self.rect = rect
        self.rect.left = x
        self.rect.top = y
        
    def __str__(self):
        return "X: " + str(self.x()) + ", Y: " + str(self.y())
    def __eq__(self, other):
        return (self.x(), self.y()) == (other.x(), other.y())

    def x(self):
        return self.rect.left

    def y(self):
        return self.rect.top

    def new_position(self, target): # [x, y]
        assert isinstance(target, list), "Argument must be a list"
        assert len(target) == 2, "The list must have 2 elements, x and y"
        assert isinstance(target[0], int) and isinstance(target[1], int), "Elements of the list must be integers."
        self.rect.left = target[0]
        self.rect.top = target[1]


class Food(pygame.sprite.Sprite):
    def __init__(self):
        super(Food, self).__init__()
        self.size = FOODSIZE
        self.surf = pygame.Surface((self.size, self.size))
        self.pick_color()
        self.rect = self.surf.get_rect()
        self.position = None
        self.place_food()

    def place_food(self):
        self.pick_color()
        x_max_limit = SCREENX - NODESIZE
        y_max_limit = SCREENY - NODESIZE
        x = random.randint(0, x_max_limit)
        y = random.randint(0, y_max_limit)
        del self.position
        self.position = Position(self.rect, x, y)

    def pick_color(self):
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        self.surf.fill((r, g, b))

"""
The snake will be a linked list.
When the snake moves, each node other than head node will be placed in the
previous position of the previous node.
When the snake eats the food, a new node will be added to tail of the snake.
"""

class SnakeNode(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(SnakeNode, self).__init__()
        self.size = NODESIZE
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.position = Position(self.rect, x, y)
        self.next = None
        self.freeze = False
        
    def __str__(self):
        return "X: " + str(self.position.x()) + " Y: " + str(self.position.y())


class Snake:
    def __init__(self):
        self.head = SnakeNode(SCREENX/2 - NODESIZE/2, SCREENY/2 - NODESIZE/2)
        self.tail = self.head
        self.is_alive = True
        self.direction = "L" # L -> left R -> right U -> up D -> down
        self.snake_size = 1

    def found_food(self):
        """
        The new node will be placed in the same position of the tail node.
        Then each node other than the new node will be moved in their next positions.
        Therefore, the new node could be added in correct position and direction.
        """
        self.tail.next = SnakeNode(self.tail.position.x(), self.tail.position.y())
        self.tail = self.tail.next
        #Freezes the new node to move every node other than the new node.
        self.tail.freeze = True
        self.move()
        #New node is in correct place now.
        #Unfreezes the new node to make it movable in next updates.
        self.tail.freeze = False
        self.snake_size = self.snake_size + 1
        #REturn the new node to add it into container,
        #To draw it into screen and check collisions in each update.
        return self.tail

    def eats_itself(self):
        self.is_alive = False

    def move(self):
        #Calculates next position of the head node,
        #According to its position and direction of the snake.
        start = self.head.position
        target = {"L": [start.x() - self.head.size, start.y()],
                  "R": [start.x() + self.head.size, start.y()],
                  "U": [start.x(), start.y() - self.head.size],
                  "D": [start.x(), start.y() + self.head.size]}[self.direction]

        if target[0] > SCREENX - NODESIZE:
            target[0] = 0
        elif target[0] < 0:
            target[0] = SCREENX - NODESIZE
            
        if target[1] < 0:
            target[1] = SCREENY - NODESIZE
        elif target[1] > SCREENY - NODESIZE:
            target[1] = 0

        #Moves head node to the next position.
        #Then, moves other nodes into previous posiition of the previous nodes.
        current = self.head
        while current != None and not current.freeze:
            current_position = [current.position.x(), current.position.y()]
            current.position.new_position(target) 
            target = current_position
            current = current.next

    def change_direction(self, direction):
        assert isinstance(direction, str), "Direction is not a string."
        direction = direction.upper()
        assert direction == "L" or direction == "R" or direction == "U" or direction == "D", "Direction must be 'L', 'R', 'U' or 'D'"
        self.direction = direction

    def length(self):
        return self.snake_size

    def kill(self):
        self.is_alive = False

    #Snake will move in each frame update.
    #Frame rate of the game shall be 2.
    #In order to move the snake only 2 times per second.
    def update(self):
        self.move()


def snakefactory():
    return Snake()


#Initializing game objects.
food = Food()
snake = Snake()

#Storing the snake's nodes in a different container to check,
#whether the snake's head collides with its body or not.
snake_node_sprites = pygame.sprite.Group()
#Storing sprites in a container to draw them into screen in each update.
all_sprites = pygame.sprite.Group()
all_sprites.add(snake.head)

#Starting lenght of the snake will be 3.
node_2 = snake.found_food()
node_3 = snake.found_food()
snake_node_sprites.add(node_2)
snake_node_sprites.add(node_3)
all_sprites.add(node_2)
all_sprites.add(node_3)

#Initializing clock object to set frame rate of the game.
clock = pygame.time.Clock()

class GameManager:
    def __init__(self):
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENX, SCREENY))
        self.run()
        self.close()

    def run(self):
        #Game will run unless player quits or game overs.
        while self.running:
            #Iterates through the player's inputs.
            #Player either changes direction of the snake,
            #or, quits the game
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif event.key == K_LEFT:
                        snake.change_direction("L")
                    elif event.key == K_RIGHT:
                        snake.change_direction("R")
                    elif event.key == K_UP:
                        snake.change_direction("U")
                    elif event.key == K_DOWN:
                        snake.change_direction("D")
                        
                elif event.type == QUIT:
                    self.running = False

            #Paints the screen's background with black.
            self.screen.fill((0, 0, 0))
            #Moves the snake, according to its direction.
            snake.update()

            #If the snake's head collides with food, the snake grows by one node.
            #Places the food in a new random place.
            #If the random place is occupied by one of the snake nodes,
            #draw food later than other entities to draw on top,
            #to make it visible.
            if pygame.sprite.collide_rect(food, snake.head):
                new_node = snake.found_food()
                snake_node_sprites.add(new_node)
                all_sprites.add(new_node)
                food.place_food()

            #If the snake's head hit itself, game over.
            if pygame.sprite.spritecollideany(snake.head, snake_node_sprites):
                snake.kill()
                break

            #Draws entities in their current place.
            for entity in all_sprites:
                self.screen.blit(entity.surf, entity.rect) 

            self.screen.blit(food.surf, food.rect) #Draw foods on top.

            pygame.display.flip() #Updates view.
            #Frame rate will be 2.
            clock.tick(2) #The snake shall move two times per second.

    def close(self):
        #Closes the program.
        pygame.quit()  
        sys.exit()  


class SnakeException(BaseException):
        #Custom exception class for testing.
	def __init__(self, msg):
		super(SnakeException, self).__init__(msg)


#Test cases.
class SnakeTest:
    def __init__(self):
        self.assert_snake_grows_by_one()
        self.assert_snake_dies()
        self.assert_snake_moves_correctly()
        
    def assert_snake_grows_by_one(self):
        snake = snakefactory()
        snake_length_start = snake.length()
        snake.found_food()
        snake_length_end = snake.length()
        difference = snake_length_end - snake_length_start
        if difference == 1 and snake.tail != snake.head:
            print("assert_snake_grows_by_one -> passes")
        else:
            raise SnakeException("assert_snake_grows_by_one -> fails")

    def assert_snake_dies(self):
        snake = snakefactory()
        snake.kill()
        if snake.is_alive == True:
            raise SnakeException("assert_snake_dies -> fails")
        else:
            print("assert_snake_dies -> passes")

    def assert_snake_moves_correctly(self):
        snake = snakefactory()
        snake.found_food()
        snake.move()
        snake.found_food()
        snake.move()
        snake.found_food()
        snake.move()
        snake.found_food()
        snake.move()
        snake_head_pos_start = snake.head.position
        target = None
        index = random.randint(0, 3)
        directions = ["L", "R", "U", "D"]
        snake.direction = directions[index]
        snake.move()
        
        if snake_head_pos_start.x() == 0 and snake.direction == "L":
            target = Position(snake.head.rect, SCREENX - NODESIZE, snake_head_pos_start.y())
        elif snake_head_pos_start.x() == SCREENX - NODESIZE and snake.direction == "R":
            target = Position(snake.head.rect, 0 + NODESIZE, snake_head_pos_start.y())
        elif snake_head_pos_start.y() == SCREENY - NODESIZE and snake.direction == "D":
            target = Position(snake.head.rect, snake_head_pos_start.x(), 0 + NODESIZE)
        elif snake_head_pos_start.y() == 0 + NODESIZE and snake.direction == "U":
            target = Position(snake.head.rect, snake_head_pos_start.x(), SCREENY - NODESIZE)
        else:
            target = Position(snake.head.rect, snake_head_pos_start.x() - NODESIZE, snake_head_pos_start.y())  

        if snake.head.position == target:
            print("assert_snake_moves_correctly 1 -> passes")
            flag_2 = True
    
            current_node = snake.head
            target_positions = []
            while current_node != None:
                if current_node == snake.tail:
                    break
                target_positions.append([current_node.position.x(), current_node.position.y()])
                current_node = current_node.next
            
            snake.move()
            
            current_node = snake.head.next
            target_index = 0
            while current_node != None:
                position_list = [current_node.position.x(), current_node.position.y()] 
                if position_list != target_positions[target_index]:
                    print(position_list)
                    print([current_node.position.x(), current_node.position.y()])
                    flag_2 = False
                    break
                current_node = current_node.next
                target_index = target_index + 1
            if flag_2:
                print("assert_snake_moves_correctly 2 -> passes")
            else:
                raise SnakeException("assert_snake_moves_correctly 2 -> fails")
        else:
            raise SnakeException("assert_snake_moves_correctly 1 -> fails")
        


SnakeTest()
GameManager()

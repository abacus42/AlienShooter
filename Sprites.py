import pygame
import pygame.freetype
from enum import Enum


class AlienArea(pygame.sprite.Sprite):
    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, width, height)


class Alien(pygame.sprite.Sprite):
    def __init__(self, image, location, lives):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = location
        self.lives = lives

    def getLocation(self):
        return(self.rect.left, self.rect.top)

    def update(self):
        self.rect = self.rect.move(0, 1)

    def hit(self):
        self.lives -= 1
        if self.lives == 0:
            self.kill()
            return True
        return False


class DropTypes(Enum):
    BOMB = 0
    LIFE = 1
    FREEZE = 2
    SLOW = 3


class Drop(pygame.sprite.Sprite):
    def __init__(self, image, location, dropType):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = location
        self.dropType = dropType

    def getLocation(self):
        return(self.rect.left, self.rect.top)

    def update(self):
        self.rect = self.rect.move(0, 15)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, location, explosionImages):
        pygame.sprite.Sprite.__init__(self)
        self.rect = explosionImages[1].get_rect()
        self.explosionImages = explosionImages
        self.image = explosionImages[0]
        self.rect.left, self.rect.top = location
        self.counter = 1

    def update(self):
        if self.counter == len(self.explosionImages):
            self.kill()
        else:
            self.image = self.explosionImages[self.counter]
            self.counter += 1


class Missile(pygame.sprite.Sprite):
    def __init__(self, image, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect = self.rect.move(location[0]-int(self.rect.width/2), location[1])

    def update(self):
        if self.rect.midbottom[1] <= 0:
            self.kill()
        self.rect = self.rect.move(0, -11)


class Shooter(pygame.sprite.Sprite):
    def __init__(self, image, frozenImage, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.defaultImage = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = (location[0]-int(self.rect.width/2), location[1]-self.rect.height)
        self.area = pygame.display.get_surface().get_rect()
        self.speed = 0
        self.freezeCounter = 0
        self.slowCounter = 0
        self.frozenImage = frozenImage

    def update(self):
        if self.rect.right > self.area.right and self.speed > 0:
            self.speed = 0
        if self.rect.left < self.area.left and self.speed < 0:
            self.speed = 0
        if self.freezeCounter == 0:
            self.rect = self.rect.move(self.speed, 0)
        if self.slowCounter > 0:
            self.slowCounter -= 1
            # speed up movement to default if "slow" ends
            if self.slowCounter == 0:
                self.speed *= 10
        if self.freezeCounter > 0:
            self.freezeCounter -= 1
            if self.freezeCounter == 0:
                self.image = self.defaultImage

    def freeze(self):
        self.stopMoving()
        self.freezeCounter = 80
        self.image = self.frozenImage

    def slow(self):
        self.stopMoving()
        self.slowCounter = 100

    def stopMoving(self):
        self.speed = 0

    def moveRight(self):
        if self.slowCounter > 0:
            self.speed = 1
        else:
            self.speed = 10

    def moveLeft(self):
        if self.slowCounter > 0:
            self.speed = -1
        else:
            self.speed = -10


class Background(pygame.sprite.Sprite):
    def __init__(self, image, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class StatusBar(pygame.sprite.Sprite):
    def __init__(self, location, rect, status):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(location, rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.font = pygame.freetype.SysFont("Alegreya Sans",24)
        self.status = status

    def draw(self, screen):
        self.image.fill((0,113,156))
        self.font.render_to(self.image, (5,5), "Enemies Destroyed: "+str(self.status.kills), fgcolor=(0, 0, 0))
        self.font.render_to(self.image, (300,5), "Lives: "+str(self.status.lives), fgcolor=(0, 0, 0))
        self.font.render_to(self.image, (450,5), "Level: "+str(self.status.level), fgcolor=(0, 0, 0))
        screen.blit(self.image, self.rect)

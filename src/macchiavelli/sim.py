from macchiavelli.game import Macchiavelli, Player
import pygame
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS_DIR = ROOT / "assets" / "cards"


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    clock = pygame.time.Clock()
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill((0, 128, 0))  # fill the screen with a green color

        # RENDER YOUR GAME HERE
        card = pygame.image.load(CARDS_DIR/"clubs_2.png").convert_alpha()
        width, height = card.get_size()
        new_width = 60
        new_height = int(height * new_width / width)

        card = pygame.transform.smoothscale(card, (new_width, new_height))
        screen.blit(card, (100, 100))
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


if __name__ == "__main__":
    main()

# player1 = Player()
# player2 = Player()
# match = Macchiavelli(players=[player1, player2])

# match.start_game()


# while True:
#     current_player = match.players[match.curr_player_index]
#     print(f"Player {match.curr_player_index + 1}'s turn")
#     print(f"Current hand: {current_player.cards}")
#     print(f"Current table: {match.table}")

#     try:
#         match.player_turn(current_player)
#     except ValueError as e:
#         print(e)
#         continue

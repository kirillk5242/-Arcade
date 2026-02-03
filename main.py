import arcade
from random import randrange as rnd
import sqlite3
import datetime

SCREEN_WIDTH = 770
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Арканоид"
FPS = 60

PADDLE_WIDTH = 200
PADDLE_HEIGHT = 10
PADDLE_SPEED = 15

BALL_RADIUS = 20
INITIAL_BALL_SPEED = 6

BLOCK_COLS = 6
BLOCK_ROWS = 4

conn = sqlite3.connect("arkanoid_scores.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    score INTEGER,
    level INTEGER,
    date TEXT
)
""")
conn.commit()


def save_score(name, score, level):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO scores (name, score, level, date) VALUES (?, ?, ?, ?)",
        (name, score, level, date)
    )
    conn.commit()


def show_top_scores():
    cursor.execute(
        "SELECT name, score, level, date FROM scores ORDER BY score DESC LIMIT 10"
    )
    print("\n===== ТОП 10 =====")
    for i, row in enumerate(cursor.fetchall(), start=1):
        print(f"{i}. {row[0]} — {row[1]} очков, уровень {row[2]}, {row[3]}")
    print("==================\n")


class Paddle(arcade.SpriteSolidColor):
    def __init__(self):
        super().__init__(PADDLE_WIDTH, PADDLE_HEIGHT, arcade.color.DARK_GREEN)
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = 30
        self.change_x = 0


class Ball(arcade.SpriteCircle):
    def __init__(self):
        super().__init__(BALL_RADIUS, arcade.color.PURPLE)
        self.center_x = rnd(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
        self.center_y = SCREEN_HEIGHT // 2
        self.change_x = 1
        self.change_y = -1


class Block(arcade.SpriteSolidColor):
    def __init__(self, x, y, color):
        super().__init__(100, 50, color)
        self.center_x = x
        self.center_y = y


class Arkanoid(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.player_list = arcade.SpriteList()
        self.ball_list = arcade.SpriteList()
        self.block_list = arcade.SpriteList()
        self.paddle = Paddle()
        self.ball = Ball()
        self.player_list.append(self.paddle)
        self.ball_list.append(self.ball)
        self.score = 0
        self.level = 1
        self.ball_speed = INITIAL_BALL_SPEED
        self.create_blocks()

    def create_blocks(self):
        self.block_list.clear()
        for i in range(BLOCK_COLS):
            for j in range(BLOCK_ROWS):
                x = 60 + i * 120
                y = SCREEN_HEIGHT - 60 - j * 60
                color = (rnd(30, 255), rnd(30, 255), rnd(30, 255))
                self.block_list.append(Block(x, y, color))

    def on_draw(self):
        self.clear()
        self.block_list.draw()
        self.player_list.draw()
        self.ball_list.draw()
        arcade.draw_text(
            f"Очки: {self.score}",
            10, 10,
            arcade.color.INDIGO,
            20
        )
        arcade.draw_text(
            f"Уровень: {self.level}",
            SCREEN_WIDTH - 150, 10,
            arcade.color.INDIGO,
            20
        )

    def on_update(self, delta_time):
        self.paddle.center_x += self.paddle.change_x
        if self.paddle.left < 0:
            self.paddle.left = 0
        if self.paddle.right > SCREEN_WIDTH:
            self.paddle.right = SCREEN_WIDTH

        self.ball.center_x += self.ball_speed * self.ball.change_x
        self.ball.center_y += self.ball_speed * self.ball.change_y

        if self.ball.left <= 0 or self.ball.right >= SCREEN_WIDTH:
            self.ball.change_x *= -1
        if self.ball.top >= SCREEN_HEIGHT:
            self.ball.change_y *= -1

        if arcade.check_for_collision(self.ball, self.paddle) and self.ball.change_y < 0:
            self.ball.change_y *= -1

        hit_list = arcade.check_for_collision_with_list(self.ball, self.block_list)
        if hit_list:
            for block in hit_list:
                block.remove_from_sprite_lists()
                self.score += 1
            self.ball.change_y *= -1

        if self.ball.bottom < 0:
            arcade.close_window()
            name = input("Введите ваше имя: ")
            save_score(name, self.score, self.level)
            show_top_scores()

        if len(self.block_list) == 0:
            self.level += 1
            self.ball_speed = INITIALIAL_BALL_SPEED = INITIAL_BALL_SPEED + self.level
            self.ball.center_x = rnd(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
            self.ball.center_y = SCREEN_HEIGHT // 2
            self.create_blocks()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.paddle.change_x = -PADDLE_SPEED
        elif key == arcade.key.RIGHT:
            self.paddle.change_x = PADDLE_SPEED

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.paddle.change_x = 0


if __name__ == "__main__":
    game = Arkanoid()
    arcade.run()

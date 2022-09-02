import Graphics as gr
import pyautogui
import random
import tkinter as tk
import  tkinter.messagebox as mb


class Window:
    def __init__(self):
        self.size_x = 500
        self.size_y = 500
        self.window = gr.GraphWin("Arkanoid", self.size_x, self.size_y)


class Block:
    def __init__(self, start_pos_x=230, start_pos_y=450):
        self.block = None
        self.start_pos_x = start_pos_x
        self.start_pos_y = start_pos_y
        self.colour = "green"
        self.size_x = 80
        self.size_y = 20
        self.velocity = 0

    def create_block(self):
        self.block = gr.Rectangle(gr.Point(self.start_pos_x, self.start_pos_y),
                                  gr.Point(self.start_pos_x + self.size_x, self. start_pos_y + self.size_y))
        self.block.setFill(self.colour)


class Ball:
    def __init__(self, x=200, y=200, vx=1, vy=1):
        self.ball = None
        self.start_pos = gr.Point(x, y)
        self.start_velocity = gr.Point(abs(vx), abs(vx))
        self.velocity = gr.Point(vx, vy)
        self.radius = 5
        self.colour = "red"

    def create_ball(self):
        self.ball = gr.Circle(self.start_pos, self.radius)
        self.ball.setFill(self.colour)


class Info:
    def __init__(self):
        self.score = None
        self.lb_sc = None
        self.level = None
        self.lb_lv = None
        self.lv_count = 0
        self.sc_count = 0
        self.font = 14
        self.position_x_level = 430
        self.position_y = 475
        self.position_x_score = 5

    def create(self, window):
        self.lb_lv = tk.Label(window, text="Level:")
        self.lb_lv.config(font=self.font)
        self.lb_lv.place(x=self.position_x_level, y=self.position_y)

        self.level = tk.Entry(window, width=2)
        self.level.config(font=self.font)
        self.level.insert(0, str(self.lv_count))
        self.level.place(x=self.position_x_level + 45, y=self.position_y)

        self.lb_sc = tk.Label(window, text="Score:")
        self.lb_sc.config(font=self.font)
        self.lb_sc.place(x=self.position_x_score, y=self.position_y)

        self.score = tk.Entry(window, width=4)
        self.score.config(font=self.font)
        self.score.insert(0, str(self.sc_count))
        self.score.place(x=self.position_x_score + 50, y=self.position_y)

    def level_change(self):
        self.lv_count += 1
        self.level.delete(0, tk.END)
        self.level.insert(0, str(self.lv_count))

    def score_change(self, velocity_ball):
        self.sc_count = int(self.sc_count + 10 * abs(velocity_ball))
        self.score.delete(0, tk.END)
        self.score.insert(0, str(self.sc_count))


class App(tk.Tk):
    def __init__(self):
        super.__init__(self)
        btn_yes = tk.Button(self, text="Да", command=self.if_yes)
        btn_no = tk.Button(self, text="Нет", command=self.if_no)
        btn_yes.pack()
    def if_yes(self):
        main()

    def if_no(self):
        exit(0)


window = Window()

def main():

    static_block = []

    user = Block()
    user.create_block()
    user.block.draw(window.window)

    ball = Ball(random.randint(100, 400), random.randint(250, 350), random.choice([1, -1]), random.choice([1, -1]))
    ball.create_ball()
    ball.ball.draw(window.window)

    counter = Info()
    counter.create(window.window)

    #начальное положение курсора мыши
    coords_mouse = gr.Point(pyautogui.position().x, 0)

    with open('levels.dat', "r") as file:
        levels = file.readlines()

    create_static_block(static_block, levels, counter)
    #level = levels[0].split("/")

    while True:
        check_collision_wall(ball, window)
        check_collision_user_block(ball, user)
        check_collision_static_block(static_block, ball, counter)
        move_block(user, window, coords_mouse)
        move_ball(ball)
        check_finish_level(static_block, levels, counter)
        check_game_over(ball, window, user, static_block, levels)

        gr.time.sleep(0.001)


def check_finish_level(static_block, levels, counter):
    """
    Проверка все ли сбиты статические блоки, если "да", то взывается функция создание новых.
    """
    if len(static_block) == 0:
        create_static_block(static_block, levels, counter)


def create_static_block(static_block, levels, counter):
    """
    Создание статических блоков, по координатам из списка.
    """
    if len(levels) == 0:
        return

    level = levels[0].split("/")
    for i in range(len(level)):
        coord_block = level[i].split()
        bl = Block(int(coord_block[0]), int(coord_block[1]))
        bl.size_x = 60
        bl.size_y = 15
        bl.colour = "yellow"
        bl.create_block()
        bl.block.draw(window.window)
        static_block.append(bl)

    counter.level_change()
    levels.pop(0)


def move_ball(ball):
    """
    Движение шарика.
    """
    ball.ball.move(ball.velocity.x, ball.velocity.y)


def check_collision_wall(ball, window):
    """
    Проверка столкновений со стенами.
    """
    if ball.ball.p1.x <= 0 or ball.ball.p2.x >= window.size_x:
        ball.velocity.x = - ball.velocity.x
    if ball.ball.p1.y <= 0:
        ball.velocity.y = - ball.velocity.y


def check_collision_user_block(ball, user):
    """
    Проверка столкновений с блоком игрока.
    """
    if ball.ball.p1.y > user.block.p1.y and ball.ball.p2.y < user.block.p2.y and ball.ball.p1.x > user.block.p1.x \
            and ball.ball.p2.x < user.block.p2.x:
        return

    elif user.block.p1.y <= ball.ball.p2.y <= user.block.p2.y and ball.ball.p1.y < user.block.p2.y\
            and user.block.p1.x <= ball.ball.p2.x - ball.radius <= user.block.p2.x:
        point_collision_ball = ball.ball.p2.x - ball.radius
        point_collision_user = user.block.p1.x + user.size_x/2
        delta_point = point_collision_ball - point_collision_user
        percent = abs(delta_point/(user.size_x/2))

        if ball.velocity.y < 3:
            ball.start_velocity.x = ball.start_velocity.x + 0.1
            ball.velocity.y = ball.velocity.y + 0.1

        if delta_point < 0:
            ball.velocity.x = - ball.start_velocity.x * percent
        elif delta_point > 0:
            ball.velocity.x = ball.start_velocity.x * percent
        else:
            ball.velocity.x = 0.1

        ball.velocity.y = - ball.velocity.y

    elif user.block.p1.x <= ball.ball.p2.x and ball.ball.p1.x <= user.block.p2.x \
            and user.block.p1.y < ball.ball.p2.y - ball.radius + 1 < user.block.p2.y:
        ball.velocity.x = - ball.velocity.x


def check_collision_static_block(static_block, ball, counter):
    """
    Проверка столкновений с статическими блоками.
    """
    for i in range(len(static_block)):
        if ball.ball.p1.y <= static_block[i].block.p2.y and ball.ball.p2.y >= static_block[i].block.p1.y\
                and static_block[i].block.p1.x <= ball.ball.p2.x - ball.radius <= static_block[i].block.p2.x:
            ball.velocity.y = - ball.velocity.y
            static_block[i].block.undraw()
            static_block.pop(i)
            counter.score_change(ball.velocity.y)
            break
        elif ball.ball.p2.x >= static_block[i].block.p1.x and ball.ball.p1.x <= static_block[i].block.p2.x\
            and ball.ball.p2.y - ball.radius <= static_block[i].block.p2.y\
                and ball.ball.p1.y + ball.radius >= static_block[i].block.p1.y:
            ball.velocity.x = - ball.velocity.x
            static_block[i].block.undraw()
            static_block.pop(i)
            counter.score_change(ball.velocity.y)
            break


def move_block(user, window, coords_mouse):
    """
    Движение блока-игрока за счет положения курсора мыши.
    """
    user.velocity = 0
    coords_mouse_new = pyautogui.position().x
    user.velocity = coords_mouse_new - coords_mouse.x

    if user.velocity > 0 and user.block.p2.x < window.size_x:
        if user.block.p2.x + user.velocity > window.size_x:
            user.velocity = window.size_x - user.block.p2.x
        user.block.move(user.velocity, 0)
    elif user.velocity < 0 and user.block.p1.x > 0:
        if user.block.p1.x + user.velocity < 0:
            user.velocity = - user.block.p1.x
        user.block.move(user.velocity, 0)

    coords_mouse.x = coords_mouse_new


def check_game_over(ball, window, user, static_block, levels):
    """
    Проверка на окончание игры.
    """
    if ball.ball.p2.y > window.size_x:
        for i in range(len(static_block)):
            static_block[i].block.undraw()
        ball.ball.undraw()
        user.block.undraw()
        main()
    elif len(levels) == 0 and len(static_block) == 0:
        app = App()


if __name__ == "__main__":
    main()

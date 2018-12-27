from psychopy.core import Clock
from psychopy import visual, event
timer = Clock()


def draw_guess_stimuli(factors, studied, studied_rect, unstudied, unstudied_rect):

    if factors.safe == 'studied':
        studied.color = 'green'
        unstudied.color = 'red'
    else:
        unstudied.color = 'green'
        studied.color = 'red'

    studied.draw()
    studied_rect.draw()
    unstudied.draw()
    unstudied_rect.draw()


def guess_response(factors, mouse, studied_rect, unstudied_rect):

    mouse.setPos((0, -.1))  # Return mouse to near center
    mouse.setVisible(1)

    timer.reset()
    resp = None
    while resp is None:
        if mouse.isPressedIn(studied_rect, [0]):
            rt = timer.getTime()
            resp = 'studied'
        if mouse.isPressedIn(unstudied_rect, [0]):
            rt = timer.getTime()
            resp = 'unstudied'

    # Wait until the mouse is no longer pressed, by doing nothing as long as it is pressed
    while mouse.getPressed()[0]:
        pass

    if resp == factors.type and resp == factors.safe:
        points = 3
    elif resp == factors.type and resp != factors.safe:
        points = 1
    elif resp != factors.type and resp == factors.safe:
        points = -1
    else:
        points = -3

    return resp, rt, points


def points_feedback(text, points):

    text.text = str(points)
    text.draw()


def draw_study_trial(x, word, faces=None):

    word.text = x.word
    word.draw()
    if faces is not None:
        faces[x.source].draw()


def draw_source_test(x, word, question, options):

    word.text = x.word
    word.draw()
    question.draw()
    options.draw()


def source_test_response(x):
    response_map = {'z': 'm', 'slash': 'f'}
    event.clearEvents()
    timer.reset()

    pressed = []
    while not pressed:
        pressed = event.getKeys(['z', 'slash'], timeStamped=timer)

    response = response_map[pressed[0][0]]
    rt = pressed[0][1]
    correct = True if response == x.source else False
    points = 2 if correct else -2

    return response, rt, correct, points


def draw_source_feedback(x, points, *args):
    if args is not None:
        draw_study_trial(x, *args)
    points.draw()


def draw_recog_stimuli(x, word, *args):
    draw_guess_stimuli(x, *args)
    word.text = x.word
    word.draw()


def give_instructions(win, event, text_list):

    instructions = visual.TextStim(win, wrapWidth=1.75, height=.085, text=text_list[0])
    instructions.draw()
    for i in range(len(text_list)):
        win.flip()
        if i < (len(text_list) - 1):
            instructions.text = text_list[i + 1]
            instructions.draw()
        event.waitKeys(keyList=['space'])


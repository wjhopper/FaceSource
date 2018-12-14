from psychopy.core import Clock

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

    resp = None
    while resp is None:
        if mouse.isPressedIn(studied_rect, [0]):
            resp = 'studied'
        if mouse.isPressedIn(unstudied_rect, [0]):
            resp = 'unstudied'

    # Wait until the mouse is no longer pressed, by doing nothing as long as it is pressed
    while mouse.getPressed()[0]:
        pass

    if resp == factors.correct and resp == factors.safe:
        points = 3
    elif resp == factors.correct and resp != factors.safe:
        points = 1
    elif resp != factors.correct and resp == factors.safe:
        points = -1
    else:
        points = -3

    return resp, points


def points_feedback(text, points):

    text.text = str(points)
    text.draw()


def draw_study_trial(x, faces, word):

    word.text = x.word
    word.draw()
    faces[x.source].draw()


def draw_source_test(x, word, question, options):

    word.text = x.word
    word.draw()
    question.draw()
    options.draw()


def source_test_response(x, event):
    timer.reset()
    response_map = {'z': 'm', '/': 'f'}

    pressed = []
    while pressed is None:
        pressed = event.getKeys(['z', '/'], timeStamped=timer)

    response = pressed[0][0]
    RT = pressed[0][1]
    correct = True if response_map[pressed[0][0]] == x.source else False
    points = 2 if correct else -2
    return response, RT, correct, points


def draw_source_feedback(x, points, *args):
    draw_study_trial(x, *args)
    points.draw()

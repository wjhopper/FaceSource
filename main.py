# Import the PsychoPy libraries that you want to use
from psychopy import core, visual, event
import random

# Create a window
win = visual.Window([1000, 800], monitor="testMonitor")
mouse = event.Mouse()
# Create a stimulus for a certain window
studied = visual.TextStim(win, text="Studied", pos = (-.75, .75))
unstudied = visual.TextStim(win, text="Not Studied", pos = (.75, .75))
studied_rect = visual.Rect(win, units='pix', pos=[(a*b)/2 for a,b in zip(studied.pos, win.size)],
                           width=studied.boundingBox[0] + 20, height=studied.boundingBox[1] + 20,
                           )
unstudied_rect = visual.Rect(win, units='pix', pos=[(a*b)/2 for a,b in zip(unstudied.pos, win.size)],
                             width=unstudied.boundingBox[0] + 20, height=unstudied.boundingBox[1] + 20,
                             )
# Draw the stimulus to the window. We always draw at the back buffer of the window.
safe_resp = ['studied','unstudied']*4
random.shuffle(safe_resp)
for x in safe_resp:
    if x == 'studied':
        studied.color = 'green'
        unstudied.color = 'red'
    else:
        unstudied.color = 'green'
        studied.color = 'red'

    studied.draw()
    studied_rect.draw()
    unstudied.draw()
    unstudied_rect.draw()
    win.flip()
    while True:
        if mouse.isPressedIn(studied_rect, [0]):
            resp = 'studied'
            mouse.clickReset()
            print(mouse.isPressedIn(studied_rect, [0]))
            print('click1')
            break
        if mouse.isPressedIn(unstudied_rect, [0]):
            resp = 'unstudied'
            mouse.clickReset()
            print(mouse.isPressedIn(unstudied_rect, [0]))
            print('click2')
            break
    win.flip()
    core.wait(1)
# Close the window
win.close()

# Close PsychoPy
core.quit()
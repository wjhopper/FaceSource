# Import the PsychoPy libraries that you want to use
from psychopy import core, visual, event
import expand

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

bias_trials = expand.expand_grid({'safe': ['studied','unstudied'],
                                  'correct':[True, False]
                                 })
bias_trials = expand.replicate(bias_trials, 2)
bias_trials = bias_trials.sample(frac=1).reset_index(drop=True)

for x in bias_trials.itertuples():
    if x.safe == 'studied':
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

    resp = None
    while resp is None:
        if mouse.isPressedIn(studied_rect, [0]):
            resp = 'studied'
        if mouse.isPressedIn(unstudied_rect, [0]):
            resp = 'unstudied'
    # Wait until the mouse is no longer pressed, by doing nothing as long as it is pressed
    while mouse.getPressed()[0]:
        pass

    mouse.clickReset()
    win.flip()
    core.wait(1)

# Close the window
win.close()

# Close PsychoPy
core.quit()
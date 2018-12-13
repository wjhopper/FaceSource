from psychopy import core, visual, event, prefs
import expand
import trials

# Create a window and mouse
win = visual.Window([1500, 1100], monitor="testMonitor")
mouse = event.Mouse()
event.globalKeys.add(key='q', func=core.quit, name='shutdown')

intro_text = [
    """Welcome to the experiment! In this experiment, you'll study a list of words to remember, and take two memory tests \
afterwards.
    
On the first test, you will be shown a word, and have to indicate if you studied the word during this experiment, or \
did not study it. You will earn points based on your performance on this test.
    
You should try to earn as many points as possible. The experiment will end when you complete the entire test OR when \
you earn 700 points, whichever comes first. 
    
Press the Space Bar to move forward.
    """,

    """On each test trial, one response will be "safe", and the other response will be "risky". "Safe" and "Risky" \
responses earn you different amounts of points.
    
If you choose a safe response, and it is the correct answer, you will earn 3 points.
    
If you choose a risky response, and it is the correct answer, you will only earn 1 point.
    
If you choose a safe response, and it is the wrong answer, you will only lose one point.
    
If you choose a risky response, and it is the wrong answer, you will lose 3 points.
    
Press the Space Bar to move forward.
    """,

    """On each trial, the "safe" response will be shown in green text, and the "risky" response will be shown in red text.
    
Let's start by getting some practice using the "safe" and "risky" response options. During this practice,  you'll \
see only the "Studied" and "Not Studied" response options on the screen, but there won't be a test word. One \
response will be the correct answer, but you won't be able to tell which one it is until after you choose. 
    
Make your guess by clicking on one of the options with the mouse. If you guess correctly, you earn points. If you \
guess incorrectly, you'll lose points.
    
To see how well guessing the "risky" option works, only choose the response shown in red during this practice round.

Press the Space Bar to begin the first practice round.
    """
]
instructions = visual.TextStim(win,wrapWidth=1.75, height=.085)
for i in intro_text:
    instructions.text = i
    instructions.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# Create studied/unstudied "button" components
studied = visual.TextStim(win, text="Studied", pos=(.75, .75))
unstudied = visual.TextStim(win, text="Not Studied", pos=(-.75, .75))
studied_rect = visual.Rect(win, units='pix', pos=[(a*b)/2 for a, b in zip(studied.pos, win.size)],
                           width=studied.boundingBox[0] + 20, height=studied.boundingBox[1] + 20,
                           )
unstudied_rect = visual.Rect(win, units='pix', pos=[(a*b)/2 for a, b in zip(unstudied.pos, win.size)],
                             width=unstudied.boundingBox[0] + 20, height=unstudied.boundingBox[1] + 20,
                             )

# Text objects for displaying points earned feedback
guess_points_text = visual.TextStim(win, pos=(0, .75))
recog_points_text = visual.TextStim(win, pos=(0, -.75))
total_points_feedback = visual.TextStim(win, pos=(0, 0))

bias_trials = expand.expand_grid({'safe': ['studied', 'unstudied'],
                                  'correct': ['studied', 'unstudied']
                                  })
bias_trials = expand.replicate(bias_trials, 2)
bias_trials = bias_trials.sort_values(by=['correct', 'safe'])

for practice_round in [1,2]:
    if practice_round == 2:
        instructions.text = """
You'll now do one more round of guessing practice. This time, guess the safe response shown in green every trial, and \
see how many points you earn this time.

Press the Space Bar to begin.
"""
        instructions.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

    total_points = 0
    bias_trials = bias_trials.sample(frac=1).reset_index(drop=True)
    for x in bias_trials.itertuples():
        # Display guess probe and collect mouse click response
        trials.draw_guess_stimuli(x, studied, studied_rect, unstudied, unstudied_rect)
        win.flip()
        resp, trial_points = trials.guess_response(x, mouse, studied_rect, unstudied_rect)
        total_points += trial_points

        # Display points feedback with guess probe
        trials.draw_guess_stimuli(x, studied, studied_rect, unstudied, unstudied_rect)
        trials.points_feedback(guess_points_text, trial_points)
        win.flip()
        core.wait(1.5)

        # Blank screen ISI
        win.flip()
        core.wait(.5)

total_points_feedback.text = 'You earned %i points.\n\nPress the space bar to continue.' % total_points
total_points_feedback.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Close the window
win.close()

# Close PsychoPy
core.quit()

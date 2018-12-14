from psychopy import core, visual, event
import expand
import trials
import pandas as pd
import numpy as np
import glob
import random


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
instructions = visual.TextStim(win, wrapWidth=1.75, height=.085)
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
total_points_feedback = visual.TextStim(win, pos=(0, 0))

bias_trials = expand.expand_grid({'safe': ['studied', 'unstudied'],
                                  'correct': ['studied', 'unstudied']
                                  })
bias_trials = expand.replicate(bias_trials, 2, ignore_index=True)
bias_trials = bias_trials.sort_values(by=['correct', 'safe']).reset_index(drop=True)

for practice_round in [1, 2]:
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

# Set up pool of face-source stimuli files
faces_table = pd.DataFrame({'m': glob.glob("faces/m[1-8].bmp"),
                           'f': glob.glob("faces/f[1-8].bmp")
                            })
faces_table['m'] = np.random.permutation(faces_table['m'])
faces_table['f'] = np.random.permutation(faces_table['f'])

# Set up target and lure word pools
with open('words.txt', 'r') as f:
    words = f.read().splitlines()
target_pool = words[:104]  # 8 practice words, 96 words for real trials
lure_pool = words[104:(104+92)]  # 8 practice lures, 84 lures for real trials. 84 because primacy/recency items are not tested

# Cross source and block
practice_study_trials = expand.expand_grid({'source': ['m', 'f'],
                                            'block': list(range(1, 3)),
                                            })
# Replicate twice, to make 4 trials per block
practice_study_trials = expand.replicate(practice_study_trials, 2, ignore_index=True)
# Randomize the order of male/female sources in each block
practice_study_trials = practice_study_trials.groupby('block').apply(lambda y: y.sample(frac=1))
practice_study_trials = practice_study_trials.reset_index(drop=True)
# Add the words to study, chosen image file, and empty response variables to the conditions
practice_study_trials = pd.concat([practice_study_trials,
                                   pd.DataFrame({'word': target_pool[:8],
                                                 'file': [faces_table.loc[0, y] for y in practice_study_trials.source],
                                                 }),
                                   pd.DataFrame(np.full(shape=(practice_study_trials.shape[0], 4), fill_value=np.nan),
                                                columns=['response', 'RT', 'correct', 'points'])],
                                  axis=1)
# Put everything in a nice order
practice_study_trials = practice_study_trials[['block', 'word', 'source', 'file', 'response', 'RT', 'correct', 'points']]
practice_study_trials.set_index('block', drop=False)
# Make the image stimuli
face_stim = {'m': visual.ImageStim(win, image=faces_table.loc[0, 'm'], pos=(0, .4)),
             'f': visual.ImageStim(win, image=faces_table.loc[0, 'f'], pos=(0, .4))
             }
# Make the text stimuli, but don't put the text in yet
study_word = visual.TextStim(win, pos=(0, 0))

# Make the source responses text
source_response_opts = visual.TextStim(win, pos=(0, -.8), text="Z = Male                       / = Female")

# Make the source question text
source_question_text = visual.TextStim(win, pos=(0, .8), text="Did you study this word with a male or female face?")

# Make the source points feedback
source_points_feedback = visual.TextStim(win, pos=(0, -.2))

# Study Practice Loop
total_points = 0
for b in practice_study_trials.index.unique(0):
    block = practice_study_trials.loc[b]
    # Show stimuli
    for x in block.itertuples():
        # Study
        trials.draw_study_trial(x, face_stim, study_word)
        win.flip()
        core.wait(2)

        # Blank screen ISI
        win.flip()
        core.wait(.5)

        # Practice Test
        x = x.sample(frac=1)
        trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
        win.flip()
        response, RT, correct, points = trials.source_test_response(x, event)
        x[['response', 'RT', 'correct', 'points']] = [response, RT, correct, points]
        total_points += points
        source_points_feedback.text = str(points)
        trials.draw_source_feedback(x, source_points_feedback, face_stim, study_word)

# Close the window
win.close()

# Close PsychoPy
core.quit()

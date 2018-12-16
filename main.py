from psychopy import core, visual, event
import expand
import trials
import pandas as pd
import numpy as np
import glob

biases = ['studied', 'unstudied']  # This should become an argument

# Create a window and mouse
win = visual.Window([1280, 768])
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
see only the "Studied" and "Not Studied" response options on the screen, but there won't be a test word.

One response will be the correct answer, but you won't be able to tell which one it is until after you choose. 

Press the Space Bar to move forward.
    """,

    """Make your guess by clicking on one of the options with the mouse. If you guess correctly, you earn points. If you \
guess incorrectly, you'll lose points.
    
To see how well guessing the "risky" option works, only choose the response shown in red during this practice round.

Press the Space Bar to begin the first practice round.
    """
]

# Give intro instructions
trials.give_instructions(win, event, intro_text)

# Create studied/unstudied "button" components
studied_guess = visual.TextStim(win, text="Studied", pos=(.75, .75))
unstudied_guess = visual.TextStim(win, text="Not Studied", pos=(-.75, .75))
studied_guess_rect = visual.Rect(win, units='pix', pos=[(a * b) / 2 for a, b in zip(studied_guess.pos, win.size)],
                                 width=studied_guess.boundingBox[0] + 20, height=studied_guess.boundingBox[1] + 20,
                                 )
unstudied_guess_rect = visual.Rect(win, units='pix', pos=[(a * b) / 2 for a, b in zip(unstudied_guess.pos, win.size)],
                                   width=unstudied_guess.boundingBox[0] + 20, height=unstudied_guess.boundingBox[1] + 20,
                                   )

# Text objects for displaying points earned feedback
guess_points_text = visual.TextStim(win, pos=(0, .75))
total_points_feedback = visual.TextStim(win, pos=(0, 0))

# "Make a guess" reminder instructions
guess_reminder = visual.TextStim(win, pos=(0, .75), text="Make a guess")

bias_trials = expand.expand_grid({'safe': biases,
                                  'type': ['studied', 'unstudied']
                                  })
bias_trials = expand.replicate(bias_trials, 2, ignore_index=True)
bias_trials = bias_trials.sort_values(by=['type', 'safe']).reset_index(drop=True)

for practice_round in [1, 2]:
    if practice_round == 2:
        guess_instructions = ["""
You'll now do one more round of guessing practice.

This time, guess the safe response shown in green every trial, and see how many points you earn guessing this way.

Press the Space Bar to begin.
"""]
        trials.give_instructions(win, event, guess_instructions)

    total_points = 0
    bias_trials = bias_trials.sample(frac=1).reset_index(drop=True)
    for x in bias_trials.itertuples():
        # Display guess probe and collect mouse click response
        guess_reminder.draw()
        trials.draw_guess_stimuli(x, studied_guess, studied_guess_rect, unstudied_guess, unstudied_guess_rect)
        win.flip()
        resp, trial_points = trials.guess_response(x, mouse, studied_guess_rect, unstudied_guess_rect)
        total_points += trial_points
        mouse.setVisible(0)

        # Display points feedback with guess probe
        trials.draw_guess_stimuli(x, studied_guess, studied_guess_rect, unstudied_guess, unstudied_guess_rect)
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
practice_study_trials = practice_study_trials.groupby('block').apply(lambda z: z.sample(frac=1)).reset_index(drop=True)
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
practice_study_trials.set_index(['block', list(range(len(practice_study_trials)))],
                                drop=False, inplace=True)

# Make the image stimuli
face_stim = {'m': visual.ImageStim(win, image=faces_table.loc[0, 'm'], pos=(0, .4)),
             'f': visual.ImageStim(win, image=faces_table.loc[0, 'f'], pos=(0, .4))
             }
# Make the text stimuli, but don't put the text in yet
study_word = visual.TextStim(win, pos=(0, 0))

# Make the source responses text
source_response_opts = visual.TextStim(win, pos=(0, -.8), text="Z = Male                       / = Female")

# Make the source question text
source_question_text = visual.TextStim(win, pos=(0, .8), text="Did you study this word with a male or female face?",
                                       wrapWidth=1.5)

# Make the source points feedback
source_points_feedback = visual.TextStim(win, pos=(0, -.2))

# Study Practice Instructions
study_practice_instructions = [
    """Now that you know how the points work with "safe" and "risky" options, it's time to learn about the words you'll \
be studying and memorizing in this experiment.

You'll see words on the screen one at a time, and get to see each word for a few seconds. Each word you see will also be \
shown with a person's face. In addition to remembering the word you see, you also need to remember if you studied it \
with a male or female face.

Press the Space Bar to move forward.

""",
    """To help you remember if you studied a word with a male or female face, you'll get practice during the study list.

After you study four word and face pairs, you'll take a test on those four words, and for each one, decide if the word was \
studied with a male or female face.

On the practice test, press the "z" key for "Male Face" and press the "/" key for "Female Face". You'll earn 2 points for \
a correct answer, and lose 2 points for an incorrect answer, so try your best! After the test on each word, you'll get a \
reminder about the correct answer.

Press the Space Bar to move forward.
""",
    """Let's begin with a short list of practice words and faces. Press the Space Bar to begin studying the practice list
"""
]

trials.give_instructions(win, event, study_practice_instructions)

# Study Practice Loop
total_points = 0
for b in practice_study_trials.index.unique(0):
    block = practice_study_trials.loc[[b]]
    # Show stimuli
    for x in block.itertuples():
        # Study
        trials.draw_study_trial(x, face_stim, study_word)
        win.flip()
        core.wait(2)

        # Blank screen ISI
        win.flip()
        core.wait(.5)

    block = block.sample(frac=1)
    for x in block.itertuples():
        # Practice Test
        trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
        win.flip()

        # Waiting for key response
        response, RT, correct, points = trials.source_test_response(x, event)
        block.loc[x.Index, ['response', 'RT', 'correct', 'points']] = [response, RT, correct, points]
        total_points += points

        # Give the accuracy/point feedback
        source_points_feedback.text = str(points)
        trials.draw_source_feedback(x, source_points_feedback, face_stim, study_word)
        win.flip()
        core.wait(2)

        # ISI
        win.flip()
        core.wait(.5)

    practice_study_trials.update(block)

# Creating Recognition Practice trials schema
# Create data frame with rows of targets
practice_recog_trials = pd.concat([practice_study_trials[['word']].reset_index(drop=True),
                                   pd.Series(['studied']*len(practice_study_trials), name='type')
                                   ], axis=1
                                  )
# Add rows of lures (unstudied)
practice_recog_trials = pd.concat([practice_recog_trials,
                                   pd.DataFrame({'word': lure_pool[:len(practice_recog_trials)],
                                                 'type': ['unstudied']*len(practice_study_trials)})
                                   ],
                                  join_axes=[pd.Index(['word', 'type'])],
                                  ignore_index=True
                                  )
# Assign items to bias conditions
practice_recog_trials = practice_recog_trials.groupby('type', group_keys=False)
practice_recog_trials = practice_recog_trials.apply(lambda z:
                                                    z.assign(safe=np.random.permutation(biases*(len(z)/len(biases))))
                                                    )
# Shuffle trial order
practice_recog_trials = practice_recog_trials.sample(frac=1).reset_index(drop=True)
# Add empty columns for response variables
practice_recog_trials = practice_recog_trials.reindex(columns=practice_recog_trials.columns.tolist() +
                                                      ['guess', 'guess_correct', 'guess_RT', 'guess_points',
                                                       'recog', 'recog_correct', 'recog_RT', 'recog_points'
                                                       ])

# Creating visual stimuli for guess & recognition tests
# Recognition response buttons
studied_recog = visual.TextStim(win, text="Studied", pos=(.75, -.75))
unstudied_recog = visual.TextStim(win, text="Not Studied", pos=(-.75, -.75))
studied_recog_rect = visual.Rect(win, units='pix', pos=[(a * b) / 2 for a, b in zip(studied_recog.pos, win.size)],
                                 width=studied_recog.boundingBox[0] + 20, height=studied_recog.boundingBox[1] + 20,
                                 )
unstudied_recog_rect = visual.Rect(win, units='pix', pos=[(a * b) / 2 for a, b in zip(unstudied_recog.pos, win.size)],
                                   width=unstudied_recog.boundingBox[0] + 20, height=unstudied_recog.boundingBox[1] + 20,
                                   )

# Recognition points feedback
recog_points_text = visual.TextStim(win, pos=(0, -.75))

# Recognition Practice Instructions
recognition_practice_instructions = [
    """Now it's time to test your memory for the words you studied. This test will have two parts on each trial.
    
Before you see the test word, you'll have to guess whether the word that appears will be a word you studied, or new, \
unstudied word. Just like the guessing practice you did in the beginning, one option will be "Safe" (in green) and the \
other will be "Risky" (in red).

After you make your guess, the test word will appear. Sometimes this will be a word you studied, and sometimes it will \
be a new, unstudied word. Click on the buttons along the bottom of the screen to respond studied or unstudied, once you \
decide. Just like the guessing part, one option will be "Safe" and the other will be "Risky".

Press the Space Bar to move forward.
""",

    """Let's practice by testing your memory for the short list of words you just studied.

Press the Space Bar to begin the memory test
"""
]

trials.give_instructions(win, event, recognition_practice_instructions)

for x in practice_recog_trials.itertuples():

    # Draw the guess response buttons
    guess_reminder.draw()
    trials.draw_guess_stimuli(x, studied_guess, studied_guess_rect, unstudied_guess, unstudied_guess_rect)
    win.flip()
    # Collect guess responses
    guess, guess_points = trials.guess_response(x, mouse, studied_guess_rect, unstudied_guess_rect)
    total_points += guess_points

    # "Deactivate" the guess response buttons
    for y in [studied_guess_rect, unstudied_guess_rect]:
        y.opacity = .25
    for y in [studied_guess, unstudied_guess]:
        y.contrast = .25
    trials.draw_guess_stimuli(x, studied_guess, studied_guess_rect, unstudied_guess, unstudied_guess_rect)

    # Draw the recognition probes
    trials.draw_recog_stimuli(x, study_word, studied_recog, studied_recog_rect, unstudied_recog, unstudied_recog_rect)
    win.flip()
    recog, recog_points = trials.guess_response(x, mouse, studied_recog_rect, unstudied_recog_rect)
    total_points += recog_points

    # "Deactivate" the recognition response buttons
    for y in [studied_recog_rect, unstudied_recog_rect]:
        y.opacity = .25
    for y in [studied_recog, unstudied_recog]:
        y.contrast = .25
    trials.draw_guess_stimuli(x, studied_guess, studied_guess_rect, unstudied_guess, unstudied_guess_rect)
    trials.draw_recog_stimuli(x, study_word, studied_recog, studied_recog_rect, unstudied_recog, unstudied_recog_rect)

    mouse.setVisible(0)

    # Give the feedback
    guess_points_text.text = str(guess_points)
    recog_points_text.text = str(recog_points)
    guess_points_text.draw()
    recog_points_text.draw()

    t = core.getTime()
    win.flip()

    # Save trial data
    practice_recog_trials.loc[x.Index, ['guess', 'guess_points', 'recog', 'recog_points']] = \
        [guess, guess_points, recog, recog_points]
    # Reset opacity for all 'buttons'
    for y in [studied_recog_rect, unstudied_recog_rect, studied_guess_rect, unstudied_guess_rect]:
        y.opacity = 1
    for y in [studied_recog, unstudied_recog, studied_guess, unstudied_guess]:
        y.contrast = 1
    core.wait(2 - (t - core.getTime()))

    win.flip()
    core.wait(.5)

# Source testing
practice_source_test = practice_study_trials.copy()
practice_source_test[['response', 'RT', 'correct', 'points']] = np.nan
practice_source_test = practice_source_test.sample(frac=1)

# Source Practice Instructions
source_practice_instructions = [
    "You've earned %i total points so far. Press the Space Bar to continue." % total_points,

    """It's time for one last test. On this final test, you'll be shown each word that you studied, and your job is to \
remember if it was studied with a male or a female face".

This test will be just like when  you practiced during the study list. Press the "z" key for "Male Face" and press \
the "/" key for "Female Face".

Press the Space Bar to begin the face memory test.
"""
]

trials.give_instructions(win, event, source_practice_instructions)

for x in practice_source_test.itertuples():
    # Source test probe
    trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
    win.flip()

    # Waiting for key response
    response, RT, correct, points = trials.source_test_response(x, event)
    total_points += points
    practice_source_test.loc[x.Index, ['response', 'RT', 'correct', 'points']] = [response, RT, correct, points]

    # # Give the accuracy/point feedback
    # source_points_feedback.text = str(points)
    # trials.draw_source_feedback(x, source_points_feedback, face_stim, study_word)
    # win.flip()
    # core.wait(2)

    # Blank screen ISI
    win.flip()
    core.wait(.5)

# Source Practice Instructions
begin_exp_instructions = [
    """That's the end of the practice phase - it's time for the real experiment.
    
The real experiment will be exactly like the practice you just did, but with more words to remember.

If you have any questions, please ask the experimenter now. If not, press the Space Bar to begin. Good luck!
"""
]

trials.give_instructions(win, event, begin_exp_instructions)

# Close the window
win.close()

# Close PsychoPy
core.quit()

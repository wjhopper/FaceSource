from psychopy import core, visual, event
import expand
import trials
import pandas as pd
import numpy as np
import glob
import uuid
import argparse
import random
import os


# Ensure Python's RNG is seeded with current time
random.seed()


def run(words, subject=None, bias=('studied', 'unstudied'), n_items=96, fullscreen=False):

    if subject is None:
        subject = uuid.uuid4()

    # Create a window
    if fullscreen:
        win = visual.Window(fullscr=True)
    else:
        win = visual.Window([1280, 768])

    # Create a mouse object
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
"""]

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

    # "Big Loss" Warning
    big_loss = visual.TextStim(win, pos=(0, 0), text="Big Loss! Careful using the risky option", color="red", height=.15,
                               wrapWidth=1.25)

    # "Make a guess" reminder instructions
    guess_reminder = visual.TextStim(win, pos=(0, .75), text="Make a guess")

    bias_trials = expand.expand_grid({'safe': bias,
                                      'type': ['studied', 'unstudied']
                                      })
    bias_trials = expand.replicate(bias_trials, 8/len(bias_trials), ignore_index=True)

    guess_instructions = ["""You'll now do one more round of guessing practice.

This time, guess the safe response shown in green every trial, and see how many points you earn guessing this way.

Press the Space Bar to begin.
"""]

    # GUESSING PRACTICE
    total_points = 0
    for practice_round in [1, 2]:
        if practice_round == 2:
            trials.give_instructions(win, event, guess_instructions)

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
    n_targets = 8 + n_items  # 8 practice words, 96 words (default) for real trials
    n_lures = (8 + n_items - 8)  # 8 practice lures, 8 fewer lures than targer for real trials because 4 primacy and recency items are not tested
    target_pool = words[:n_targets]
    lure_pool = words[n_targets:(n_targets + n_lures)]

    # Cross source and block
    practice_study_trials = expand.expand_grid({'source': ['m', 'f'],
                                                'block': list(range(1, 3)),
                                                })
    practice_study_trials.block = practice_study_trials.block.astype(np.int32)
    # Replicate twice, to make 4 trials per block
    practice_study_trials = expand.replicate(practice_study_trials, 2, ignore_index=True)
    # Randomize the order of male/female sources in each block
    practice_study_trials = practice_study_trials.groupby('block').apply(lambda z: z.sample(frac=1)).reset_index(drop=True)
    # Add the words to study, chosen image file, and empty response variables to the conditions
    practice_study_trials = pd.concat([practice_study_trials,
                                       pd.DataFrame({'word': target_pool[:8],
                                                     'file': [faces_table.loc[0, y] for y in practice_study_trials.source],
                                                     }),
                                       pd.DataFrame(np.full(shape=(practice_study_trials.shape[0], 5), fill_value=np.nan),
                                                    columns=['response', 'RT', 'correct', 'points', 'test_order'])],
                                      axis=1)
    # Put everything in a nice order
    practice_study_trials = practice_study_trials[['block', 'word', 'source', 'file', 'response', 'RT', 'correct', 'points', 'test_order']]
    practice_study_trials.set_index(['block', list(range(len(practice_study_trials)))],
                                    drop=False, inplace=True)

    # Remove words chosen for practice from the target pool
    target_pool = target_pool[8:]
    # Shuffle the target pool
    random.shuffle(target_pool)

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
        """Let's begin with a short list of practice words and faces. Press the Space Bar to begin studying the practice list.
"""]

    trials.give_instructions(win, event, study_practice_instructions)

    # Study Practice Loop
    total_points = 0
    for b in practice_study_trials.index.unique(0):
        block = practice_study_trials.loc[[b]]
        # Show stimuli
        for x in block.itertuples():
            # Study
            trials.draw_study_trial(x,  study_word, face_stim)
            win.flip()
            core.wait(2)

            # Blank screen ISI
            win.flip()
            core.wait(.5)

        block = block.sample(frac=1)
        block['test_order'] = list(range(1, len(block)+1))
        for x in block.itertuples():
            # Practice Test
            trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
            win.flip()

            # Waiting for key response
            response, rt, correct, points = trials.source_test_response(x)
            block.loc[x.Index, ['response', 'RT', 'correct', 'points']] = [response, rt, correct, points]

            # Give the accuracy/point feedback
            total_points += points
            source_points_feedback.text = str(points)
            trials.draw_source_feedback(x, source_points_feedback, study_word, face_stim)
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
    # Remove lures chosen for practice from the lure pool
    lure_pool = lure_pool[8:]
    # Shuffle remaining lure pool
    random.shuffle(lure_pool)

    # Assign items to bias conditions
    practice_recog_trials = practice_recog_trials.groupby('type', group_keys=False)
    practice_recog_trials = practice_recog_trials.apply(lambda z:
                                                        z.assign(safe=np.random.permutation(bias * (len(z) / len(bias))))
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
"""]

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
        win.flip()
        core.wait(2)

        if guess_points + recog_points == -6:
            big_loss.draw()
            win.flip()
            core.wait(2)

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

        core.wait(.5 - (core.getTime() - t))

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
"""]

    trials.give_instructions(win, event, source_practice_instructions)

    for x in practice_source_test.itertuples():
        # Source test probe
        trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
        win.flip()

        # Waiting for key response
        response, rt, correct, points = trials.source_test_response(x)
        total_points += points
        practice_source_test.loc[x.Index, ['response', 'RT', 'correct', 'points']] = [response, rt, correct, points]

        # Give accuracy feedback
        source_points_feedback.text = str(points)
        trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
        trials.draw_source_feedback(x, source_points_feedback, study_word)
        win.flip()
        core.wait(1)

        # Blank screen ISI
        win.flip()
        core.wait(.25)

    # Source Practice Instructions
    begin_exp_instructions = [
        """That's the end of the practice phase - it's time for the real experiment.
        
The real experiment will be exactly like the practice you just did, but with more words to remember.
    
If you have any questions, please ask the experimenter now. If not, press the Space Bar to begin. Good luck!
"""
    ]

    trials.give_instructions(win, event, begin_exp_instructions)

    # Create the study list
    # Cross the two sources and the 24 blocks
    study_trials = expand.expand_grid({'source': ['m', 'f'],
                                       'block': list(range(1, (n_items / 4) + 1)),
                                       })
    study_trials.block = study_trials.block.astype(np.int32)
    # Replicate twice, to make 4 trials per block
    study_trials = expand.replicate(study_trials, 2, ignore_index=True)
    # Randomize the order of male/female sources in each block
    study_trials = study_trials.groupby('block').apply(lambda z: z.sample(frac=1)).reset_index(drop=True)
    # Add the words to study, chosen image file, and empty response variables to the conditions
    study_trials = pd.concat([study_trials,
                              pd.DataFrame({'word': target_pool[:len(study_trials)],
                                            'file': [faces_table.loc[1, y] for y in study_trials.source],
                                            }),
                              pd.DataFrame(np.full(shape=(len(study_trials), 5), fill_value=np.nan),
                                           columns=['response', 'RT', 'correct', 'points', 'test_order'])],
                             axis=1)
    # Put everything in a nice order
    study_trials = study_trials[['block', 'word', 'source', 'file', 'response', 'RT', 'correct', 'points', 'test_order']]
    study_trials.set_index(['block', list(range(len(study_trials)))],
                           drop=False, inplace=True)

    # Study Practice Trials Loop
    total_points = 0
    for b in study_trials.index.unique(0):
        block = study_trials.loc[[b]]
        # Show stimuli
        for x in block.itertuples():
            # Study
            trials.draw_study_trial(x, study_word, face_stim)
            win.flip()
            core.wait(2)

            # Blank screen ISI
            win.flip()
            core.wait(.5)

        block = block.sample(frac=1)
        block['test_order'] = list(range(1, len(block) + 1))
        for x in block.itertuples():
            # Practice Test
            trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
            win.flip()

            # Waiting for key response
            response, rt, correct, points = trials.source_test_response(x)
            block.loc[x.Index, ['response', 'RT', 'correct', 'points']] = [response, rt, correct, points]
            total_points += points

            # Give the accuracy/point feedback
            source_points_feedback.text = str(points)
            trials.draw_source_feedback(x, source_points_feedback, study_word, face_stim)
            win.flip()
            core.wait(2)

            # ISI
            win.flip()
            core.wait(.5)

        study_trials.update(block)

    total_points_feedback.text = 'You earned %i points during the study list!\n\nPress the space bar to begin the word memory test.' % total_points
    total_points_feedback.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Creating Recognition trials schema
    # We need to drop the first and last block, so we select items from the second and second-to-last blocks
    targets = study_trials.loc[range(2, study_trials.index.max()[0]), 'word']
    # Create data frame with rows of targets
    recog_trials = pd.concat([targets,
                              pd.Series(['studied'] * len(targets), name='type', index=targets.index)
                              ],
                             axis=1
                             )
    # Add rows of lures (unstudied)
    recog_trials = pd.concat([recog_trials,
                              pd.DataFrame({'word': lure_pool[:len(recog_trials)],
                                            'type': ['unstudied'] * len(recog_trials)},
                                           index=recog_trials.index)
                              ],
                             join_axes=[pd.Index(['word', 'type'])]
                             )

    # Assign items to bias conditions
    recog_trials = recog_trials.groupby('type', group_keys=False)
    recog_trials = recog_trials.apply(lambda z:
                                      z.assign(safe=np.random.permutation(bias * (len(z) / len(bias))))
                                      )
    # Begin the test with the second block of 4 words, but randomly order trials after that
    recog_trials = pd.concat([recog_trials.loc[[2]].reset_index(level=1, drop=True),
                              recog_trials.loc[3:].sample(frac=1).reset_index(level=1, drop=True)
                              ]
                             )
    # Add a trial number index
    recog_trials['trial'] = range(1, len(recog_trials)+1)
    recog_trials = recog_trials.set_index('trial', append=True)

    # Add empty columns for response variables
    recog_trials = recog_trials.reindex(columns=recog_trials.columns.tolist() +
                                        ['guess', 'guess_correct', 'guess_RT', 'guess_points',
                                         'recog', 'recog_correct', 'recog_RT', 'recog_points'
                                         ])

    for t in ['5', '4', '3', '2', '1']:
        total_points_feedback.text = t
        total_points_feedback.draw()
        win.flip()
        core.wait(1)

    for x in recog_trials.itertuples():

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
        win.flip()
        core.wait(2)

        if guess_points + recog_points == -6:
            big_loss.draw()
            win.flip()
            core.wait(2)

        t = core.getTime()
        win.flip()
        # Save trial data
        recog_trials.loc[x.Index, ['guess', 'guess_points', 'recog', 'recog_points']] = \
            [guess, guess_points, recog, recog_points]
        # Reset opacity for all 'buttons'
        for y in [studied_recog_rect, unstudied_recog_rect, studied_guess_rect, unstudied_guess_rect]:
            y.opacity = 1
        for y in [studied_recog, unstudied_recog, studied_guess, unstudied_guess]:
            y.contrast = 1

        core.wait(.5 - (core.getTime() - t))

    total_points_feedback.text = 'You earned %i points during the word memory test!\n\nPress the space bar to begin the face memory test.' % total_points
    total_points_feedback.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Source testing
    source_test = study_trials.copy()
    # Again, begin the test with the second block of 4 words, but randomly order trials after that
    source_test = pd.concat([source_test.loc[[2]].reset_index(level=1, drop=True),
                             source_test.loc[3:source_test.index.get_level_values('block').max()-1].sample(frac=1).reset_index(level=1, drop=True)
                             ])
    source_test[['response', 'RT', 'correct', 'points']] = np.nan

    # Add a trial number index
    source_test['trial'] = range(1, len(source_test)+1)
    source_test = source_test.set_index('trial', append=True)

    # Begin Source Test Countdown
    for t in ['5', '4', '3', '2', '1']:
        total_points_feedback.text = t
        total_points_feedback.draw()
        win.flip()
        core.wait(1)

    for x in source_test.itertuples():
        # Source test probe
        trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
        win.flip()

        # Waiting for key response
        response, rt, correct, points = trials.source_test_response(x)
        total_points += points
        source_test.loc[x.Index, ['response', 'RT', 'correct', 'points']] = [response, rt, correct, points]

        # Give the accuracy/point feedback
        source_points_feedback.text = str(points)
        trials.draw_source_test(x, study_word, source_question_text, source_response_opts)
        trials.draw_source_feedback(x, source_points_feedback, study_word)
        win.flip()
        core.wait(1)

        # Blank screen ISI
        win.flip()
        core.wait(.25)

    # Saving the data to CSV
    study_trials['subject'] = subject
    study_trials = study_trials[['subject'] + study_trials.columns.tolist()[:-1]]
    study_trials.to_csv(os.path.join('data', subject + '_study.csv'), index=False, index_label=False)

    recog_trials['subject'] = subject
    recog_trials = recog_trials[['subject'] + recog_trials.columns.tolist()[:-1]]
    recog_trials.to_csv(os.path.join('data', subject + '_recognition.csv'), index=False, index_label=False)

    source_test['subject'] = subject
    source_test = source_test[['subject'] + source_test.columns.tolist()[:-1]]
    source_test.to_csv(os.path.join('data', subject + '_source.csv'), index=False, index_label=False)

    # Close the window
    win.close()

    # Close PsychoPy
    core.quit()


if __name__ == "__main__":
    if not os.path.exists('data') and not os.path.isfile('data'):
        os.mkdir('data')

    min_trials = 16
    max_trials = 548

    parser = argparse.ArgumentParser()
    parser.add_argument("--subject",
                        help="Manually set the subject ID. Useful if you want to impose a numerical sequence of subject IDs as generated \
                              from an external source.  Value is treated as a string internally. If unset, a type 4 UUID is generated for the subject ID",
                        default=str(uuid.uuid4()))
    bias_options = ['studied', 'unstudied']
    parser.add_argument("--bias",
                        help="Choose within or between subjects manipulation of which response option is safe, or manually set \
                             the \"studied\" or \"unstudied\" response to be the safe one.",
                        default='between',
                        choices=['between', 'within'] + bias_options
                        )
    parser.add_argument("--n_items",
                        help="How many words should be studied. Minimum %i, maximum %i. Value must be a multiple of 4." % (min_trials, max_trials),
                        default=96, type=int,
                        )
    parser.add_argument("--words",
                        help="Path to plain text file containing word stimuli. Each word should be on its own line. \
                             Converted to an absolute path, if necessary",
                        default='words.txt'
                        )
    parser.add_argument("--fullscreen", help="If included, open a fullscreen PsychoPy window. Otherwise, open a 1280x768 window",
                        default=False, action="store_true")
    args = parser.parse_args()

    if args.bias == 'between':
        args.bias = random.sample(bias_options, 1)
    elif args.bias == 'within':
        args.bias = bias_options

    if args.n_items % 4 != 0:
        raise ValueError('n_items argument value must be a multiple of 4')

    if not (16 <= args.n_items <= 548):
        raise ValueError('n_items argument value must be between %i and %i' % (min_trials, max_trials))

    if not os.path.isabs(args.words):
        args.words = os.path.abspath(args.words)

    with open(args.words, 'r') as f:
        words = f.read().splitlines()

    run(words=words, subject=args.subject, bias=args.bias, n_items=args.n_items, fullscreen=args.fullscreen)

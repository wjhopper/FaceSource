from psychopy import core, visual, event
import config
import expand
import trials

# Create a window and mouse
config.win = visual.Window([1000, 800], monitor="testMonitor")
config.mouse = event.Mouse()

# Create studied/unstudied "button" components
studied = visual.TextStim(config.win, text="Studied", pos=(-.75, .75))
unstudied = visual.TextStim(config.win, text="Not Studied", pos=(.75, .75))
studied_rect = visual.Rect(config.win, units='pix', pos=[(a*b)/2 for a, b in zip(studied.pos, config.win.size)],
                           width=studied.boundingBox[0] + 20, height=studied.boundingBox[1] + 20,
                           )
unstudied_rect = visual.Rect(config.win, units='pix', pos=[(a*b)/2 for a, b in zip(unstudied.pos, config.win.size)],
                             width=unstudied.boundingBox[0] + 20, height=unstudied.boundingBox[1] + 20,
                             )

# Text objects for displaying points earned feedback
guess_points_text = visual.TextStim(config.win, pos=(0, .75))
recog_points_text = visual.TextStim(config.win, pos=(0, -.75))
total_points_feedback = visual.TextStim(config.win, pos=(0, 0))

bias_trials = expand.expand_grid({'safe': ['studied', 'unstudied'],
                                  'correct': ['studied', 'unstudied']
                                  })
bias_trials = expand.replicate(bias_trials, 2)

# First round of guessing practice - use risky choice
total_points = 0
bias_trials = bias_trials.sample(frac=1).reset_index(drop=True)
for x in bias_trials.itertuples():
    # Display guess probe
    resp, trial_points = trials.guess(x, studied, studied_rect, unstudied, unstudied_rect)
    print trial_points

    # Display points feedback
    total_points += trial_points
    trials.points_feedback(guess_points_text, trial_points)
    core.wait(1.5)

    # ISI
    config.win.flip()
    core.wait(.5)

total_points_feedback.text = 'You earned %i points.\n\nPress the space bar to continue.' % total_points
total_points_feedback.draw()
config.win.flip()
event.waitKeys(keyList=['space'])

# Second round of guessing practice - use safe choice
total_points = 0 # reset total points
bias_trials = bias_trials.sample(frac=1).reset_index(drop=True)
for x in bias_trials.itertuples():
    # Display guess probe
    resp, trial_points = trials.guess(x, studied, studied_rect, unstudied, unstudied_rect)
    print trial_points

    # Display points feedback
    total_points += trial_points
    trials.points_feedback(guess_points_text, trial_points)
    core.wait(1.5)

    # ISI
    config.win.flip()
    core.wait(.5)

total_points_feedback.text = 'You earned %i points.\n\nPress the space bar to continue.' % total_points
total_points_feedback.draw()
config.win.flip()
event.waitKeys(keyList=['space'])

# Close the window
config.win.close()

# Close PsychoPy
core.quit()
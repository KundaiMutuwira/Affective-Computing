from psychopy import visual, core, event, gui
from datetime import datetime
import random
import csv
import os

# ----------------- Participant info dialog -------------------------#
participant_info = {"Participant Name": ""}

dlg = gui.DlgFromDict(participant_info, title="Participant Information")

if not dlg.OK:
    core.quit()

participant_name = participant_info["Participant Name"]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# folder where THIS script is located
save_folder = r"C:/Users/Dell/Documents/Masters/2B/Affective/results"

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

filename = os.path.join(
    save_folder,
    f"stroop_{participant_name}_{timestamp}.csv")

# ------------------------- Window setup -------------------------#
win = visual.Window(size=(1800, 1000), color="black", units='norm', fullscr=False)
text_stim = visual.TextStim( win, text="", height=0.15, color="black", wrapWidth=1.8, alignHoriz='center', alignVert='center')
feedback_stim = visual.TextStim(win, text="", height=0.25, color="white")
bg_rect = visual.Rect( win, width=1.2, height=0.45, fillColor="white", lineColor=None)
fixation = visual.TextStim(win,text="+",color="white",height=0.1)
timer_stim = visual.TextStim(win, text="", height=0.2, color="white", pos=(0.5, 0.8))

# ------------------------- Helper Functions -------------------------#
# Fixation display
def show_fixation(duration=0.5):
    fixation.draw()
    win.flip()
    core.wait(duration)

# Trial generation
def generate_trial():
    words = ["RED", "GREEN", "BLUE", "YELLOW", "ORANGE", "PURPLE", "WHITE","BROWN", "PINK", "GRAY"]
    colors_map = { "RED": "red","GREEN": "green", "BLUE": "blue", "YELLOW": "yellow", 
                   "ORANGE": "orange", "PURPLE": "purple", "WHITE": "white", "BROWN": "brown", 
                   "PINK": "pink", "GRAY": "gray" }

    word = random.choice(words)
    is_match = random.choice([True, False])

    ink_word = word if is_match else random.choice([w for w in words if w != word])
    ink_color = colors_map[ink_word]

    return word, ink_color, is_match

# Message display
def show_message(msg):
    stim = visual.TextStim(win, text=msg, color="white", height=0.08, wrapWidth=1.6)
    while True:
        stim.draw()
        win.flip()
        keys = event.getKeys()
        if "space" in keys:
            return
        if "escape" in keys:
            win.close()
            core.quit()

# Break display
def show_break_timer(duration=60):
    timer = core.CountdownTimer(duration)
    msg = visual.TextStim(win, text="Baseline complete.\n\nTake a break before the stress block.\nPress SPACE to end break.",
                          color="white", height=0.1, pos=(0, 0.2))
    countdown = visual.TextStim(win, text="", color="cyan", height=0.15, pos=(0, -0.2))

    while timer.getTime() > 0:
        remaining = int(timer.getTime())
        countdown.text = f"{remaining:}s" 
        msg.draw()
        countdown.draw()
        win.flip()
        keys = event.getKeys()
        if "space" in keys:
            return
        if 'escape' in event.getKeys():
            win.close()
            core.quit()

# ------------------ Practice block ------------------------
def run_practice(n=5):
    data = []

    for i in range(n):
        event.clearEvents()
        show_fixation(0.5)
        word, color, is_match = generate_trial()

        # Timestamp for HR correlation
        trial_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        responded = False
        clock = core.Clock()

        while not responded:
            bg_rect.fillColor = color
            bg_rect.draw()

            text_stim.text = word
            text_stim.color = "black"
            text_stim.draw()

            win.flip()

            keys = event.getKeys(keyList=["left", "right", "escape"], timeStamped=clock)

            if keys:
                key, rt = keys[0]
                if key == "escape":
                    win.close()
                    core.quit()

                correct = (key == "right" and is_match) or (key == "left" and not is_match)
                responded = True

        feedback_stim.text = "✓" if correct else "✗"
        feedback_stim.draw()
        win.flip()
        core.wait(0.5)

        data.append({ "block": "practice", "trial": i+1,"trail_timestamp": trial_ts,
            "word": word, "color": color, "is_match": is_match, "key": key, "rt": rt,
            "correct": correct
        })

    return data


# =========================
# BASELINE (UNSTRESSED COGNITIVE LOAD)
# =========================
def run_baseline(n=50):
    data = []

    for i in range(n):
        event.clearEvents()
        show_fixation(0.5)
        word, color, is_match = generate_trial()

        # Timestamp for HR correlation
        trial_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        responded = False
        clock = core.Clock()

        while not responded:
            bg_rect.fillColor = color
            bg_rect.draw()

            text_stim.text = word
            text_stim.color = "black"
            text_stim.draw()

            win.flip()

            keys = event.getKeys(keyList=["left", "right", "escape"], timeStamped=clock)

            if keys:
                key, rt = keys[0]
                if key == "escape":
                    win.close()
                    core.quit()

                correct = (key == "right" and is_match) or (key == "left" and not is_match)
                responded = True

        data.append({
            "block": "baseline",
            "trial": i+1,
            "trail_timestamp": trial_ts,
            "word": word,
            "color": color,
            "is_match": is_match,
            "key": key,
            "rt": rt,
            "correct": correct
        })

        core.wait(0.3)

    return data


# =========================
# ADAPTIVE STRESS
# =========================
def run_adaptive_stress(n=150, start_time_limit=4):
    data = []
    time_limit = start_time_limit
    consecutive = 0

    for i in range(n):
        event.clearEvents()
        show_fixation(random.uniform(0.4, 0.8))
        word, color, is_match = generate_trial()

        # Timestamp for HR correlation
        trial_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        responded = False
        timed_out = False
        clock = core.Clock()

        while not responded:
            bg_rect.fillColor = color
            bg_rect.draw()

            text_stim.text = word
            text_stim.color = "black"
            text_stim.draw()

            # adaptive timer display
            remaining = max(0, time_limit - clock.getTime())
            timer_stim.text = f"{remaining:.1f}s"
            if remaining <= 0.25:
                timer_stim.color = "red"
            else:
                timer_stim.color = "green"
            timer_stim.draw()   

            win.flip()

            keys = event.getKeys(keyList=["left", "right", "escape"], timeStamped=clock)

            if keys:
                key, rt = keys[0]
                if key == "escape":
                    win.close()
                    core.quit()

                correct = (key == "right" and is_match) or (key == "left" and not is_match)
                responded = True

            elif clock.getTime() >= time_limit:
                key = "timeout"
                rt = time_limit
                correct = False
                timed_out = True
                responded = True

        # adaptive difficulty
        if correct and not timed_out:
            consecutive += 1
            if consecutive >= 5:
                time_limit = max(0.5, time_limit - 0.25)
                consecutive = 0
        else:
            consecutive = 0

        feedback_stim.text = "✓" if correct else "✗"
        feedback_stim.color = "white"
        feedback_stim.draw()
        win.flip()
        core.wait(0.5)

        data.append({
            "block": "stress",
            "trial": i+1,
            "trail_timestamp": trial_ts,
            "word": word,
            "color": color,
            "is_match": is_match,
            "key": key,
            "rt": rt,
            "correct": correct,
            "time_limit": time_limit,
            "timed_out": timed_out
        })

        core.wait(0.2)

    return data


# Save data to CSV
def save_data(all_data, filename):
    if not all_data:
        print("No data to save.")
        return
    
    fieldnames = ["block","trial", "trail_timestamp", "rt","correct","time_limit","timed_out"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for row in all_data:

            # ensure all fields exist
            for field in fieldnames:
                if field not in row:
                    row[field] = ""

            writer.writerow(row)

        print(f"Data successfully saved to: {filename}")

    print("Saved:", filename)


# =========================
# MAIN EXPERIMENT
# =========================
try:
    show_message(
        "Welcome to our Stroop Game\n\n"
        "If color matches the word press Right Arrow \n If color does NOT match the word press Left Arrow\n\n"
        "Press SPACE to start"
    )

    show_message("Practice starting\nPress SPACE")
    practice = run_practice(5)

    show_message("Baseline starting\nPress SPACE")
    baseline = run_baseline(50)

    show_break_timer(duration=60)

    show_message("Stress block starting\nPress SPACE")
    stress = run_adaptive_stress(150)

    show_message("Done. Press SPACE to save & exit")

    #(practice + baseline + stress)
    # saving data
    all_data = []

    all_data.extend(practice)
    save_data(all_data, filename)

    all_data.extend(baseline)
    save_data(all_data, filename)

    all_data.extend(stress)
    save_data(all_data, filename)

except Exception as e:
    print("Error:", e)

finally:
    win.close()
    core.quit()
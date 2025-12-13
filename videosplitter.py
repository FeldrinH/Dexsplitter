import colorsys
from dataclasses import dataclass
import hashlib
import itertools
from pathlib import Path
import sys
import time
import numpy as np
import cv2


@dataclass(frozen=True)
class Timecode:
    hours: int
    minutes: int
    seconds: int
    milliseconds: int

    def __str__(self):
        return f"{self.hours:01d}:{self.minutes:02d}:{self.seconds:02d}.{self.milliseconds:03d}"

    def total_milliseconds(self):
        return 3_600_000 * self.hours + 60_000 * self.minutes + 1000 * self.seconds + self.milliseconds

    def add_milliseconds(self, milliseconds: int):
        total_milliseconds = self.total_milliseconds() + milliseconds
        return Timecode(total_milliseconds // 3_600_000, (total_milliseconds % 3_600_000) // 60_000, (total_milliseconds % 60_000) // 1000, total_milliseconds % 1000)

def locate_timecode_bounds(frame: np.ndarray):
    """Determine areas where timecodes are located in the frame"""

    height, width, _ = frame.shape
    timecode_area_top, timecode_area_bottom = 0, round(0.4 * height)
    timecode_area_left, timecode_area_right = round(0.25 * width), round(0.75 * width)
    timecode_area = frame[timecode_area_top:timecode_area_bottom, timecode_area_left:timecode_area_right]

    cv2.imwrite('timecode_area.png', timecode_area)

    FOREGROUND_THRESHOLD = 26

    horizontal_averages = np.mean(timecode_area, axis=(0, 2))
    horizontal_transitions = [v + timecode_area_left for v in transitions(horizontal_averages >= FOREGROUND_THRESHOLD)]
    
    vertical_averages = np.mean(timecode_area, axis=(1, 2))
    vertical_transitions = [v + timecode_area_top for v in transitions(vertical_averages >= FOREGROUND_THRESHOLD)]
    
    timecode_bounds_upper = (
        slice(vertical_transitions[0] - 4, vertical_transitions[1] + 4),
        slice(horizontal_transitions[0] - 4, horizontal_transitions[-1] + 4)
    )
    timecode_bounds_lower = (
        slice(vertical_transitions[2] - 4, vertical_transitions[3] + 4),
        slice(horizontal_transitions[0] - 4, horizontal_transitions[-1] + 4)
    )

    return timecode_bounds_upper, timecode_bounds_lower

def extract_timecode(timecode: np.ndarray):
    """Extract timecode from frame cropped to timecode bounds"""

    cv2.imwrite('timecode.png', timecode)
    
    # Merge color channels and apply thresholding to simplify processing
    timecode = np.mean(timecode, axis=2)
    base_threshold = np.mean(timecode)

    for threshold in np.arange(base_threshold, base_threshold + 40):
        timecode_thresholded = timecode >= threshold

        # Try to remove borders if they exist
        # TODO: The border detection really needs a redesign. This logic is broken, it just hasn't failed catastrophically yet.
        for i in range(1, 6):
            if np.count_nonzero(timecode_thresholded[i, :]) < 5:
                timecode_thresholded[:i, :] = 0
            if np.count_nonzero(timecode_thresholded[-i, :]) < 5:
                timecode_thresholded[-i:, :] = 0
            if np.count_nonzero(timecode_thresholded[:, i]) < 5:
                timecode_thresholded[:, :i] = 0
            if np.count_nonzero(timecode_thresholded[:, -i]) < 5:
                timecode_thresholded[:, -i:] = 0
        
        cv2.imwrite(f'timecode_thresholded.png', 255 * timecode_thresholded)

        vertical_transitions = transitions(np.max(timecode_thresholded, axis=1))
        if len(vertical_transitions) < 2:
            # Wrong number of transitions, try again (should have one row of digits, 2 transitions)
            continue
        
        timecode_thresholded = timecode_thresholded[vertical_transitions[0]:vertical_transitions[1], :]
        
        horizontal_transitions = transitions(np.max(timecode_thresholded, axis=0))
        for i in reversed(range(0, len(horizontal_transitions), 2)):
            if horizontal_transitions[i + 1] - horizontal_transitions[i] <= 2:
                # Delete segments that are too short to be a digit or colon
                del horizontal_transitions[i + 1], horizontal_transitions[i]
        if len(horizontal_transitions) != 22:
            # Wrong number of transitions, try again (should have 8 digits + 3 colons, 2 transitions each)
            continue
        
        # Remove transitions corresponding to colons
        del horizontal_transitions[14:16], horizontal_transitions[8:10], horizontal_transitions[2:4]
        
        digits: list[int] = []
        for i in range(0, len(horizontal_transitions), 2):
            digit = timecode[vertical_transitions[0]:vertical_transitions[1], horizontal_transitions[i]:horizontal_transitions[i + 1]]
            digit = extract_digit_nn(digit)
            digits.append(digit)
        
        return Timecode(digits[0], 10 * digits[1] + digits[2], 10 * digits[3] + digits[4], 100 * digits[5] + 10 * digits[6] + digits[7])
    
    raise AssertionError("Failed to segment digits")

REFERENCE_DIGITS = np.split(cv2.imread('reference_digits.png', cv2.IMREAD_GRAYSCALE).astype(np.bool), 10)

def extract_digit_nn(digit: np.ndarray):
    """Extract digit from image using nearest neighbor"""

    digit = normalize(digit)
    digit = np.clip(2 * digit - 0.5, 0.0, 1.0) # Increase contrast for easier recognition

    best_difference = 400
    best_value = None

    for xl, xr, yl, yr in itertools.product(range(2), repeat=4):        
        digit_cropped = digit[xl:digit.shape[0] - xr, yl:digit.shape[1] - yr]
        digit_cropped = cv2.resize(digit_cropped, (25, 34), interpolation=cv2.INTER_NEAREST)
        
        for value, reference_digit in enumerate(REFERENCE_DIGITS):
            difference = np.sum(np.abs(digit_cropped - reference_digit))
            if difference < best_difference:
                best_difference = difference
                best_value = value
        
        if best_difference < 100:
            # Early exit if we already have a good match
            break
    
    if best_value is None:
        raise AssertionError("Failed to identify digit")
    
    # digest = hashlib.sha256((255 * digit).astype(np.uint8).tobytes()).hexdigest()
    # Path(f'digits_dump/{best_value}').mkdir(parents=True, exist_ok=True)
    # cv2.imwrite(f'digits_dump/{best_value}/{digest[:8]}.png', 255 * digit)
    
    return best_value

def transitions(values: np.ndarray):
    transitions = [i for i in range(1, len(values)) if values[i - 1] != values[i]]
    if values[0]:
        transitions.insert(0, 0)
    if values[-1]:
        transitions.append(len(values))
    return transitions

def normalize(image: np.ndarray):
    image = image.astype(np.float32)
    min, max = image.min(), image.max()
    return (image - min) / (max - min)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        video_path = sys.argv[1]
    else:
        print("ERROR: Expected 1 argument")
        print()
        print(f"Usage: python {sys.argv[0]} <video path>")
        sys.exit(1)

    start_time = time.perf_counter()
    
    video_capture = cv2.VideoCapture(video_path)
    
    timecode_bounds_upper, timecode_bounds_lower = None, None
    
    level = 0
    timecode_start = Timecode(0, 0, 0, 0)
    in_transition = True
    in_final_level = False

    results = []

    while True:
        success, frame = video_capture.read()
        if not success:
            break

        # NB: OpenCV uses BGR color space for some reason, so we need to reorder the channels to get correct hue.
        average_blue, average_green, average_red = np.mean(frame[-150:, :900], axis=(0, 1)) / 255.0 # type: ignore
        average_hue, average_saturation, average_value = colorsys.rgb_to_hsv(average_red, average_green, average_blue)

        timecode_seconds = video_capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
        
        new_in_transition = average_saturation < 0.1 and average_value < 0.2
        new_in_credits = 0.55 < average_hue < 0.75 and average_saturation > 0.8 and average_value < 0.1
        new_in_final_level = (average_hue < 0.2 or average_hue > 0.95) and average_saturation > 0.5 and average_value > 0.1

        # print(f"{timecode_seconds:.3f}   {average_hue:.5f} {average_saturation:.5f} {average_value:.5f}   {new_in_transition} {new_in_credits} {new_in_final_level}")
        
        if (new_in_transition and not in_transition) or (new_in_final_level and not in_final_level) or new_in_credits:
            # End of current level, three possible cases:
            # - Start of level transition screen
            # - Start of final level (no level transition screen)
            # - Start of credits

            cv2.imwrite('frame_cropped.png', frame[-150:, :900])

            if timecode_bounds_upper is None or timecode_bounds_lower is None:
                cv2.imwrite('timecode_bounds_frame.png', frame)
                timecode_bounds_upper, timecode_bounds_lower = locate_timecode_bounds(frame)
            
            if new_in_final_level and not in_final_level:
                timecode_area_end = 255 - frame[timecode_bounds_upper]
            elif new_in_credits:
                timecode_area_end = frame[timecode_bounds_upper]
            else:
                timecode_area_end = frame[timecode_bounds_lower]
            timecode_end = extract_timecode(timecode_area_end)
            
            result = (level, timecode_start, timecode_end, (timecode_end.total_milliseconds() - timecode_start.total_milliseconds()) / 1000)
            results.append(result)
            print(*result)

            if timecode_end.total_milliseconds() <= timecode_start.total_milliseconds():
                raise AssertionError("Out of order timecodes")
        
        if ((not new_in_transition and in_transition) or (new_in_final_level and not in_final_level)) and (timecode_bounds_upper and timecode_bounds_lower):
            # Start of new level, two possible cases:
            # - End of level stransition screen
            # - Start of final level (no level transition screen)
            #
            # Note: If timecode bounds are unknown then we are in the first level.
            # We skip it because timecode bounds are unknown and the timecode is always 0:00:00:000 anyways.

            cv2.imwrite('frame_cropped.png', frame[-150:, :900])

            timecode_area_start = 255 - frame[timecode_bounds_upper]
            timecode_start = extract_timecode(timecode_area_start)
            
            level += 1
        
        if new_in_credits:
            # End of game
            assert in_final_level
            break
        
        in_transition = new_in_transition
        if new_in_final_level:
            in_final_level = True
    
    end_time = time.perf_counter()
    
    out_path = Path(video_path).with_suffix('.tsv')
    with open(out_path, mode='w') as f:
        f.write("Level\tStart\tEnd\tTime\n")
        for level, start, end, level_time in results:
            f.write(f"{level}\t{start}\t{end}\t{level_time}\n")
    
    print()
    print(f"Results written to {out_path}")
    print()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

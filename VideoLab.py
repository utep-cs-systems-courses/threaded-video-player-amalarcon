#!/usr/bin/env python3

'''
@author: Aaron Alarcon
'''

import threading
import cv2


FILE_NAME = 'clip.mp4'
tacos = "tacos"

class ThreadQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.full = threading.Semaphore(0)
        self.empty = threading.Semaphore(24)


    def put(self, item):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.full.release()


    def get(self):
        self.full.acquire()
        self.lock.acquire()
        item = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return item

#same, insert everything into the frame_queue
def extract_frames(filename, frame_queue):
    # Initialize frame count
    count = 0

    # Open video file
    vid_cap = cv2.VideoCapture(filename)

    # Read first image
    success, image = vid_cap.read()

    print(f'Reading frame {count} {success}')
    while success:
        # Add the frame to the buffer
        frame_queue.put(image)

        success, image = vid_cap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    print('Frame extraction complete')
    frame_queue.put(tacos)


#same as before. get frames from color and after converting, put in grays
def convert_grayscale(color_frames, gray_frames):
    # Initialize frame count
    count = 0

    # First color frame
    color_frame = color_frames.get()

    # Iterate through frames
    while color_frame is not tacos:
        print(f'Converting frame {count}')

        # Convert the image to grayscale_
        gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)

        # Enqueue gray_frame into gray_frames
        gray_frames.put(gray_frame)

        count += 1

        # Dequeue next color frame
        color_frame = color_frames.get()

    print('Conversion to grayscale  complete')
    gray_frames.put(tacos)


#same as the display_frames code except you get the frame from the gray_frames
def display_frames(g_frames):
    # Initialize frame count
    count = 0

    # Get the next frame
    frame = g_frames.get()

    # Go through each frame in the buffer until the buffer is empty
    while frame is not tacos:
        print(f'Displaying frame {count}')

        # Display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        count += 1

        # Get the next frame
        frame = g_frames.get()

    print('Finished displaying all frames')
    # Cleanup the windows
    cv2.destroyAllWindows()


def main():
    '''
    Start of code
    '''
    #Two queues for each frame
    color_frames = ThreadQueue()
    gray_frames = ThreadQueue()

    # Setting up threads
    extract = threading.Thread(target = extract_frames, args = (FILE_NAME, color_frames))
    convert = threading.Thread(target = convert_grayscale, args = (color_frames, gray_frames))
    display = threading.Thread(target = display_frames, args = (gray_frames))

    #Starting Each Thread
    extract.start()
    convert.start()
    display.start()


if __name__ == "__main__":
    main()

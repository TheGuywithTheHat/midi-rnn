import numpy as np
import os
import pretty_midi


class MidiDataGenerator:
    def __init__(self, path="clean_midi", max_len=100):
        self.files = self.enumerate_files()
        self.reset()
        self.max_len = max_len

    def enumerate_files(self):
        data_path = "clean_midi"
        return [data_path + "/" + d + "/" + p for d in os.listdir(data_path) for p in os.listdir(data_path + "/" + d)]

    def reset(self):
        self.index = 0
        self.shuffled = self.files
        np.random.shuffle(self.shuffled)

    def load_next(self):
        while True:
            try:
                if self.index >= len(self.shuffled):
                    self.reset()

                song = pretty_midi.PrettyMIDI(self.shuffled[self.index])
                
                if len(song.instruments) == 1:
                    return song
            except Exception as e:
                print("error on " + self.shuffled[self.index] + " " + str(e))
            finally:
                self.index += 1

    def preprocess_song(self, song):
        notes = song.instruments[0].notes
        print("len:{}".format(len(notes)))
        # 21/A0 to 116/G#8, 8 octaves and 12 notes per octave

        
        output_octaves = np.zeros((self.max_len, 8))
        output_notes = np.zeros((self.max_len, 12))
        output_velocities = np.zeros((self.max_len, 1))
        output_durations = np.zeros((self.max_len, 1))
        output_rests = np.zeros((self.max_len, 1))
        
        end = 0
        
        for i, n in enumerate(notes[:self.max_len]):
            output_octaves[i, (n.pitch - 21) // 12] = 1
            output_notes[i, (n.pitch - 21) % 12] = 1
            output_velocities[i, 0] = n.velocity
            output_durations[i, 0] = n.end - n.start
            if i > 0:
                output_rests[i - 1, 0] = n.start - end
            end = n.end
        return output_octaves, output_notes, output_velocities, output_durations, output_rests

    def flow(self, batch_size=100):
        while True:
            output_octaves = np.zeros((batch_size, self.max_len, 8))
            output_notes = np.zeros((batch_size, self.max_len, 12))
            output_velocities = np.zeros((batch_size, self.max_len, 1))
            output_durations = np.zeros((batch_size, self.max_len, 1))
            output_rests = np.zeros((batch_size, self.max_len, 1))
            for i in range(batch_size):
                output_octaves[i], output_notes[i], output_velocities[i], output_durations[i], output_rests[i] = self.preprocess_song(self.load_next())
            yield output_octaves, output_notes, output_velocities, output_durations, output_rests

if __name__ == "__main__":
    mdg = MidiDataGenerator()
    i = 0
    while True:
    #for i in range(10):
        print(i)
        s = mdg.load_next()
        i += 1
from glob import glob
import os
import librosa
from scipy import signal
import random
import numpy as np
from scipy.io import wavfile
import soundfile as sf


random.seed(42)


class ReverbGenerator(object):
    def __init__(self, sr=16000, musan=False):
        # Image source simulation
        ps_path = "/data2/home/vincent0730/dereverb/dataset/RIRS_NOISES/real_rirs_isotropic_noises/*.wav"
        self.ps_files = glob(ps_path)

        # RIR simulation
        rir_path        = "/data2/home/vincent0730/dereverb/dataset/RIRS_NOISES/simulated_rirs/*/*/*.wav"
        self.rir_files  = glob(rir_path)
        
        speech_path = "/data2/home/vincent0730/dereverb/dataset/musan/speech/*/*.wav"
        self.speech_files = glob(speech_path)
        
        music_path = "/data2/home/vincent0730/dereverb/dataset/musan/music/*/*.wav"
        self.music_files = glob(music_path)

        self.sr = sr

    def reverberation(self, audio, files_list, breaker=1):
        rir_file  = random.choice(files_list)
        rir, fs  = librosa.load(rir_file, sr=self.sr)

        rir      = np.expand_dims(rir.astype(np.float64),0)
        rir      = rir / np.sqrt(np.sum(rir**2))
        rir      = rir * breaker
        audio    = np.expand_dims(audio.astype(np.float64),0)


        rev_audio = signal.convolve(audio, rir, mode='full')[:,:audio.shape[1]]
        # rev_audio = signal.convolve(audio, rir, mode='full')
        rev_audio = np.squeeze(rev_audio)
        return rev_audio

    def add_noise(self, audio, file_list, snr_list, num):
        clean_db = 10 * np.log10(np.mean(audio ** 2)+1e-4)
        noise_file  =  random.sample(file_list, random.randint(num[0], num[1]))
        noises = []
        
        for n in noise_file:
            noise, fs = librosa.load(n, sr=self.sr)
            
            audiolen = audio.shape[0]
            noiselen = noise.shape[0]
            if noiselen < audiolen:
                shortage  = audiolen - noiselen + 1
                noise     = np.pad(noise, (0, shortage), 'wrap')
                noiselen  = noise.shape[0]
            elif noiselen > audiolen:
                sf = np.int64(random.random()*(noiselen-audiolen))
                noise = noise[int(sf):int(sf)+audiolen]
                noiselen  = noise.shape[0]

            
            noise_snr = random.uniform(snr_list[0],snr_list[1])
            noise_db = 10 * np.log10(np.mean(noise[0] ** 2)+1e-4)
            noises.append(np.sqrt(10 ** ((clean_db - noise_db - noise_snr) / 10)) * noise)
        
        new_audio = np.sum(np.array(noises), axis=0, keepdims=True)[0] + audio

        return new_audio

    def simulate(self, audio, musan=False, selection=None):
        if not selection:
            
            # 1: image source, 2: rir, 3: speech, 4: music
            if musan:
                selection = random.randint(1, 4)
            else:
                selection = random.randint(1, 2)

        if selection == 1:
            rev_audio = self.reverberation(audio, self.ps_files)
        elif selection == 2:
            rev_audio = self.reverberation(audio, self.rir_files)
        elif selection == 3:
            rev_audio = self.add_noise(audio, self.speech_files, [21, 26], [2, 5]) 
        elif selection == 4:
            rev_audio = self.add_noise(audio, self.music_files, [8, 18], [1, 1]) 
        else:
            print("selection not exists")

        return rev_audio


if __name__ == "__main__":
    audio, fs = librosa.load("example/sent_16_01458_1.wav", sr=16000)
    rg = ReverbGenerator(musan=True)
    rev_audio = rg.simulate(audio, musan=True, selection=3)
    print(audio)
    print(rev_audio)
    
    sf.write('example/rev.wav', rev_audio, fs)



from glob import glob
import os
import librosa
import soundfile as sf
from generator import ReverbGenerator
import argparse
import warnings
import random
from tqdm import tqdm
warnings.filterwarnings('ignore')


def get_args():
    '''
    input:
    dir/to/input_path/*.wav

    output:
    dir/to/output_path/train/ane/*.wav
    dir/to/output_path/train/rev/*.wav
    dir/to/output_path/dev/ane/*.wav
    dir/to/output_path/dev/rev/*.wav
    dir/to/output_path/test/ane/*.wav
    dir/to/output_path/test/rev/*.wav
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', default='/home/vincent0730/dereverb/dataset/aishell/train/wav')
    # parser.add_argument('--input_path', default='/media/DATA/dayiData/PonddyEngRecordings/Colin_16k')
    parser.add_argument('--output_path', default='/home/vincent0730/dereverb/dataset/zh-ponddy_dereverb/mix')
    parser.add_argument('--mode', default='split', choices=['train', 'dev', 'test', 'split'])
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--mklist', action='store_true')

    args = parser.parse_args()
    return args

def makedirs(args):
    os.makedirs(f"{args.output_path}/train/ane", exist_ok=True)
    os.makedirs(f"{args.output_path}/train/rev", exist_ok=True)
    os.makedirs(f"{args.output_path}/dev/ane"  , exist_ok=True)
    os.makedirs(f"{args.output_path}/dev/rev"  , exist_ok=True)
    os.makedirs(f"{args.output_path}/test/ane" , exist_ok=True)
    os.makedirs(f"{args.output_path}/test/rev" , exist_ok=True)

def writelist(audio_path, list_path):

    audio_list = glob(f"{audio_path}/*.wav")

    fp = open(list_path, 'w')
    for audio in audio_list:
        basename = '.'.join(os.path.basename(audio).split('.')[:-1])
        fp.write(f"{basename}\n")

def main(args):

    if args.generate:
        makedirs(args)
        rg = ReverbGenerator()
        audio_list = glob(f"{args.input_path}/*/*.wav")

        for audio in tqdm(audio_list):
            data, sr = librosa.load(audio, sr=16000)
            mode = args.mode
            if mode == 'split':
                dice = random.randint(0, 9)
                if dice == 9:
                    mode = 'test'
                elif dice == 7 or dice == 8:
                    mode = 'dev'
                else:
                    mode = 'train'

            basename = os.path.basename(audio)
            rev_data = rg.simulate(data)

            sf.write(f"{args.output_path}/{mode}/ane/{basename}", data, 16000)
            sf.write(f"{args.output_path}/{mode}/rev/{basename}", rev_data, 16000)

    if args.mklist:
        mode = args.mode
        if mode == 'split':
            writelist(f"{args.output_path}/train/ane/", f"{args.output_path}/train/train_list")
            writelist(f"{args.output_path}/dev/ane/", f"{args.output_path}/dev/dev_list")
        else:
            writelist(f"{args.output_path}/{mode}/ane/", f"{args.output_path}/{mode}/{mode}_list")


if __name__ == '__main__':
    args = get_args()
    main(args)

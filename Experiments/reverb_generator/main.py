import argparse
import os
import random
import warnings
from glob import glob

import librosa
import soundfile as sf
from tqdm.contrib.concurrent import thread_map

from generator import ReverbGenerator

warnings.filterwarnings("ignore")

def get_args():
    """
    input:
    dir/to/input_path/*.wav
    output:
    dir/to/output_path/train/ane/*.wav
    dir/to/output_path/train/rev/*.wav
    dir/to/output_path/dev/ane/*.wav
    dir/to/output_path/dev/rev/*.wav
    dir/to/output_path/test/ane/*.wav
    dir/to/output_path/test/rev/*.wav
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default="/data2/home/vincent0730/VC/wav/VCTK/wavs")
    # parser.add_argument('--input_path', default='/media/DATA/dayiData/PonddyEngRecordings/Colin_16k')
    parser.add_argument(
        "--output_path",
        default="/data2/home/vincent0730/dereverb/dataset/ponddy_dereverb/mix",
    )
    parser.add_argument(
        "--mode", default="split", choices=["train", "dev", "test", "split"]
    )
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--mklist", action="store_true")
    parser.add_argument("--musan", action="store_true")

    return parser.parse_args()

args = get_args()
rg = ReverbGenerator(sr=16000, musan=args.musan)

def makedirs(args):
    os.makedirs(f"{args.output_path}/train/ane", exist_ok=True)
    os.makedirs(f"{args.output_path}/train/rev", exist_ok=True)
    os.makedirs(f"{args.output_path}/dev/ane", exist_ok=True)
    os.makedirs(f"{args.output_path}/dev/rev", exist_ok=True)
    os.makedirs(f"{args.output_path}/test/ane", exist_ok=True)
    os.makedirs(f"{args.output_path}/test/rev", exist_ok=True)


def writelist(audio_path, list_path):

    audio_list = glob(f"{audio_path}/*.wav")

    fp = open(list_path, "w")
    for audio in audio_list:
        basename = ".".join(os.path.basename(audio).split(".")[:-1])
        fp.write(f"{basename}\n")


def do_something(audio):
    data, _ = librosa.load(audio, sr=16000)
    mode = args.mode
    if mode == "split":
        dice = random.randint(0, 9)
        if dice == 9:
            mode = "test"
        elif dice in [7, 8]:
            mode = "dev"
        else:
            mode = "train"

    basename = os.path.basename(audio)
    rev_data = rg.simulate(data, musan=args.musan)

    sf.write(f"{args.output_path}/{mode}/ane/{basename}", data, 16000)
    sf.write(f"{args.output_path}/{mode}/rev/{basename}", rev_data, 16000)


def main(args):

    if args.generate:
        makedirs(args)
        audio_list = glob(f"{args.input_path}/*.wav")
        thread_map(do_something, audio_list)

    if args.mklist:
        mode = args.mode
        if mode == "split":
            writelist(
                f"{args.output_path}/train/ane/", f"{args.output_path}/train/train_list"
            )
            writelist(
                f"{args.output_path}/dev/ane/", f"{args.output_path}/dev/dev_list"
            )
        else:
            writelist(
                f"{args.output_path}/{mode}/ane/",
                f"{args.output_path}/{mode}/{mode}_list",
            )


if __name__ == "__main__":
    args = get_args()
    main(args)

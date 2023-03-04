# -*- coding: utf-8 -*-
"""
Data preparation.

First "Manually" Download VoiceBank-SLR [1] from:
https://bio-asplab.citi.sinica.edu.tw/Opensource.html#VB-SLR

[1] “MetricGAN-U: Unsupervised speech enhancement/ dereverberation based only on noisy/ reverberated speech”

Authors:
 * Szu-Wei Fu, 2020
 * Peter Plantinga, 2020
"""

import os
import json
import string
import logging
from speechbrain.utils.data_utils import get_all_files
from speechbrain.dataio.dataio import read_audio

logger = logging.getLogger(__name__)
LEXICON_URL = "http://www.openslr.org/resources/11/librispeech-lexicon.txt"
TRAIN_JSON = "train_revb.json"
TEST_JSON = "test_revb.json"
VALID_JSON = "valid_revb.json"
SAMPLERATE = 16000

def prepare_voicebank(
    data_folder, save_folder, valid_speaker_count=2, skip_prep=False
):
    """
    Prepares the json files for the Voicebank dataset.

    Expects the data folder to be the same format as the output of
    ``download_vctk_slr()`` below.

    Arguments
    ---------
    data_folder : str
        Path to the folder where the original Voicebank dataset is stored.
    save_folder : str
        The directory where to store the json files.
    valid_speaker_count : int
        The number of validation speakers to use (out of 28 in train set).
    skip_prep: bool
        If True, skip data preparation.

    Example
    -------
    >>> data_folder = '/path/to/datasets/Voicebank'
    >>> save_folder = 'exp/Voicebank_exp'
    >>> prepare_voicebank(data_folder, save_folder)
    """

    if skip_prep:
        return

    # Setting ouput files
    save_json_train = os.path.join(save_folder, TRAIN_JSON)
    save_json_valid = os.path.join(save_folder, VALID_JSON)
    save_json_test = os.path.join(save_folder, TEST_JSON)

    # Check if this phase is already done (if so, skip it)
    if skip(save_json_train, save_json_test, save_json_valid):
        logger.info("Preparation completed in previous run, skipping.")
        return

    train_clean_folder = os.path.join(data_folder, "train/ane")
    train_noisy_folder = os.path.join(data_folder, "train/rev")

    dev_clean_folder = os.path.join(data_folder, "dev/ane")
    dev_noisy_folder = os.path.join(data_folder, "dev/rev")

    test_clean_folder = os.path.join(data_folder, "test/ane")
    test_noisy_folder = os.path.join(data_folder, "test/rev")

    # Setting the save folder
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        """
    # Additional checks to make sure the data folder contains Voicebank
    check_voicebank_folders(
        train_clean_folder,
        train_noisy_folder,
        train_txts,
        test_clean_folder,
        test_noisy_folder,
        test_txts,
    )
    """
    logger.debug("Creating lexicon...")
    logger.info("Creating json files for noisy VoiceBank...")

    logger.debug("Collecting files...")
    extension = [".wav"]
    
    # valid_speakers = TRAIN_SPEAKERS[:valid_speaker_count]
    wav_lst_train = get_all_files(train_noisy_folder, match_and=extension)
    wav_lst_valid = get_all_files(dev_noisy_folder, match_and=extension)
    wav_lst_test  = get_all_files(test_noisy_folder, match_and=extension)

    logger.debug("Creating json files for reverb VoiceBank...")
    create_json(wav_lst_train, save_json_train, train_clean_folder, 'train')
    create_json(wav_lst_valid, save_json_valid, dev_clean_folder, 'dev')
    create_json(wav_lst_test, save_json_test, test_clean_folder, 'test')


def skip(*filenames):
    """
    Detects if the Voicebank data_preparation has been already done.
    If the preparation has been done, we can skip it.

    Returns
    -------
    bool
        if True, the preparation phase can be skipped.
        if False, it must be done.
    """
    for filename in filenames:
        if not os.path.isfile(filename):
            return False
    return True


def remove_punctuation(a_string):
    """Remove all punctuation from string"""
    return a_string.translate(str.maketrans("", "", string.punctuation))


def create_json(wav_lst, json_file, clean_folder, label=''):
    """
    Creates the json file given a list of wav files.

    Arguments
    ---------
    wav_lst : list
        The list of wav files.
    json_file : str
        The path of the output json file
    clean_folder : str
        The location of parallel clean samples.
    """
    logger.debug(f"Creating json lists in {json_file}")

    # Processing all the wav files in the list
    json_dict = {}
    for wav_file in wav_lst:  # ex:p203_122.wav

        # Example wav_file: p232_001.wav
        noisy_path, filename = os.path.split(wav_file)
        _, noisy_dir = os.path.split(noisy_path)
        _, clean_dir = os.path.split(clean_folder)
        noisy_rel_path = os.path.join("{data_root}", label, noisy_dir, filename)
        clean_rel_path = os.path.join("{data_root}", label, clean_dir, filename)


        # Reading the signal (to retrieve duration in seconds)
        signal = read_audio(wav_file)
        duration = signal.shape[0] / SAMPLERATE

        # Read text
        snt_id = filename.replace(".wav", "")

        json_dict[snt_id] = {
            "noisy_wav": noisy_rel_path,
            "clean_wav": clean_rel_path,
            "length": duration,
        }

    # Writing the json lines
    with open(json_file, mode="w") as json_f:
        json.dump(json_dict, json_f, indent=2)

    logger.info(f"{json_file} successfully created!")


def check_voicebank_folders(*folders):
    """Raises FileNotFoundError if any passed folder does not exist."""
    for folder in folders:
        if not os.path.exists(folder):
            raise FileNotFoundError(
                f"the folder {folder} does not exist (it is expected in "
                "the Voicebank dataset)"
            )

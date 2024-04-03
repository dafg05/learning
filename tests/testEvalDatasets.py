import torch
from pathlib import Path

from evaluation.evalDatasets import ValidationHvoDataset, MonotonicHvoDataset, GeneratedHvoDataset
from evaluation.constants import SF_PATH
from training.grooveTransformer import GrooveTransformer

from hvo_sequence.hvo_seq import HVO_Sequence

# Validation set path
SOURCE_DIR = Path('tests', 'AfroCuban_Validation_PreProcessed_On_03_04_2024_at_01_04_hrs')

# Load model
MODEL_PATH = Path('tests', 'smol_solar-shadow_1711138656.pth')
MODEL = GrooveTransformer(d_model = 8, nhead = 4, num_layers=11, dim_feedforward=16, dropout=0.1594, voices=9, time_steps=32, hit_sigmoid_in_forward=False)
MODEL.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))

AUDIO_OUT_DIR = Path('tests','datasets_out')
SUBSET_SIZE = 4

def testEvalDatasets():
    validation_set = ValidationHvoDataset(SOURCE_DIR)
    
    # check if validation set is valid
    for i in range(len(validation_set)):
        validation_seq = validation_set[i]
        assert validation_seq.hvo.shape == (32, 27), f"Validation hvo shape is invalid: {validation_seq.hvo.shape}"
        filename = f"{AUDIO_OUT_DIR}/valid_{validation_seq.master_id}.wav"
        validation_seq.save_audio(filename=filename, sf_path=SF_PATH)
    print("validation set looking good")

    monotonic_set = MonotonicHvoDataset(validation_set)
    # check if monotonic set is valid
    assert len(monotonic_set) == len(validation_set)
    assert monotonic_set[0].master_id == validation_set[0].master_id
    assert monotonic_set[0].style_primary == validation_set[0].style_primary
    for i in range(SUBSET_SIZE):
        monotonic_seq = monotonic_set[i]
        assert monotonic_seq.hvo.shape == (32, 27), f"Monotonic hvo shape is invalid: {monotonic_seq.hvo.shape}"
        filename = f"{AUDIO_OUT_DIR}/monotonic_{monotonic_seq.master_id}.wav"
        monotonic_seq.save_audio(filename=filename, sf_path=SF_PATH)
    print("monotonic set looking good")

    generated_set = GeneratedHvoDataset(monotonic_set, MODEL)
    # check if generated set is valid
    assert len(generated_set) == len(monotonic_set)
    assert generated_set[0].master_id == monotonic_set[0].master_id
    assert generated_set[0].style_primary == monotonic_set[0].style_primary
    for i in range(SUBSET_SIZE):
        generated_seq = generated_set[i]
        assert generated_seq.hvo.shape == (32, 27), f"Generated hvo shape is invalid: {generated_seq.hvo.shape}"
        filename = f"{AUDIO_OUT_DIR}/generated_{generated_seq.master_id}.wav"
        generated_seq.save_audio(filename=filename, sf_path=SF_PATH)
    print("generated set looking good")

    print("All sets looking good")

if __name__ == "__main__":
    testEvalDatasets()
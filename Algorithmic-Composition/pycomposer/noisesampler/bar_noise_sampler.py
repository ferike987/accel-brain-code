# -*- coding: utf-8 -*-
import numpy as np
from pygan.noise_sampler import NoiseSampler


class BarNoiseSampler(NoiseSampler):
    '''
    Generate samples based on the noise prior by distribution of MIDI files.
    '''

    # Channel
    __channel = 1

    def __init__(
        self, 
        midi_df_list, 
        batch_size=20, 
        seq_len=10, 
        time_fraction=0.1,
        min_pitch=24,
        max_pitch=108
    ):
        '''
        Init.

        Args:
            midi_path_list:         `list` of paths to MIDI files.
            batch_size:             Batch size.
            seq_len:                The length of sequneces.
                                    The length corresponds to the number of `time` splited by `time_fraction`.

            time_fraction:          Time fraction which means the length of bars.

            min_pitch:              The minimum of note number.
            max_pitch:              The maximum of note number.
        '''
        program_list = []
        self.__midi_df_list = midi_df_list
        for i in range(len(self.__midi_df_list)):
            program_list.extend(
                self.__midi_df_list[i]["program"].drop_duplicates().values.tolist()
            )
        program_list = list(set(program_list))

        self.__batch_size = batch_size
        self.__seq_len = seq_len
        self.__channel = len(program_list)
        self.__program_list = program_list
        self.__time_fraction = time_fraction
        self.__min_pitch = min_pitch
        self.__max_pitch = max_pitch
        self.__dim = self.__max_pitch - self.__min_pitch

    def generate(self):
        '''
        Generate noise samples.
        
        Returns:
            `np.ndarray` of samples.
        '''
        sampled_arr = np.zeros((self.__batch_size, self.__channel, self.__seq_len, self.__dim))

        for batch in range(self.__batch_size):
            for i in range(len(self.__program_list)):
                program_key = self.__program_list[i]
                key = np.random.randint(low=0, high=len(self.__midi_df_list))
                midi_df = self.__midi_df_list[key]
                midi_df = midi_df[midi_df.program == program_key]
                if midi_df.shape[0] < self.__seq_len:
                    continue

                row = np.random.uniform(
                    low=midi_df.start.min(), 
                    high=midi_df.end.max() - (self.__seq_len * self.__time_fraction)
                )
                for seq in range(self.__seq_len):
                    df = midi_df[midi_df.start < row + (seq * self.__time_fraction)]
                    df = df[df.end > row + ((seq+1) * self.__time_fraction)]
                    sampled_arr[batch, i, seq] = self.__convert_into_feature(df)

        return sampled_arr

    def __convert_into_feature(self, df):
        arr = np.zeros(self.__dim)
        for i in range(df.shape[0]):
            if df.pitch.values[i] < self.__max_pitch - 1:
                arr[df.pitch.values[i] - self.__min_pitch] = 1

        return arr.reshape(1, -1).astype(float)

    def get_channel(self):
        ''' getter '''
        return self.__channel
    
    def set_readonly(self, value):
        ''' setter '''
        raise TypeError("This property must be read-only.")
    
    channel = property(get_channel, set_readonly)

    def get_program_list(self):
        ''' getter '''
        return self.__program_list
    
    program_list = property(get_program_list, set_readonly)

import os
import sys
import csv

import torch
from torchtext.data import Field, TabularDataset
from torchtext.data.iterator import BucketIterator
from torchtext.vocab import Vectors
from datasets.reuters import clean_string

csv.field_size_limit(sys.maxsize)


def process_labels(label_str, num_classes):
    label_num = int(label_str)  # label is one of "1", "2", "3", F"4"
    label = [0.0] * num_classes
    label[label_num] = 1.0
    return label

class OHSUMED(TabularDataset):
    NAME = 'OHSUMED'
    NUM_CLASSES = 23
    IS_MULTILABEL = False

    TEXT_FIELD = Field(batch_first=True, tokenize=clean_string, include_lengths=True)
    LABEL_FIELD = Field(sequential=False, use_vocab=False, batch_first=True, preprocessing=lambda s: process_labels(s, OHSUMED.NUM_CLASSES))

    @staticmethod
    def sort_key(ex):
        return len(ex.text)

    @classmethod
    def splits(cls, path, train=os.path.join('.local_data', 'OHSUMED', 'train.csv'),
               test=os.path.join('.local_data', 'OHSUMED', 'test.csv'), **kwargs):
        return super(OHSUMED, cls).splits(
            path, train=train, test=test, format='csv', fields=[('label', cls.LABEL_FIELD), ('text', cls.TEXT_FIELD)]
        )

    @classmethod
    def iters(cls, path, vectors_name, vectors_cache, batch_size=64, shuffle=True, device=0, vectors=None,
              unk_init=torch.Tensor.zero_):
        """
        :param path: directory containing train, test, dev files
        :param vectors_name: name of word vectors file
        :param vectors_cache: path to directory containing word vectors file
        :param batch_size: batch size
        :param device: GPU device
        :param vectors: custom vectors - either predefined torchtext vectors or your own custom Vector classes
        :param unk_init: function used to generate vector for OOV words
        :return:
        """
        if vectors is None:
            vectors = Vectors(name=vectors_name, cache=vectors_cache, unk_init=unk_init)

        train, test = cls.splits(path)
        cls.TEXT_FIELD.build_vocab(train, test, vectors=vectors)
        return BucketIterator.splits((train, test), batch_size=batch_size, repeat=False, shuffle=shuffle,
                                     sort_within_batch=True, device=device)
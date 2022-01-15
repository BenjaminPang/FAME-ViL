import copy
import json
import random

import torch
from mmf.common.sample import Sample
from mmf.common.typings import MMFDatasetConfigType
from mmf.datasets.mmf_dataset import MMFDataset
from .database import FashionGenDatabase


class FashionGenDataset(MMFDataset):
    def __init__(
        self,
        config: MMFDatasetConfigType,
        dataset_type: str,
        index: int,
        *args,
        **kwargs,
    ):
        super().__init__(
            "fashiongen",
            config,
            dataset_type,
            index,
            FashionGenDatabase,
            *args,
            **kwargs,
        )

    def init_processors(self):
        super().init_processors()
        if self._use_images:
            # Assign transforms to the image_db
            if self._dataset_type == "train":
                self.image_db.transform = self.train_image_processor
            else:
                self.image_db.transform = self.eval_image_processor

    def _get_valid_text_attribute(self, sample_info):
        if "captions" in sample_info:
            return "captions"

        if "sentences" in sample_info:
            return "sentences"

        raise AttributeError("No valid text attribution was found")


    def __getitem__(self, idx):
        sample_info = self.annotation_db[idx]
        text_attr = self._get_valid_text_attribute(sample_info)

        current_sample = Sample()
        sentence = sample_info[text_attr]
        current_sample.text = sentence

        if hasattr(self, "masked_token_processor") and self._dataset_type == "train":
            processed_sentence = self.masked_token_processor({"text": sentence})
            current_sample.update(processed_sentence)
        else:
            processed_sentence = self.text_processor({"text": sentence})
            current_sample.update(processed_sentence)

        image_path = sample_info["image_path"]
        if self._dataset_type == "train":
            image_path = random.choices(image_path)[0]
            current_sample.image = self.image_db.from_path(image_path)["images"][0]
        else:
            images = self.image_db.from_path(image_path)["images"]
            images = torch.stack(images)
            current_sample.image = images
            current_sample.text_id = torch.tensor(sample_info["id"], dtype=torch.long)
            current_sample.image_id = current_sample.text_id.repeat(len(image_path), 1)

        current_sample.ann_idx = torch.tensor(idx, dtype=torch.long)
        current_sample.targets = None

        return current_sample

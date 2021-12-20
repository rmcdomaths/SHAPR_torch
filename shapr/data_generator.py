import numpy as np

from ._settings import settings
from .utils import *
from .metrics import *
from torch.utils.data import Dataset

def augmentation(obj, img):
    random.seed(settings.random_seed)
    np.random.seed(settings.random_seed)
    if random.choice([True, True, False]) == True:
        obj = np.flip(obj, len(np.shape(obj)) - 1)
        img = np.flip(img, len(np.shape(img)) - 1)
    if random.choice([True, True, False]) == True:
        obj = np.flip(obj, len(np.shape(obj)) - 2)
        img = np.flip(img, len(np.shape(img)) - 2)

    if random.choice([True, True, False]) == True:
        angle = np.random.choice(int(360 * 100)) / 100
        img = np.nan_to_num(rotate(img, angle, resize=False, preserve_range=True))
        for i in range(0, np.shape(obj)[0]):
            obj[i, :, :] = np.nan_to_num(rotate(obj[i, :, :], angle, resize=False, preserve_range=True))

    if random.choice([True, True, False]) == True:
        from skimage.util import random_noise
        img = random_noise(img, mode='gaussian', var= 0.02)

    if random.choice([True, True, False]) == True:
        obj_shape = np.shape(obj)
        img_shape = np.shape(img)
        x_shift = np.random.choice(int(40))
        y_shift = np.random.choice(int(40))
        x_shift2 = np.random.choice(int(40))
        y_shift2 = np.random.choice(int(40))
        z_shift = np.random.choice(int(10))
        z_shift2 = np.random.choice(int(10))
        obj = obj[z_shift:-(z_shift2+1), x_shift:-(x_shift2+1), y_shift:-(y_shift2+1)]
        img = img[int(x_shift/4):-int(x_shift2/4+1), int(y_shift/4):-int(y_shift2/4+1),:]
        obj = resize(obj, obj_shape, preserve_range=True)
        img = resize(img, img_shape, preserve_range=True)

    return obj, img



"""
The data generator will open the 3D segmentation, 2D masks and 2D images for each fold from the directory given the filenames and return a tensor
The 2D mask and the 2D image will be multiplied pixel-wise to remove the background
"""

class SHAPRDataset(Dataset):
    def __init__(self, path, filenames, transform=None, target_transform=None):
        self.path = path
        self.filenames = filenames

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        #print("load file", self.filenames[idx])
        obj = import_image(os.path.join(self.path, "obj", self.filenames[idx])) / 255.
        img = import_image(os.path.join(self.path, "mask", self.filenames[idx])) / 255.
        bf = import_image(os.path.join(self.path, "image", self.filenames[idx])) / 255.
        mask_bf = np.zeros((2, 1, int(np.shape(img)[0]), int(np.shape(img)[1])))
        mask_bf[0, 0, :, :] = img
        mask_bf[1, 0, :, :] = bf * img
        obj = obj[np.newaxis,:,:,:]
        return {
            'image': torch.as_tensor(mask_bf.copy()).float().contiguous(),
            'obj': torch.as_tensor(obj.copy()).long().contiguous()
        }

def get_test_image(self, filename):
    img = import_image(os.path.join(self.path, "mask", filename)) / 255.
    bf = import_image(os.path.join(self.path, "image", filename)) / 255.
    mask_bf = np.zeros((2, 1, int(np.shape(img)[0]), int(np.shape(img)[1])))
    mask_bf[0, 0, :, :] = img
    mask_bf[1, 0, :, :] = bf * img
    mask_bf = mask_bf[np.newaxis,...]
    return mask_bf



"""
The test data generator will open the 2D masks and 2D images for each fold from the directory given the filenames and return a tensor
"""
def data_generator_test_set(path, filenames):
    while True:
        for test_file in filenames:
            if not test_file.startswith('.'):
                img = import_image(os.path.join(path, "mask", test_file)) / 255.
                bf = import_image(os.path.join(path, "image", test_file)) /255.
                img_out_2 = np.zeros((int(np.shape(img)[0]), int(np.shape(img)[1]), 2))
                img_out_2[:, :, 0] = img
                img_out_2[:, :, 1] = bf * img
                img_out_2 = img_out_2[np.newaxis, np.newaxis, ...]
                yield img_out_2
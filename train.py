import argparse

from keras.callbacks import ModelCheckpoint
import keras
from keras.optimizers import Adam

from data.load_data import trainGenerator
from nets import Hairnet

import os


def get_args():
    parser = argparse.ArgumentParser(description='Hair Segmentation')
    parser.add_argument('--data_dir', default='./data/')
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--epochs', default=10, type=int)
    parser.add_argument('--lr', default=0.0001, type=float)
    parser.add_argument('--img_size', type=int, default=256)
    parser.add_argument('--use_pretrained', type=bool, default=False)
    parser.add_argument('--path_model', default='models/hair.h5')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()

    # Augmentation Data
    data_gen_args = dict(rotation_range=0.2,
                         width_shift_range=0.05,
                         height_shift_range=0.05,
                         shear_range=0.05,
                         zoom_range=0.05,
                         horizontal_flip=True,
                         fill_mode='nearest')

    myGene = trainGenerator(args.batch_size, args.data_dir, 'images', 'masks', data_gen_args, save_to_dir=None)

    size_data = len(os.listdir(f"{args.data_dir}/images"))
    steps_per_epoch = size_data // args.batch_size
    args.steps_per_epoch = steps_per_epoch

    print(args)

    if args.use_pretrained:
        # Pretrain model
        model = keras.models.load_model('models/hairnet_matting.hdf5')
    else:
        model = Hairnet.get_model()

    model.compile(optimizer=Adam(lr=args.lr), loss='binary_crossentropy', metrics=['accuracy'])

    model_checkpoint = ModelCheckpoint('models/hairnet_matting.hdf5', monitor='loss', verbose=1, save_best_only=True)
    model.fit_generator(myGene, callbacks=[model_checkpoint], steps_per_epoch= args.steps_per_epoch, epochs=args.epochs)

    model.save(args.path_model)

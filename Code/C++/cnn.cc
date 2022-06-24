#include "cnn.hh"
#include "utils.hh"
#include "activ_fun.hh"
#include "conv.hh"
#include "pool.hh"
#include "flat.hh"
#include "dense.hh"

#ifndef __SYNTHESIS__
# include <cstdio>
#endif

void cnn(float img_in [IMG_ROWS][IMG_COLS], float prediction[DIGITS])
{
  /******** Normalization. ********/
  float norm_img [IMG_ROWS][IMG_COLS] = { 0 };
  normalization(img_in, norm_img);

  #if 0
    #ifndef __SYNTHESIS__
      printf("Normalized image.\n");
      print_img(norm_img);
    #endif
  #endif

  /******** Padding. ********/
  float pad_img [PAD_IMG_ROWS][PAD_IMG_COLS] = { 0 };
  padding(norm_img, pad_img);

  #if 0
    #ifndef __SYNTHESIS__
      printf("Padded image.\n");
      print_pad_img(pad_img);
    #endif
  #endif

  /******** Convolution layer. ********/
  /*
    An array to collect .hhe convolution results:
    FILTERS resulting feature maps, one for ea.hh filter.
  */
  float features [FILTERS][IMG_ROWS][IMG_COLS] = { 0 };
  // Convolution wi.hh relu as activation function.
  convolutional_layer(pad_img, features);

  #if 0
    #ifndef __SYNTHESIS__
      // Print results.
      print_features(features);
    #endif
  #endif

  /******** Maxpooling layer. ********/
  float pool_features [FILTERS][POOL_IMG_ROWS][POOL_IMG_COLS] = { 0 };
  max_pooling_layer(features, pool_features);

  #if 0
    #ifndef __SYNTHESIS__
      print_pool_features(pool_features);
    #endif
  #endif

  /******** Flatten layer. ********/
  float flat_array [FLAT_SIZE] = { 0 };
  flattening_layer(pool_features, flat_array);

  /******** Dense layer ********/
  dense_layer(flat_array, prediction);
}
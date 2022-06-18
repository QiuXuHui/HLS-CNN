#pragma once

#include "definitions.h"

void
normalize (
  const float img_in  [IMG_ROWS][IMG_COLS], // Input image.
  float       img_out [IMG_ROWS][IMG_COLS]  // Normalized image.
);

void
padding(
  const float img_in [IMG_ROWS][IMG_COLS],                       // Input image.
  float       img_out [IMG_ROWS + PAD_ROWS][IMG_COLS + PAD_COLS] // Paded out.
);

// FIME: remove code below before synthesis.

void
print_img(const float img[IMG_ROWS][IMG_COLS]);

void
print_pad_img(const float img[IMG_ROWS + PAD_ROWS][IMG_COLS + PAD_COLS]);

#include "pool.h"

#include <float.h>

void
max_pooling
(
  const float img_in[IMG_ROWS][IMG_COLS],
  float       img_out[POOL_IMG_ROWS][POOL_IMG_COLS]
)
{
  float pool = 0.0;
  float tmp  = 0.0;

  pool_for_rows:
  for(uint8_t i = 0; i < IMG_ROWS; i += POOL_ROWS)
	pool_for_cols:
    for(uint8_t j = 0; j < IMG_COLS; j += POOL_COLS)
    {
      pool = FLT_MIN;

      max_for_rows:
      for (uint8_t pi = 0; pi < POOL_ROWS; ++pi)
    	max_for_cols:
        for (uint8_t pj = 0; pj < POOL_COLS; ++pj)
        {
          tmp = img_in[i + pi][j + pj];
          if (tmp > pool)
            pool = tmp;
        }

      img_out[i / POOL_ROWS][j / POOL_COLS] = pool;
    }
}

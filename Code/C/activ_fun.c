#include "activ_fun.h"

#include <math.h>

#pragma GCC diagnostic ignored "-Wunused-label"

float relu (float x)
{
  if(x > 0.0)
    return x;
  else
    return 0.0;
}

void soft_max(float dense_array [DIGITS], float pred[DIGITS])
{
  float sum = 0.0;

  for_exp_sum:
  for (uint8_t i = 0; i < DIGITS; ++i)
  {
    sum += expf(dense_array[i]);
  }

  for_prediction:
  for (uint8_t j = 0; j < DIGITS; ++j)
  {
    pred[j] = expf(dense_array[j]) / sum;
  }

}

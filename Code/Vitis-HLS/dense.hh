#pragma once

#include "definitions.hh"

#include "hls_stream.h"

void
dense_layer
(
  hls::stream<float> flat_to_dense_streams[FILTERS],
  float              prediction [DIGITS]
);
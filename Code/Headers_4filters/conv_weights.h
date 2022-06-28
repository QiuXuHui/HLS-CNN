/*
 * This file is auto-generated by gen-weights.py
 */

#pragma once

#include "definitions.h"


// Conv layer weights.
float conv_weights [FILTERS][KRN_ROWS][KRN_COLS]
	= {
			{
				{ -0.47080832719802856, 0.32262930274009705, 0.9474257826805115 },
				{ -0.26119935512542725, 0.22615189850330353, 0.7443171739578247 },
				{ 1.1230748891830444, 0.4416429102420807, 0.62715744972229 }
			},
			{
				{ 2.2626705169677734, -0.9155095815658569, -1.2591710090637207 },
				{ 0.7731971740722656, -2.9045703411102295, -0.1797010898590088 },
				{ -1.636474609375, -0.9741566181182861, 1.9884620904922485 }
			},
			{
				{ 0.5701413154602051, 0.9823038578033447, -0.6180001497268677 },
				{ 0.5772498250007629, 2.101029872894287, 1.4775304794311523 },
				{ -3.065988540649414, -2.225825309753418, -0.5587272644042969 }
			},
			{
				{ -1.7043757438659668, 0.32994335889816284, 2.262918472290039 },
				{ -1.5198893547058105, -0.99240642786026, 1.6073665618896484 },
				{ -1.3486419916152954, -0.7100018262863159, 1.694703221321106 }
			}
		};

// Conv layer biases.
float conv_biases [FILTERS] = { -1.4128817319869995, 0.3397355377674103, -0.2530405819416046, -1.3997337818145752 };

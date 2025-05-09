#ifndef BRACCIO_H_
#define BRACCIO_H_

#include "stm32f4xx_hal.h"
#include "stdlib.h"

typedef struct {
	TIM_HandleTypeDef* timBase;
	TIM_HandleTypeDef* timShoulder;
	TIM_HandleTypeDef* timElbow;
	TIM_HandleTypeDef* timWristV;
	TIM_HandleTypeDef* timWristR;
	TIM_HandleTypeDef* timGripper;

} Braccio;

void Braccio_Init(Braccio* arm);
void Braccio_Move(Braccio* arm, int base, int shoulder, int elbow, int wristV, int wristR, int gripper);

#endif

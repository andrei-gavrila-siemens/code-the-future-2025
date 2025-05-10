#ifndef BRACCIO_H_
#define BRACCIO_H_

#define L1 12.5f
#define L2 12.5f
#define L3 5.5f

#include "stm32f4xx_hal.h"
#include "stdlib.h"
#include <math.h>

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
void Braccio_SmoothMove(Braccio* arm);
void Braccio_RotateAndLiftGripperOpen(Braccio* arm, int rot_start, int rot_end, int wristVer_start, int wristVer_end);
void Braccio_RotateAndLiftGripperClosed(Braccio* arm, int rot_start, int rot_end, int wristVer_start, int wristVer_end);
void Braccio_MoveGripperSmooth(Braccio* arm, int base, int shoulder, int elbow, int wristV, int wristR, int gripper_target);


#endif

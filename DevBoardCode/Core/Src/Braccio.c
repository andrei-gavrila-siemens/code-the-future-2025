 #include "Braccio.h"

static void set_pwm_us(TIM_HandleTypeDef* htim, uint32_t channel, uint16_t us) {
    if (us < 500) us = 500;
    if (us > 2500) us = 2500;

    __HAL_TIM_SET_COMPARE(htim, channel, us);
}

void Braccio_Init(Braccio* arm)
{
    HAL_TIM_PWM_Start(arm->timBase	  , TIM_CHANNEL_2);     // PA7
    HAL_TIM_PWM_Start(arm->timShoulder, TIM_CHANNEL_1); 	// PB6
    HAL_TIM_PWM_Start(arm->timElbow	  , TIM_CHANNEL_1);     // PA8
    HAL_TIM_PWM_Start(arm->timWristV  , TIM_CHANNEL_3);     // PB10
    HAL_TIM_PWM_Start(arm->timWristR  , TIM_CHANNEL_1);     // PB4
    HAL_TIM_PWM_Start(arm->timGripper , TIM_CHANNEL_2);     // PB3
}

void Braccio_Move(Braccio* arm, int base, int shoulder, int elbow, int wristV, int wristR, int gripper)
{
    set_pwm_us(arm->timBase		, TIM_CHANNEL_2,     base);
    HAL_Delay(10);
    set_pwm_us(arm->timShoulder , TIM_CHANNEL_1, shoulder);
    HAL_Delay(10);
    set_pwm_us(arm->timElbow	, TIM_CHANNEL_1,    elbow);
    HAL_Delay(10);
    set_pwm_us(arm->timWristV	, TIM_CHANNEL_3,   wristV);
    HAL_Delay(10);
    set_pwm_us(arm->timWristR	, TIM_CHANNEL_1,   wristR);
    HAL_Delay(10);
    set_pwm_us(arm->timGripper	, TIM_CHANNEL_2,  gripper);
    HAL_Delay(10);
}


void Braccio_SmoothMove(Braccio* arm) {
    int baseValue = 1900;
    int shoulderValue = 1500;
    int elbowValue = 1900;
    int wristVerValue = 1400;
    int wristRotValue = 2500;

    int stepDelay = 1;
    int stepSize = 20;

    for (int gripper = 500; gripper <= 2800; gripper += stepSize) {
        Braccio_Move(arm, baseValue, shoulderValue, elbowValue, wristVerValue, gripper, wristRotValue);
        HAL_Delay(stepDelay);
    }

    for (int gripper = 2800; gripper >= 500; gripper -= stepSize) {
        Braccio_Move(arm, baseValue, shoulderValue, elbowValue, wristVerValue, gripper, wristRotValue);
        HAL_Delay(stepDelay);
    }
    for (int gripper = 500; gripper <= 1500; gripper += stepSize) {
        Braccio_Move(arm, baseValue, shoulderValue, elbowValue, wristVerValue, gripper, wristRotValue);
        HAL_Delay(stepDelay);
    }
}

void Braccio_RotateAndLiftGripperOpen(Braccio* arm, int rot_start, int rot_end, int wristVer_start, int wristVer_end) {
    int shoulderValue = 1500;
    int elbowValue = 1500;
    int wristRotValue = 1500;


    int gripperValue = 166;

    int steps = 50;
    int delayMs = 2;

    float baseStep = (float)(rot_end - rot_start) / steps;
    float wristVerStep = (float)(wristVer_end - wristVer_start) / steps;

    for (int i = 0; i <= steps; i++) {
        int currentBase = rot_start + (int)(i * baseStep);
        int currentWristVer = wristVer_start + (int)(i * wristVerStep);
        Braccio_Move(arm, currentBase, shoulderValue, elbowValue, currentWristVer, wristRotValue, gripperValue);
        HAL_Delay(delayMs);
    }
}
void Braccio_RotateAndLiftGripperClosed(Braccio* arm, int rot_start, int rot_end, int wristVer_start, int wristVer_end) {
    int shoulderValue = 1500;
    int elbowValue = 1500;
    int wristRotValue = 1500;


    int gripperValue = 2200;

    int steps = 50;
    int delayMs = 2;

    float baseStep = (float)(rot_end - rot_start) / steps;
    float wristVerStep = (float)(wristVer_end - wristVer_start) / steps;

    for (int i = 0; i <= steps; i++) {
        int currentBase = rot_start + (int)(i * baseStep);
        int currentWristVer = wristVer_start + (int)(i * wristVerStep);
        Braccio_Move(arm, currentBase, shoulderValue, elbowValue, currentWristVer, wristRotValue, gripperValue);
        HAL_Delay(delayMs);
    }
}
void Braccio_MoveGripperSmooth(Braccio* arm, int base, int shoulder, int elbow, int wristV, int wristR, int gripper_target) {
    int steps = 15;
    int delayMs = 1;

    static int gripper_current = 1500;

    float gripperStep = (float)(gripper_target - gripper_current) / steps;

    for (int i = 0; i <= steps; i++) {
        int currentGripper = gripper_current + (int)(i * gripperStep);
        Braccio_Move(arm, base, shoulder, elbow, wristV, wristR, currentGripper);
        HAL_Delay(delayMs);
    }


    gripper_current = gripper_target;
}



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
    set_pwm_us(arm->timShoulder , TIM_CHANNEL_1, shoulder);
    set_pwm_us(arm->timElbow	, TIM_CHANNEL_1,    elbow);
    set_pwm_us(arm->timWristV	, TIM_CHANNEL_3,   wristV);
    set_pwm_us(arm->timWristR	, TIM_CHANNEL_1,   wristR);
    set_pwm_us(arm->timGripper	, TIM_CHANNEL_2,  gripper);
}

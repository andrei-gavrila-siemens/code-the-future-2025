#include "Ultra.h"

extern TIM_HandleTypeDef htim11;

uint16_t Ultrasonic_ReadDistance(void)
{
    uint32_t start, stop, duration;

    // Trigger pulse (10 us)
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);
    HAL_Delay(2);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_SET);
    HAL_Delay(0.01);  // 10 µs
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);

    // Wait for echo to go HIGH
    while (!HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN));

    __HAL_TIM_SET_COUNTER(&htim11, 0);
    HAL_TIM_IC_Start(&htim11, TIM_CHANNEL_1);

    // Wait for echo to go LOW
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN));

    HAL_TIM_IC_Stop(&htim11, TIM_CHANNEL_1);

    duration = HAL_TIM_ReadCapturedValue(&htim11, TIM_CHANNEL_1);

    // Distance in cm = (duration * speed of sound) / 2
    return (uint16_t)((duration * 0.0343f) / 2.0f);
}

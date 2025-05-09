#include "Ultra.h"

extern TIM_HandleTypeDef htim11;

// Constants
#define ULTRASONIC_TIMEOUT_MS    100U         // Timeout for waiting echo (in ms)
#define SPEED_OF_SOUND_CM_PER_US 0.0343f      // Speed of sound in cm/us
#define TRIG_PULSE_DURATION_US   10U          // Trigger pulse duration (10 µs)

uint16_t Ultrasonic_ReadDistance(void)
{
    uint32_t tickStart = 0;
    uint32_t echoDuration = 0;

    // Ensure trigger is LOW before sending pulse
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);
    HAL_Delay(2);

    // Send 10 µs pulse to trigger pin
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_SET);
    HAL_Delay(1);  // Minimal delay to ensure proper pulse (>10 µs)
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);

    // Wait for ECHO pin to go HIGH
    tickStart = HAL_GetTick();
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_RESET)
    {
        if ((HAL_GetTick() - tickStart) > ULTRASONIC_TIMEOUT_MS)
            return 0;  // Timeout: no echo received
    }

    // Start timer to measure echo HIGH duration
    __HAL_TIM_SET_COUNTER(&htim11, 0);
    HAL_TIM_Base_Start(&htim11);

    // Wait for ECHO pin to go LOW
    tickStart = HAL_GetTick();
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_SET)
    {
        if ((HAL_GetTick() - tickStart) > ULTRASONIC_TIMEOUT_MS)
        {
            HAL_TIM_Base_Stop(&htim11);
            return 0;  // Timeout while waiting for echo to end
        }
    }

    // Measure duration and stop timer
    echoDuration = __HAL_TIM_GET_COUNTER(&htim11);
    HAL_TIM_Base_Stop(&htim11);

    // Calculate distance (in cm): duration * speed of sound / 2
    return (uint16_t)((echoDuration * SPEED_OF_SOUND_CM_PER_US) / 2.0f);
}

#ifndef ULTRASONIC_H_
#define ULTRASONIC_H_

#include "stm32f4xx_hal.h"

#define TRIG_PORT    GPIOA
#define TRIG_PIN     GPIO_PIN_9
#define ECHO_PORT    GPIOB
#define ECHO_PIN     GPIO_PIN_9

uint16_t Ultrasonic_ReadDistance(void);

#endif

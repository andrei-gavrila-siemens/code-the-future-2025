#ifndef UART_COMM_H_
#define UART_COMM_H_

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stddef.h>

// Configurează UART-ul cu handler extern (ex. huart2)
void UART_Comm_Init(UART_HandleTypeDef *huart);

// Transmite un buffer de octeți
HAL_StatusTypeDef UART_Comm_Send(uint8_t *data, size_t len);

// Transmite un șir de caractere (null-terminated)
HAL_StatusTypeDef UART_Comm_SendString(const char *str);

// Primește un singur octet (blocking)
HAL_StatusTypeDef UART_Comm_ReceiveByte(uint8_t *byte, uint32_t timeout);

#endif /* UART_COMM_H_ */

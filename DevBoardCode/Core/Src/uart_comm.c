#include "uart_comm.h"
#include <string.h>

static UART_HandleTypeDef *uart_handle = NULL;

void UART_Comm_Init(UART_HandleTypeDef *huart)
{
    uart_handle = huart;
}

HAL_StatusTypeDef UART_Comm_Send(uint8_t *data, size_t len)
{
    if (uart_handle == NULL || data == NULL || len == 0) return HAL_ERROR;
    return HAL_UART_Transmit(uart_handle, data, len, HAL_MAX_DELAY);
}

HAL_StatusTypeDef UART_Comm_SendString(const char *str)
{
    if (uart_handle == NULL || str == NULL) return HAL_ERROR;
    return HAL_UART_Transmit(uart_handle, (uint8_t *)str, strlen(str), HAL_MAX_DELAY);
}

HAL_StatusTypeDef UART_Comm_ReceiveByte(uint8_t *byte, uint32_t timeout)
{
    if (uart_handle == NULL || byte == NULL) return HAL_ERROR;
    return HAL_UART_Receive(uart_handle, byte, 1, timeout);
}

#include "stm32f10x.h" // Device header
#include "Delay.h"
#include "OLED.h"
#include "Motor.h"
#include "Key.h"

uint8_t KeyNum;			 // 定义用于接收按键键码的变量
int8_t Speed, Direction; // 定义速度变量

int main(void)
{
	/*模块初始化*/
	OLED_Init();  // OLED初始化
	Motor_Init(); // 直流电机初始化
	Key_Init();	  // 按键初始化

	/*显示静态字符串*/
	OLED_ShowString(1, 1, "Speed:"); // 1行1列显示字符串Speed:
	OLED_ShowString(2, 1, "Direct"); // 1行1列显示字符串Speed:
	while (1)
	{
		KeyNum = Key_GetNum(); // 获取按键键码
		if (KeyNum == 1)	   // 按键1按下
		{
			Speed += 20;	 // 速度变量自增20
			if (Speed > 100) // 速度变量超过100后
			{
				Speed = -100; // 速度变量变为-100
							  // 此操作会让电机旋转方向突然改变，可能会因供电不足而导致单片机复位
							  // 若出现了此现象，则应避免使用这样的操作
			}
		}

		if (KeyNum == 2) // 按键2按下
		{
			Direction += 50;	 // 速度变量自增50
			if (Direction > 100) // Direction=50是左转，100是右转。
			{
				Direction = -100; // 方向变量变为-100
			}
		}
		if (Direction == -50) // 按键3按下
		{
			Motor_OUT();
		}
		if (Direction == 50) // 按键3按下
		{
			Motor_IN();
		}
		if (Direction == 100) // 按键3按下
		{
			Motor_L();
		}
		if (Direction == -100) // 按键3按下
		{
			Motor_OUT();
		}

		Motor_SetSpeed(Speed);					// 设置直流电机的速度为速度变量
		OLED_ShowSignedNum(1, 7, Speed, 3);		// OLED显示速度变量
		OLED_ShowSignedNum(2, 7, Direction, 3); // OLED显示速度变量
	}
}

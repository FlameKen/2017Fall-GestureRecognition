#include <Servo.h>

#define left 12
#define right 13
#define up 5
#define down 6

#define  servocenterx   70  // center po#define  of x servo
#define  servocentery   70  // center po#define  of y servo
#define  servopinx   9   // digital pin for servo x
#define  servopiny   10  // digital servo for pin y
#define  baudrate 9600  // com port speed. Must match your C++ setting
#define  distancex 1  // x servo rotation steps
#define  distancey 1  // y servo rotation steps

int posx = 0;
int posy = 0;

int turnleft = 0;
int turnright = 0;
int turnup = 0;
int turndown = 0;

Servo servox;
Servo servoy;

void setup() {

  Serial.begin(baudrate);        // connect to the serial port
  Serial.println("Starting Cam-servo Face tracker");

  pinMode(left, INPUT);
  pinMode(right, INPUT);
  pinMode(up, INPUT);
  pinMode(down, INPUT);

  pinMode(servopinx,OUTPUT);    // declare the LED's pin as output
  pinMode(servopiny,OUTPUT);    // declare the LED's pin as output

  servoy.attach(servopiny); 
  servox.attach(servopinx); 

  // center servos

  servox.write(servocenterx); 
  delay(200);
  servoy.write(servocentery); 
  delay(200);
}

void loop () {
  turnleft = digitalRead(left);
  turnright = digitalRead(right);
  turnup = digitalRead(up);
  turndown = digitalRead(down);

  posx = servox.read(); 
  posy = servoy.read();
  if (turnleft) {
    posx += distancex;
    servox.write(posx);
  }
  else if (turnright) {
    posx -= distancex;
    servox.write(posx);
  }
  delay(250);

  if (turnup) {
    posy -= distancey;
    servoy.write(posy); 
  }
  else if (turndown) {
    posy += distancey;
    servoy.write(posy); 
  }
  
  delay(250);
  
}















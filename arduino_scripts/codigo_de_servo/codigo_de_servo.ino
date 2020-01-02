#include <Servo.h>
int grados;
float angle_calib;
Servo __myservo9;
char condition = 'F';
// Paso angular define cada cuantos grados avanzara el servo
int paso_angular = 5;

// Period de envio de angulo al servo
int T = 50;

void setup()
{
  Serial.begin(9600);

  __myservo9.attach(9);
  __myservo9.write(97.5);
  delay(2000);
}
void loop()
{
  if (condition != 'T'){
    delay(1000);
    if (Serial.available() > 0) {
      // read the incoming byte:
      char condition_read = Serial.read();
      //Serial.println(condition_read);
      condition = condition_read;
      /**if(condition == 'T'){
        Serial.println("Si cumple la condicion");
      }**/
    }
    Serial.print("grado ");
    Serial.println(90);
  }

  if (condition == 'T'){
    //Serial.println("Moviendo el servo ...");
    for (grados = 90; grados > 0; grados--) {
      angle_calib = 17.5 + (grados*(97.5-17.5)/90);
      __myservo9.write(angle_calib);
      delay(T);
      if(grados % 5 == 0){
        Serial.print("grado ");
        Serial.println(180-grados);
      }
    }
    for (grados = 0; grados < 90; grados++) {
      angle_calib = 17.5 + (grados*(97.5-17.5)/90);
      __myservo9.write(angle_calib);
      delay(T);
      if(grados % 5 == 0){
        Serial.print("grado ");
        Serial.println(180-grados);
      }
    }
    for (grados = 90; grados < 180; grados++){
      angle_calib = 97.5 + ((grados-90)*(180-97.5)/90);
      __myservo9.write(angle_calib);
      delay(T);
      if(grados % 5 == 0){
        Serial.print("grado ");
        Serial.println(180-grados);
      }
    }
    for (grados = 180; grados >90; grados--){
      angle_calib = 97.5 + ((grados-90)*(180-97.5)/90);
      __myservo9.write(angle_calib);
      delay(T);
      if(grados % 5 == 0){
        Serial.print("grado ");
        Serial.println(180-grados);
      }
    }
  }
}

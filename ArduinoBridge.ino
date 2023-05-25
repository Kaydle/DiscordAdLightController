#include <IRremote.hpp>

int Timedelay = 2000;
int frenzyDelay = 50;

void setup() {
  IrSender.begin(4);
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  // IrSender.sendNEC(0xFE02, 0x02, 1);
    
  while (Serial.available()){
    String number = Serial.readString();
    uint8_t hexString = uint8_t(number.toInt());
    Serial.print(hexString);
    IrSender.sendNEC(0xFE02, hexString, 8);
  }


  //if (data){
  //  converted = uint8_t
  //}  


}

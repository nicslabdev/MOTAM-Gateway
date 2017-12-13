#!/bin/bash
# Bash script for creating GUI dialog for choosing simulations
# Developed for MOTAM Project
# Created by Manuel Montenegro. 06/10/2017

ans=$(zenity  --list  --title "OBDII not found" --text "What do you want to do?" --radiolist --column "Pick" --column "Choice" TRUE "Load a session" FALSE "Run OBDII interface simulator"); 
echo $ans
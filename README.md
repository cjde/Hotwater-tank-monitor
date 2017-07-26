# Hotwater tank monitor

This is a hotwater tank monitoring applicaition. Attached to the A/C unit is a heat recovery unit. This provides hotwater through out the summer months. There is a Pi Zero that has 4 DS18B20 Digital temperature sensor (1 wire bus) that monitor the temperature of the tank at various points. These values are collected every minute and sent (via MQTT) to a PI "B" that is running MRTG ( and associated Web and DB ).  The Pi"B" computes various energy components and the heat map of the tank. This goes into a very crude display ( mainly a PHP learning project ) to server up to 


# Освещение спальни 1й этаж
functions.append( DCL.Trigger_OnOff( 164, 54 ).run )		# Спальня 1 этаж, выключатель на входе 1: 164, Лампа: 54
functions.append( DCL.Trigger_OnOff( 168, 52 ).run )		# Спальня 1 этаж, выключатель на входе 2: 168, Лампа: 52
functions.append( DCL.Trigger_OnOff( 167, 52 ).run )		# Спальня 1 этаж, выключатель по центру:  167, Лампа: 52
functions.append( DCL.LongPress_Off( 167, [52, 54] ).run )	# Спальня 1 этаж, выключатель по центру, длинное нажатие отключает лампы: 52, 54

# Освещение ванной комнаты 1й этаж
functions.append( DCL.Trigger_On_first_Off_all(173, [47, 38]).run )	# Ванная 1 этаж, выключатель в коридоре:    173, Лампа: 47, отключает 47, 38
functions.append( DCL.Trigger_OnOff( 185, 38 ).run )				# Ванная 1 этаж, выключатель в постирочной: 185, Лампа: 38
